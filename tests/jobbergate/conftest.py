"""
Define fixtures for the ``jobbergate`` section.
"""
from textwrap import dedent

import pytest


@pytest.fixture(scope="module")
def dummy_template_source():
    """
    Provide a fixture that returns a valid job_script_template.
    """
    return dedent(
        """
        #!/bin/python3

        #SBATCH -t 60
        print("I am a very, very dumb job script")
        print(f"foo='{{foo}}'")
        print(f"bar='{{bar}}'")
        print(f"baz='{{baz}}'")
        """
    ).strip()


@pytest.fixture
def dummy_job_script_files(dummy_template_source):
    return {
        "main_file_path": "application.sh",
        "files": {"application.sh": dummy_template_source},
    }


@pytest.fixture
def dummy_pending_job_submission_data(dummy_job_script_files):
    """
    Provide a fixture that returns a dict that is compatible with PendingJobSubmission.
    """
    return dict(
        id=1,
        job_submission_name="sub1",
        job_submission_owner_email="email1@dummy.com",
        job_script_id=11,
        job_script_name="script1",
        job_script_files=dummy_job_script_files,
        application_name="app1",
        slurm_job_id=13,
    )
