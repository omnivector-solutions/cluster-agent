from cluster_agent.settings import SETTINGS
from cluster_agent.utils.jwt import generate_jwt_token


async def slurmrestd_header():

    x_slurm_user_token = await generate_jwt_token()

    return {
        "X-SLURM-USER-NAME": SETTINGS.X_SLURM_USER_NAME,
        "X-SLURM-USER-TOKEN": x_slurm_user_token,
    }
