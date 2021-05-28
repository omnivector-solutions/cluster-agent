"""Core module for JWT related operations"""
import subprocess

from armada_agent.settings import SETTINGS

def generate_jwt_token() -> str:

    output = subprocess.check_output(
        "scontrol token username={}" \
        .format(SETTINGS.ARMADA_AGENT_X_SLURM_USER_NAME) \
        .split()
    ).decode('utf-8')

    # TODO: Get JWT token from regex
    jwt_token = output.strip().split('=')[1]

    return jwt_token