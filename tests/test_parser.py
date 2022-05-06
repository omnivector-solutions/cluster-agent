import inspect

import pytest
from bidict import bidict
from cluster_agent.utils.parser import (
    parser,
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
        ("#SBATCH#SBATCH", ""),
        ("#SBATCH -abc # A comment", "-abc"),
        ("#SBATCH --abc=0 # A comment", "--abc=0"),
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
        #SBATCH -n 4 -A <account>
        #SBATCH --job-name=serial_job_test      # Job name
        #SBATCH --mail-type=END,FAIL            # Mail events (NONE, BEGIN, END, FAIL, ALL)
        #SBATCH --mail-user=email@somewhere.com # Where to send mail
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
    desired_list = [
        "--verbose",
        "-n",
        "4",
        "-A",
        "<account>",
        "--job-name",
        "serial_job_test",
        "--mail-type",
        "END,FAIL",
        "--mail-user",
        "email@somewhere.com",
        "--mem",
        "1gb",
        "--time",
        "00:05:00",
        "--output",
        "serial_test_%j.log",
    ]
    actual_list = list(_clean_jobscript(dummy_slurm_script))
    assert actual_list == desired_list


def test_parser(dummy_slurm_script):

    desired_dict = {
        "account": "<account>",
        "job_name": "serial_job_test",
        "mail_type": "END,FAIL",
        "mail_user": "email@somewhere.com",
        "mem": "1gb",
        "ntasks": "4",
        "output": "serial_test_%j.log",
        "time": "00:05:00",
        "verbose": True,
    }

    values = parser.parse_args(_clean_jobscript(dummy_slurm_script))
    actual_dict = {
        key: value for key, value in vars(values).items() if value if not None
    }

    assert actual_dict == desired_dict


@pytest.fixture
def dummy_mapping():
    return {f"key_{i}": f"value_{i}" for i in range(5)}


def test_bidict_mapping(dummy_mapping):
    """
    Integration test with the requirement bidict
    """
    assert dummy_mapping == bidict(dummy_mapping)


def test_bidict_mapping_reversed(dummy_mapping):
    """
    Integration test with the requirement bidict,
    this time checking its inverse capability
    """
    desired_value = {value: key for key, value in dummy_mapping.items()}

    assert desired_value == bidict(dummy_mapping).inverse
