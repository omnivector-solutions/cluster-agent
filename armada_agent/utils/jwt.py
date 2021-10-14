"""Core module for JWT related operations"""
import asyncio

from armada_agent.utils.exception import ProcessExecutionError
from armada_agent.settings import SETTINGS


async def generate_jwt_token():

    # note the username isn't passed in the scontrol command line
    # it's responsability of who is running the code to run it with the specified user
    proc = await asyncio.create_subprocess_shell(
        f"scontrol token",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:

        raise ProcessExecutionError(stderr.decode().strip())

    return stdout.decode().strip().split("=")[1]
