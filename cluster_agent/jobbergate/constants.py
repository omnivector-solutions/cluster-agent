from collections import defaultdict
from enum import Enum
from typing import DefaultDict


class JobSubmissionStatus(str, Enum):
    """
    Enumeration of possible job_submission statuses.
    """

    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


status_map: DefaultDict[str, JobSubmissionStatus] = defaultdict(
    lambda: JobSubmissionStatus.SUBMITTED,
    COMPLETED=JobSubmissionStatus.COMPLETED,
    FAILED=JobSubmissionStatus.FAILED,
)
