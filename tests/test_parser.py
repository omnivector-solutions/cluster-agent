import inspect

import pytest
from cluster_agent.utils.parser import (
    _IDENTIFICATION_FLAG,
    _INLINE_COMMENT_MARK,
    _clean_jobscript,
    _clean_line,
    _flagged_line,
)


def test_identification_flag():
    assert _IDENTIFICATION_FLAG == "#SBATCH"


def test_inline_comment_mark():
    assert _INLINE_COMMENT_MARK == "#"


@pytest.mark.parametrize(
    "line, desired_value",
    (
        ("#SBATCH -abc", True),
        ("#SBATCH#SBATCH -abc", True),  # TODO: Discuss this with the team
        ("##SBATCH -abc", False),
        ("run python application", False),
        ("# A comment", False),
    ),
)
def test_flagged_line(line, desired_value):
    actual_value = _flagged_line(line)
    assert actual_value == desired_value


@pytest.mark.parametrize(
    "line, desired_value",
    (
        ("#SBATCH", ""),
        ("#SBATCH -abc # A comment", "-abc"),
    ),
)
def test_clean_line(line, desired_value):
    actual_value = _clean_line(line)
    assert actual_value == desired_value


@pytest.fixture
def dummy_slurm_script():
    return inspect.cleandoc(
        """
        #!/bin/bash
        #SBATCH --verbose
        #SBATCH -abc
        #SBATCH -n 4 -A <account>
        #SBATCH --job-name=serial_job_test      # Job name
        #SBATCH --mail-type=END,FAIL            # Mail events (NONE, BEGIN, END, FAIL, ALL)
        #SBATCH --mail-user=email@somewhere.com # Where to send mail
        #SBATCH --ntasks=1                      # Run on a single CPU
        #SBATCH --mem=1gb                       # Job memory request
        #SBATCH --time=00:05:00                 # Time limit hrs:min:sec
        #SBATCH --output=serial_test_%j.log     # Standard output and error log
        pwd; hostname; date

        module load python

        echo "Running plot script on a single CPU core"

        python /data/training/SLURM/plot_template.py

        date
        """
    )


def test_clean_jobscript(dummy_slurm_script):
    expected_result = {
        "--verbose",
        "-abc",
        "-n 4 -A <account>",
        "--job-name=serial_job_test",
        "--mail-type=END,FAIL",
        "--mail-user=email@somewhere.com",
        "--ntasks=1",
        "--mem=1gb",
        "--time=00:05:00",
        "--output=serial_test_%j.log",
    }
    computed_result = set(_clean_jobscript(dummy_slurm_script))
    assert computed_result == expected_result
