"""
Establish an SSM port-forwarding tunnel to an EC2 instance.

• First tries with existing cached SSO credentials
• If that fails, runs `aws sso login --profile …`
• Retries the tunnel once more
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple

import boto3
import botocore
import click

# ─────────────────────────── defaults ──────────────────────────── #
DEFAULT_PROFILE    = "default"
DEFAULT_REGION     = "us-east-1"          # fallback if not in ~/.aws/config
TIMEOUT_SECS       = 5 * 60               # 5 minutes
SSH_PORT           = 22
RDP_PORT           = 3389
LOCAL_SSH_PORT     = 2222
LOCAL_RDP_PORT     = 2389
IAM_ROLE_DOCUMENT = "AWS-StartPortForwardingSession"

# ─────────────────────── helper functions ──────────────────────── #
def resolve_ports(protocol: str | None,
                  remote: int | None,
                  local: int | None) -> Tuple[int, int]:
    """Return (remote_port, local_port) with validation."""
    if remote is not None and protocol is not None:
        raise click.UsageError("--remote-port/-r and --protocol/-p are mutually exclusive.")

    if remote is not None:                     # arbitrary port mode
        if local is None:
            raise click.UsageError("--local-port/-l is required with --remote-port/-r.")
        return remote, local

    # protocol presets
    if protocol == "ssh":
        return SSH_PORT,   local or LOCAL_SSH_PORT
    if protocol == "rdp":
        return RDP_PORT, local or LOCAL_RDP_PORT
    raise click.ClickException(f"unsupported protocol {protocol!r}")


def boto3_session(profile: str) -> boto3.Session:
    """Create a boto3 session *without* triggering an SSO login."""
    return boto3.Session(profile_name=profile)


def start_session_api(
    session: boto3.Session,
    region: str,
    instance_id: str,
    remote: int,
    local: int,
) -> dict:
    """
    Call SSM StartSession (port-forwarding doc) and return the full response.
    """
    ssm = session.client("ssm", region_name=region)
    return ssm.start_session(
        Target=instance_id,
        DocumentName=IAM_ROLE_DOCUMENT,
        Parameters={
            "portNumber":       [str(remote)],
            "localPortNumber":  [str(local)],
        },
    )


def run_plugin(
    start_session_response: dict,
    region: str,
    profile: str,
    instance_id: str,
) -> subprocess.CompletedProcess:
    """
    Spawn the session-manager-plugin to establish the tunnel.  Mirrors what
    `aws ssm start-session` does under the hood.
    """
    plugin_cmd = [
        "session-manager-plugin",
        json.dumps(start_session_response),
        region,
        "StartSession",
        profile,
        json.dumps({"Target": instance_id}),
        f"https://ssm.{region}.amazonaws.com",
    ]
    return subprocess.run(plugin_cmd)


def login_sso(profile: str) -> None:
    """Interactive device-code login via the regular AWS CLI."""
    click.echo("Running `aws sso login` …")
    result = subprocess.run(
        ["aws", "sso", "login", "--profile", profile],
        stdin=subprocess.DEVNULL,
    )
    if result.returncode:
        raise click.ClickException("aws sso login failed.")


# ──────────────────────────── CLI ──────────────────────────────── #
@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("instance_id", required=False, default=None)
@click.option("-l", "--local-port",   type=int, metavar="PORT",
              help="Local port. Required with --remote-port.")
@click.option("-r", "--remote-port",  type=int, metavar="PORT",
              help="Arbitrary remote port (mutually exclusive with --protocol).")
@click.option("-p", "--protocol",     default="ssh", show_default=True,
              type=click.Choice(["ssh", "rdp"], case_sensitive=False),
              help="Preset protocol (ssh → 22/2222, rdp → 3389/2389).")
@click.option("-P", "--profile",      default=DEFAULT_PROFILE, show_default=True,
              help="AWS profile name.")
@click.option("--region",            help="AWS region; autodetected otherwise.")
@click.option("--no-tunnel", is_flag=True,
              help="Skip the first tunnel attempt and just force an SSO login.")
@click.option("--ls", is_flag=True,)
def main(
    instance_id: str,
    local_port: int | None,
    remote_port: int | None,
    protocol: str,
    profile: str,
    region: str | None,
    no_tunnel: bool,
    ls: bool = False,
) -> None:
    if ls:
        list_instances(profile)
        return

    """Open an SSM port-forwarding tunnel (see `.ps1` original for full doc)."""
    remote, local = resolve_ports(protocol, remote_port, local_port)

    # Figure out region from profile config if not explicitly provided
    if region is None:
        region = boto3_session(profile).region_name or DEFAULT_REGION

    click.echo(
        f"Instance : {instance_id}\n"
        f"Remote   : {remote}\n"
        f"Local    : {local}\n"
        f"Profile  : {profile}\n"
        f"Region   : {region}"
    )

    start_time = time.time()
    def timed_out() -> bool:
        return time.time() - start_time > TIMEOUT_SECS

    # One (optional) attempt before SSO login
    if not no_tunnel and instance_id:
        try:
            sess = boto3_session(profile)
            resp = start_session_api(sess, region, instance_id, remote, local)
            click.echo("Tunnel established (cached SSO credentials were still valid).")
            run_plugin(resp, region, profile, instance_id)
            return
        except botocore.exceptions.ClientError as err:
            click.echo(f"First attempt failed: {err.response['Error']['Code']}")
        except Exception as e:
            click.echo(f"First attempt failed: {e!s}")

    if timed_out():
        raise click.ClickException("Timeout hit before login could start.")

    # Refresh SSO credentials
    login_sso(profile)
    if timed_out():
        raise click.ClickException("Timeout hit before second attempt.")

    # Retry with fresh token
    if instance_id:
        try:
            sess = boto3_session(profile)      # picks up new cached token
            resp = start_session_api(sess, region, instance_id, remote, local)
            click.echo("Tunnel established after SSO login.")
            run_plugin(resp, region, profile, instance_id)
        except click.ClickException as exc:
            click.echo(f"Error: {exc.message}", err=True)
            sys.exit(1)



def list_instances(profile: str | None = None) -> None:
    """
    List all EC2 instances in the configured AWS profile. Only display instances
    with "Cluster" tag, in columns: Cluster │ Name │ Instance ID, with row
    separators between each cluster group.
    """
    boto3_profile = profile or DEFAULT_PROFILE
    session = boto3.Session(profile_name=boto3_profile)
    ec2 = session.client("ec2")
    paginator = ec2.get_paginator("describe_instances")

    # collect only tagged instances
    instances: list[dict] = []
    for page in paginator.paginate():
        for r in page["Reservations"]:
            for inst in r["Instances"]:
                tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
                if "Cluster" in tags:
                    instances.append({
                        "Cluster":    tags["Cluster"],
                        "Name":       tags.get("Name", "N/A"),
                        "InstanceId": inst["InstanceId"],
                    })

    if not instances:
        click.echo("No instances found with 'Cluster' tag.")
        return

    # group by cluster
    from collections import defaultdict
    clusters: dict[str, list[dict]] = defaultdict(list)
    for inst in instances:
        clusters[inst["Cluster"]].append(inst)

    # compute column widths
    hdrs = ["Cluster", "Name", "Instance ID"]
    # max length of each field across all rows
    w_cluster = max(len(hdrs[0]), *(len(c) for c in clusters))
    w_name    = max(len(hdrs[1]), *(len(i["Name"]) for grp in clusters.values() for i in grp))
    w_id      = max(len(hdrs[2]), *(len(i["InstanceId"]) for grp in clusters.values() for i in grp))

    # header and separator
    header = f"{hdrs[0]:<{w_cluster}} │ {hdrs[1]:<{w_name}} │ {hdrs[2]:<{w_id}}"
    sep_line = "─" * len(header)

    click.echo(header)
    click.echo(sep_line)

    # print each cluster block
    for cluster_name in sorted(clusters):
        for inst in clusters[cluster_name]:
            click.echo(
                f"{cluster_name:<{w_cluster}} │ "
                f"{inst['Name']:<{w_name}} │ "
                f"{inst['InstanceId']:<{w_id}}"
            )
        # separator between clusters
        click.echo(sep_line)
