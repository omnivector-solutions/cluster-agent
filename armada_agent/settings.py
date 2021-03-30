from pydantic import BaseSettings


class Settings(BaseSettings):
    # slurmrestd info
    base_scraper_url: str
    x_slurm_user_name: str
    x_slurm_user_token: str

    # armada api info
    base_api_url: str
    api_key: str

    # scraper info
    stage: str = "prod"


    class Config:

        env_file = ".env"
