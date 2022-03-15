import json

import pytest
import snick


@pytest.fixture(scope="module")
def dummy_template_source():
    return snick.dedent(
        """
        #!/bin/python3

        #SBATCH -J dummy_job
        #SBATCH -t 60
        print("I am a very, very dumb job script")
        print(f"foo='{{foo}}'")
        print(f"bar='{{bar}}'")
        print(f"baz='{{baz}}'")
        """
    )


@pytest.fixture
def dummy_job_script_data(dummy_template_source):
    return dict(
        id=1,
        job_script_name="script1",
        job_script_data_as_string=json.dumps({"application.sh": dummy_template_source}),
        job_script_owner_email="tucker@omnivector.solutions",
        application_id=11,
    )


@pytest.fixture
def dummy_job_submission_data(dummy_job_script_data):
    return dict(
        id=1,
        job_submission_name="sub1",
        job_script_id=dummy_job_script_data["id"],
        slurm_job_id=13,
    )
