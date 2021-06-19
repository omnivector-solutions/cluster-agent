"""Core module for JWT related operations"""
import asyncio

from armada_agent.utils.exception import ProcessExecutionError
from armada_agent.settings import SETTINGS


async def generate_jwt_token(test: bool = True):

    proc = await asyncio.create_subprocess_shell(
        "scontrol token".format(SETTINGS.X_SLURM_USER_NAME)
        if not test
        else "juju run --unit slurmctld/3 scontrol token",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:

        raise ProcessExecutionError(
            "Armada Agent could not retrieve slurmrestd token for username `{}`".format(
                SETTINGS.X_SLURM_USER_NAME
            )
        )

    return stdout.decode().strip().split("=")[1]
