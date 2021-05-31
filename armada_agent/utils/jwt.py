"""Core module for JWT related operations"""
import asyncio

from armada_agent.settings import SETTINGS

async def generate_jwt_token(test: bool = True):

    proc = await asyncio.create_subprocess_shell(
        "scontrol token username={}" \
        .format(SETTINGS.ARMADA_AGENT_X_SLURM_USER_NAME) if not test else
        "juju run --unit slurmctld/3 scontrol token",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    return stdout.decode().strip().split('=')[1] if stdout else ""