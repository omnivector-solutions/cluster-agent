import pydantic


class ApplicationResponse(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    """
    Describes the format of data for applications retrieved from the Jobbergate API endpoints.
    """

    application_name: str


class JobScriptResponse(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    """
    Describes the format of data for job_scripts retrieved from the Jobbergate API endpoints.
    """

    id: int
    application_id: int
    job_script_name: str
    job_script_data_as_string: str


class JobSubmissionResponse(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    """
    Describes the format of data for job_submissions retrieved from the Jobbergate API endpoints.
    """

    id: int
    job_script_id: int
    slurm_job_id: int
