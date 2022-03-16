import pydantic


class PendingJobSubmission(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    """
    Specialized model for the cluster-agent to pull a pending job_submission along with
    data from its job_script and application sources.
    """

    id: int
    job_submission_name: str
    job_script_name: str
    job_script_data_as_string: str
    application_name: str


class ActiveJobSubmission(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    """
    Specialized model for the cluster-agent to pull an active job_submission.
    """

    id: int
    slurm_job_id: int
