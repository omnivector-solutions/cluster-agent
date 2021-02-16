#!/usr/bin/env python3
# Credit: Corydodt
"""
Edit AWS SSM parameters in a text editor and save them
"""
import inspect
import secrets
import string
import sys

from botocore.exceptions import ClientError
from codado import hotedit
import boto3
import click
import toml


PASSWORD_CHARS = string.ascii_letters + string.digits

PARAM_KEYS = (
    "BASE_SCRAPER_URL",
    "X_SLURM_USER_NAME",
    "X_SLURM_USER_TOKEN",
    "BASE_API_URL",
    "API_KEY"
)

PARAM_TEMPLATE = inspect.cleandoc(
    """
    # {stage}
    [ssm]
    BASE_SCRAPER_URL = {BASE_SCRAPER_URL!a}
    X_SLURM_USER_NAME = {X_SLURM_USER_NAME!a}
    X_SLURM_USER_TOKEN = {X_SLURM_USER_TOKEN!a}
    BASE_API_URL = {BASE_API_URL!a}
    API_KEY = {API_KEY!a}
    """
)


def make_token(charset=PASSWORD_CHARS):
    """
    Generate a secure token
    """
    return "".join(secrets.choice(charset) for i in range(20))


def read_upstream(client, stage):
    """
    Get a bunch of SSM Parameters from AWS
    """
    defaults = dict(
        BASE_SCRAPER_URL="http://172.31.80.90:6820",
        X_SLURM_USER_NAME="ubuntu",
        X_SLURM_USER_TOKEN=make_token(),
        BASE_API_URL="https://...",
        API_KEY=""
    )

    prefix = f"/armada-agent/{stage}"
    for k in PARAM_KEYS:
        try:
            val = client.get_parameter(Name=f"{prefix}/{k}")["Parameter"]["Value"]
        except ClientError as e:
            if e.response["Error"]["Code"] == "ParameterNotFound":
                val = defaults.get(k, "")
            else:
                raise

        yield (k, val)


def save_upstream(client, stage, data):
    """
    Put a bunch of param values into AWS
    """
    prefix = f"/armada-agent/{stage}"
    for k, v in data.items():
        client.put_parameter(
            Name=f"{prefix}/{k}",
            Value=v,
            Type="String",
            Overwrite=True,
        )
        yield (k, v)


@click.command()
@click.pass_context
@click.argument("stage", type=str)
def ssmparameters(ctx: click.Context, stage):
    """
    Edit AWS SSM parameters in a text editor and save them
    """
    client = boto3.client("ssm")

    orig = {}
    for (k, v) in read_upstream(client, stage):
        orig.update({k: v})
        click.echo(".", nl=False)

    click.echo("")

    orig_file = PARAM_TEMPLATE.format(**orig, stage=stage)

    while True:
        try:
            new_file = hotedit.hotedit(initial=orig_file, validate_unchanged=True)
        except hotedit.Unchanged:
            click.echo("** Parameters were unchanged", file=sys.stderr)
            if click.confirm("Try again?"):
                continue
            else:
                ctx.exit(1)

        new_data = toml.loads(new_file)
        # sanity check that we've only seen the keys we want to see
        check_keys = sorted(new_data.get("ssm", {}).keys())
        if not check_keys == sorted(PARAM_KEYS):
            click.echo(f"** Error: some unexpected parameters (saw: {check_keys})")
            if click.confirm("Try again?"):
                orig_file = new_file
                continue
            else:
                ctx.exit(1)

        break

    for _ in save_upstream(client, stage, new_data["ssm"]):
        click.echo(".", nl=False)
    click.echo("Saved.")


class Config:

    def __init__(self, stage) -> None:

        ssm = boto3.client("ssm")

        # slurm restd info
        self.base_scraper_url = ssm.get_parameter(Name=f"/armada-agent/{stage}/BASE_SCRAPER_URL")["Parameter"]["Value"]
        self.x_slurm_user_name = ssm.get_parameter(Name=f"/armada-agent/{stage}/X_SLURM_USER_NAME")["Parameter"]["Value"]
        self.x_slurm_user_token = ssm.get_parameter(Name=f"/armada-agent/{stage}/X_SLURM_USER_TOKEN")["Parameter"]["Value"]

        # armada api info
        self.base_api_url = ssm.get_parameter(Name=f"/armada-agent/{stage}/BASE_API_URL")["Parameter"]["Value"]
        self.api_key = ssm.get_parameter(Name=f"/armada-agent/{stage}/API_KEY")["Parameter"]["Value"]