from pathlib import Path
from typing import Any, Dict, List, Optional

import pydantic


class JobScriptFiles(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    """
    Model containing job-script files.
    """

    main_file_path: Path
    files: Dict[Path, str]


class PendingJobSubmission(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    """
    Specialized model for the cluster-agent to pull a pending job_submission along with
    data from its job_script and application sources.
    """

    id: int
    job_submission_name: str
    job_submission_owner_email: str
    execution_directory: Optional[Path]
    execution_parameters: Dict[str, Any] = pydantic.Field(default_factory=dict)
    job_script_name: str
    application_name: str
    job_script_files: JobScriptFiles


class ActiveJobSubmission(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    """
    Specialized model for the cluster-agent to pull an active job_submission.
    """

    id: int
    slurm_job_id: int


class SlurmJobParams(pydantic.BaseModel):
    """
    Specialized model for describing job submission parameters for Slurm REST API.
    """

    name: str
    get_user_environment: int = 1
    standard_error: Optional[Path]
    standard_output: Optional[Path]
    current_working_directory: Optional[Path]

    class Config:
        extra = "allow"


class SlurmJobSubmission(pydantic.BaseModel):
    """
    Specialized model for describing a request to submit a job to Slurm REST API.
    """

    script: str
    job: SlurmJobParams


class SlurmSubmitError(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    """
    Specialized model for error content in a SlurmSubmitResponse.
    """

    error: Optional[str]
    errno: Optional[int]


class SlurmSubmitResponse(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    """
    Specialized model for the cluster-agent to pull a pending job_submission along with
    data from its job_script and application sources.
    """

    errors: List[SlurmSubmitError] = []
    job_id: Optional[int]
