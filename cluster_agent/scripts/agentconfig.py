#!/usr/bin/env python3
# Credit: Corydodt
# Modified by: Matheus Tosta
"""
Edit .env parameters in a text editor and save them
"""
import inspect
import string
import sys

from dotenv import dotenv_values
from codado import hotedit
import dotenv
import click
import toml


PASSWORD_CHARS = string.ascii_letters + string.digits

PARAM_KEYS = (
    "CLUSTER_AGENT_BASE_SLURMRESTD_URL",
    "CLUSTER_AGENT_X_SLURM_USER_NAME",
    "CLUSTER_AGENT_BASE_API_URL",
    "CLUSTER_AGENT_SENTRY_DSN",
    "CLUSTER_AGENT_OIDC_DOMAIN",
    "CLUSTER_AGENT_OIDC_AUDIENCE",
    "CLUSTER_AGENT_OIDC_CLIENT_ID",
    "CLUSTER_AGENT_OIDC_CLIENT_SECRET",
)

PARAM_TEMPLATE = inspect.cleandoc(
    """
    CLUSTER_AGENT_BASE_SLURMRESTD_URL = {CLUSTER_AGENT_BASE_SLURMRESTD_URL!a}
    CLUSTER_AGENT_X_SLURM_USER_NAME = {CLUSTER_AGENT_X_SLURM_USER_NAME!a}
    CLUSTER_AGENT_BASE_API_URL = {CLUSTER_AGENT_BASE_API_URL!a}
    CLUSTER_AGENT_SENTRY_DSN = {CLUSTER_AGENT_SENTRY_DSN!a}
    CLUSTER_AGENT_OIDC_DOMAIN = {CLUSTER_AGENT_OIDC_DOMAIN!a}
    CLUSTER_AGENT_OIDC_AUDIENCE = {CLUSTER_AGENT_OIDC_AUDIENCE!a}
    CLUSTER_AGENT_OIDC_CLIENT_ID = {CLUSTER_AGENT_OIDC_CLIENT_ID!a}
    CLUSTER_AGENT_OIDC_CLIENT_SECRET = {CLUSTER_AGENT_OIDC_CLIENT_SECRET!a}
    """
)

CONFIG = dict(dotenv_values(".env"))


def read_upstream():
    """
    Get a bunch of SSM Parameters from AWS
    """
    defaults = dict(
        CLUSTER_AGENT_BASE_SLURMRESTD_URL="http://172.31.80.90:6820",
        CLUSTER_AGENT_X_SLURM_USER_NAME="ubuntu",
        CLUSTER_AGENT_BASE_API_URL="https://...",
        CLUSTER_AGENT_SENTRY_DSN="https://...",
        CLUSTER_AGENT_OIDC_DOMAIN="https://auth-domain.com",
        CLUSTER_AGENT_OIDC_AUDIENCE="https://apis.omnivector.solutions",
        CLUSTER_AGENT_OIDC_CLIENT_ID="abcde12345",
        CLUSTER_AGENT_OIDC_CLIENT_SECRET="abcde12345",
    )

    for k in PARAM_KEYS:

        if k not in CONFIG:
            val = defaults.get(k, "")
        else:
            val = CONFIG[k]

        yield (k, val)


def save_upstream(data):
    """
    Put a bunch of param values into .env file
    """

    for k, v in data.items():
        dotenv.set_key(".env", k, v)
        yield (k, v)


@click.command()
@click.pass_context
def parameters(ctx: click.Context):
    """
    Edit .env parameters in a text editor and save them
    """

    orig = {}
    for (k, v) in read_upstream():
        orig.update({k: v})
        click.echo(".", nl=False)

    click.echo("")

    orig_file = PARAM_TEMPLATE.format(**orig)

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
        check_keys = sorted(new_data.keys())
        if not check_keys == sorted(PARAM_KEYS):
            click.echo(f"** Error: some unexpected parameters (saw: {check_keys})")
            if click.confirm("Try again?"):
                orig_file = new_file
                continue
            else:
                raise ValueError(
                    "Please install the application again and provide only expected keys"
                )

        break

    for _ in save_upstream(new_data):
        click.echo(".", nl=False)
    click.echo("Saved.")
