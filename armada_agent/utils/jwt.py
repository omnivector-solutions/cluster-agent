"""Core module for JWT related operations"""
import asyncio

from armada_agent.utils.exception import ProcessExecutionError
from armada_agent.settings import SETTINGS


async def generate_jwt_token():

    proc = await asyncio.create_subprocess_shell(
        f"scontrol token username={SETTINGS.X_SLURM_USER_NAME}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:

        raise ProcessExecutionError(stderr.decode().strip())

    return stdout.decode().strip().split("=")[1]
