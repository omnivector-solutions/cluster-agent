import inspect
from argparse import ArgumentParser
from typing import MutableMapping

import pytest
from bidict import bidict
from cluster_agent.utils.parser import (
    _IDENTIFICATION_FLAG,
    _INLINE_COMMENT_MARK,
    _clean_jobscript,
    _clean_line,
    _flagged_line,
    _split_line,
    build_mapping_sbatch_to_slurm,
    build_parser,
    convert_sbatch_to_slurm_api,
    get_job_parameters,
    jobscript_to_dict,
    sbatch_to_slurm,
)


def test_identification_flag():
    """
    Check if the value of the identification flag is the same codded in the tests.
    """
    assert _IDENTIFICATION_FLAG == "#SBATCH"


def test_inline_comment_mark():
    """
    Check if the inline comment mark is the same codded in the tests.
    """
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
    """
    Check if the flagged lines are identified properly.
    """
    actual_value = _flagged_line(line)
    assert actual_value == desired_value


@pytest.mark.parametrize(
    "line, desired_value",
    (
        ("#SBATCH", ""),
        ("#SBATCH#SBATCH", ""),
        ("#SBATCH -abc # A comment", "-abc"),
        ("#SBATCH --abc=0 # A comment", "--abc=0"),
        ("#SBATCH --abc 0 # A comment", "--abc 0"),
        ("#SBATCH -a 0 # A comment", "-a 0"),
        ("#SBATCH -a=0 # A comment", "-a=0"),
        ("#SBATCH -a = 0 # A comment", "-a = 0"),
        ("#SBATCH -a=C&Aaccount # A comment", "-a=C&Aaccount"),
    ),
)
def test_clean_line(line, desired_value):
    """
    Check if the provided lines are cleaned properly, i.e.,
    identification flag, inline comments, and comment mark are all removed.
    """
    actual_value = _clean_line(line)
    assert actual_value == desired_value


@pytest.mark.parametrize(
    "line, desired_value",
    (
        ("--help", ["--help"]),
        ("--abc=0", ["--abc", "0"]),
        ("--abc = 0", ["--abc", "0"]),
        ("-J job_name", ["-J", "job_name"]),
        ("-v -J job_name", ["-v", "-J", "job_name"]),
        ("-J job_name -v", ["-J", "job_name", "-v"]),
        ("-a=0", ["-a", "0"]),
        ("-a = 0", ["-a", "0"]),
        ("-a 0", ["-a", "0"]),
    ),
)
def test_split_line(line, desired_value):
    """
    Check if the provided lines are splitted properly at white spaces and equal
    character. This procedure is important because it is the way argparse
    expects to receive the parameters.
    """
    actual_value = _split_line(line)
    assert actual_value == desired_value


@pytest.fixture
def dummy_slurm_script():
    """
    Provide a dummy job script for testing.
    """
    # TODO: DRY, integrate this one with conftest/dummy_template_source
    return inspect.cleandoc(
        """
        #!/bin/bash
        #SBATCH                                 # Empty line
        #SBATCH -n 4 -A <account>               # Multiple args per line
        #SBATCH --job-name=serial_job_test      # Job name
        #SBATCH --mail-type=END,FAIL            # Mail events (NONE, BEGIN, END, FAIL, ALL)
        #SBATCH --mail-user=email@somewhere.com # Where to send mail
        #SBATCH --mem=1gb                       # Job memory request
        #SBATCH --time=00:05:00                 # Time limit hrs:min:sec
        #SBATCH --output = serial_test_%j.log   # Standard output and error log
        pwd; hostname; date

        module load python

        echo "Running plot script on a single CPU core"

        python /data/training/SLURM/plot_template.py

        date
        """
    )


def test_clean_jobscript(dummy_slurm_script):
    """
    Check if all sbatch parameters are correctly extracted from a job script.
    This operation combines many of the functions tested above (filter,
    clean, and slit the parameters on each line).
    """
    desired_list = [
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


@pytest.mark.parametrize("item", sbatch_to_slurm)
def test_sbatch_to_slurm_list__slurmrestd_var_name(item):
    """
    Check if the field slurmrestd_var_name for each item at sbatch_to_slurm
    is appropriated.
    """
    assert isinstance(item.slurmrestd_var_name, str)
    if item.slurmrestd_var_name:
        assert item.slurmrestd_var_name.replace("_", "").isalpha()


@pytest.mark.parametrize("item", sbatch_to_slurm)
def test_sbatch_to_slurm_list__sbatch(item):
    """
    Check if the field sbatch for each item at sbatch_to_slurm is appropriated.
    """
    assert isinstance(item.sbatch, str)
    assert item.sbatch.startswith("--")
    assert len(item.sbatch) >= 3
    assert item.sbatch.replace("-", "").isalpha()


@pytest.mark.parametrize("item", sbatch_to_slurm)
def test_sbatch_to_slurm_list__sbatch_short(item):
    """
    Check if the field sbatch_short for each item at sbatch_to_slurm is appropriated.
    """
    assert isinstance(item.sbatch_short, str)
    if item.sbatch_short:
        assert item.sbatch_short.startswith("-")
        assert len(item.sbatch_short) == 2
        assert item.sbatch_short.replace("-", "").isalpha()


@pytest.mark.parametrize("item", sbatch_to_slurm)
def test_sbatch_to_slurm_list__argparser_param(item):
    """
    Check if the field argparser_param for each item at sbatch_to_slurm
    is appropriated by adding it to a new parser.
    """
    assert isinstance(item.argparser_param, MutableMapping)
    if item.argparser_param:
        args = (i for i in (item.sbatch_short, item.sbatch) if i)
        parser = ArgumentParser()
        parser.add_argument(*args, **item.argparser_param)


@pytest.mark.parametrize("field", ["slurmrestd_var_name", "sbatch", "sbatch_short"])
def test_sbatch_to_slurm_list__only_unique_values(field):
    """
    Test that any given field has no duplicated values for all parameters stored
    at sbatch_to_slurm. This aims to avoid ambiguity at the SBATCH argparser and
    the two-way mapping between SBATCH and Slurm Rest API namespaces.
    """
    list_of_values = [
        getattr(i, field) for i in sbatch_to_slurm if bool(getattr(i, field))
    ]

    assert len(list_of_values) == len(set(list_of_values))


def test_build_parser():
    """
    Test if build_parser runs with no problem and returns the correct type.
    """
    parser = build_parser()
    assert isinstance(parser, ArgumentParser)


def test_build_mapping_sbatch_to_slurm():
    """
    Test if build_mapping_sbatch_to_slurm runs with no problem and
    returns the correct type.
    """
    mapping = build_mapping_sbatch_to_slurm()
    assert isinstance(mapping, bidict)


def test_jobscript_to_dict__success(dummy_slurm_script):
    """
    Test if the SBATCH parameters are properly extracted from a job script
    and returned in a dictionary mapping parameters to their value.
    """

    desired_dict = {
        "account": "<account>",
        "job_name": "serial_job_test",
        "mail_type": "END,FAIL",
        "mail_user": "email@somewhere.com",
        "mem": "1gb",
        "ntasks": "4",
        "output": "serial_test_%j.log",
        "time": "00:05:00",
    }

    actual_dict = jobscript_to_dict(dummy_slurm_script)

    assert actual_dict == desired_dict


def test_jobscript_to_dict__raises_exception_for_unknown_parameter():
    """
    Test if jobscript_to_dict raises a ValueError when facing unknown parameters.
    """
    with pytest.raises(
        ValueError, match="Unrecognized SBATCH arguments: --foo --bar 0"
    ):
        jobscript_to_dict("#SBATCH --foo\n#SBATCH --bar=0")


@pytest.mark.parametrize(
    "item", filter(lambda i: i.slurmrestd_var_name, sbatch_to_slurm)
)
def test_convert_sbatch_to_slurm_api__success(item):
    """
    Test if the keys in a dictionary are properly renamed from SBATCH to Slurm
    Rest API namespace. Notice the values should not be affected.
    """
    desired_dict = {item.slurmrestd_var_name: None}

    sbatch_name = item.sbatch.lstrip("-").replace("-", "_")
    actual_dict = convert_sbatch_to_slurm_api({sbatch_name: None})

    assert actual_dict == desired_dict


def test_convert_sbatch_to_slurm_api__raises_exception_for_unknown_parameter():
    """
    Test if the conversion of dictionary keys from SBATCH to Slurm Rest API
    namespace raises KeyError when facing unknown names.
    """
    with pytest.raises(
        KeyError, match="Impossible to convert from SBATCH to Slurm REST API: foo, bar"
    ):
        convert_sbatch_to_slurm_api(dict(foo=0, bar=1))


def test_get_job_parameters(dummy_slurm_script):
    """
    Test if all SBATCH parameters are properly extrated from a given job script,
    the name of each of them is mapper to Slurm Rest API namespace and returned
    in a dictionary. Notice get_job_parameters accepts extra keywords as
    default values that may be overwritten by the values at the job script.
    """
    extra_options = {"name": "name", "current_working_directory": "cwd"}

    desired_dict = extra_options.copy()

    desired_dict.update(
        {
            "account": "<account>",
            "name": "serial_job_test",
            "mail_type": "END,FAIL",
            "mail_user": "email@somewhere.com",
            "memory_per_node": "1gb",
            "tasks": "4",
            "standard_output": "serial_test_%j.log",
            "time_limit": "00:05:00",
        }
    )

    actual_dict = get_job_parameters(dummy_slurm_script, **extra_options)

    assert desired_dict == actual_dict


@pytest.fixture
def dummy_mapping():
    """
    A dummy dictionary used to test the integration with the requirement bidict.
    """
    return {f"key_{i}": f"value_{i}" for i in range(5)}


@pytest.mark.asyncio
def test_bidict_mapping(dummy_mapping):
    """
    Integration test with the requirement bidict.
    Check if it really behaves as a dictionary.
    """
    assert issubclass(bidict, MutableMapping)
    assert dummy_mapping == bidict(dummy_mapping)


def test_bidict_mapping_reversed(dummy_mapping):
    """
    Integration test with the requirement bidict, this time checking
    its inverse capability (i.e., swaping keys and values).
    """
    desired_value = {value: key for key, value in dummy_mapping.items()}

    assert desired_value == bidict(dummy_mapping).inverse
