import inspect
from argparse import ArgumentParser
from typing import MutableMapping

import pytest
from bidict import bidict
from cluster_agent.utils.job_script_parser import (
    _IDENTIFICATION_FLAG,
    _INLINE_COMMENT_MARK,
    ArgumentParserCustomExit,
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
        #SBATCH --no-kill --no-requeue          # Flagged params
        #SBATCH -n 4 -A <account>               # Multiple args per line
        #SBATCH --job-name=serial_job_test      # Job name
        #SBATCH --mail-type=END,FAIL            # Mail events (NONE, BEGIN, END, FAIL, ALL)
        #SBATCH --mail-user=email@somewhere.com # Where to send mail
        #SBATCH --mem=1gb                       # Job memory request
        #SBATCH --time=00:05:00                 # Time limit hrs:min:sec
        #SBATCH --output = serial_test_%j.log   # Standard output and error log
        #SBATCH --wait-all-nodes=0              #
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
        "--no-kill",
        "--no-requeue",
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
        "--wait-all-nodes",
        "0",
    ]
    actual_list = list(_clean_jobscript(dummy_slurm_script))
    assert actual_list == desired_list


@pytest.mark.parametrize("item", sbatch_to_slurm)
class TestSbatchToSlurmList:
    """
    Test all the fields of the objects SbatchToSlurm that are
    stored in the list sbatch_to_slurm.
    """

    def test_slurmrestd_var_name__is_string(self, item):
        """
        Check if the field slurmrestd_var_name is a string.
        """
        assert isinstance(item.slurmrestd_var_name, str)

    def test_slurmrestd_var_name__only_contains_letters(self, item):
        """
        Check if the field slurmrestd_var_name contains only underscores and letters.
        """
        if item.slurmrestd_var_name:
            assert item.slurmrestd_var_name.replace("_", "").isalpha()

    def test_sbatch__is_string(self, item):
        """
        Check if the field sbatch is a string.
        """
        assert isinstance(item.sbatch, str)

    def test_sbatch__starts_with_double_hyphen(self, item):
        """
        Check if the field sbatch starts with a double hyphen.
        """
        assert item.sbatch.startswith("--")

    def test_sbatch__is_not_empty(self, item):
        """
        Check if the field sbatch is not empty by asserting that it has more
        than three characters, since it starts with a double hyphen.
        """
        assert len(item.sbatch) >= 3

    def test_sbatch__only_contains_letters(self, item):
        """
        Check if the field sbatch contains only hyphens and letters.
        """
        assert item.sbatch.replace("-", "").isalpha()

    def test_sbatch_short__is_string(self, item):
        """
        Check if the optional field sbatch_short  is a string.
        """
        assert isinstance(item.sbatch_short, str)

    def test_sbatch_short__starts_with_hyphen(self, item):
        """
        Check if the optional field sbatch_short starts with a hyphen.
        """
        if item.sbatch_short:
            assert item.sbatch_short.startswith("-")

    def test_sbatch_short__is_not_empty(self, item):
        """
        Check if of the optional field sbatch_short is equal to two, since it
        should be a hyphen and a letter.
        """
        if item.sbatch_short:
            assert len(item.sbatch_short) == 2

    def test_sbatch_short__only_contains_letters(self, item):
        """
        Check if the optional field sbatch_short contains only hyphens and letters.
        """
        if item.sbatch_short:
            assert item.sbatch_short.replace("-", "").isalpha()

    def test_argparser_param__is_mutable_mapping(self, item):
        """
        Check if the field argparser_param is a MutableMapping.
        """
        assert isinstance(item.argparser_param, MutableMapping)

    def test_argparser_param__is_valid_for_parser(self, item):
        """
        Check if the field argparser_param can be added in a parser.
        """
        if item.argparser_param:
            args = (i for i in (item.sbatch_short, item.sbatch) if i)
            parser = ArgumentParserCustomExit()
            parser.add_argument(*args, **item.argparser_param)


@pytest.mark.parametrize("field", ["slurmrestd_var_name", "sbatch", "sbatch_short"])
def test_sbatch_to_slurm_list__contains_only_unique_values(field):
    """
    Test that any given field has no duplicated values for all parameters stored
    at sbatch_to_slurm. This aims to avoid ambiguity at the SBATCH argparser and
    the two-way mapping between SBATCH and Slurm Rest API namespaces.
    """
    list_of_values = [
        getattr(i, field) for i in sbatch_to_slurm if bool(getattr(i, field))
    ]

    assert len(list_of_values) == len(set(list_of_values))


class TestArgumentParserCustomExit:
    """
    Test the custom error handling implemented over the built-in argument parser.
    """

    @pytest.fixture(scope="module")
    def parser(self):
        """
        An instance of parser, used to support the tests in this class.
        """
        parser = ArgumentParserCustomExit()
        parser.add_argument("--foo", type=int)
        parser.add_argument("--bar", action="store_true")
        return parser

    def test_argument_parser_success(self, parser):
        """
        Test the base case, where the arguments are successfully parsed and
        converted to the expected type.
        """
        args = parser.parse_args("--foo=10 --bar".split())
        assert {"foo": 10, "bar": True} == vars(args)

    def test_argument_parser_raise_value_error_when_value_is_missing(self, parser):
        """
        Test that ValueError is raised when the value for one parameter is missing.
        """
        with pytest.raises(
            ValueError, match="error: argument --foo: expected one argument"
        ):
            parser.parse_args("--foo".split())

    def test_argument_parser_raise_value_error_in_case_of_wrong_type(self, parser):
        """
        Test that ValueError is raised when the value for some parameter is
        incompatible with its type.
        """
        with pytest.raises(
            ValueError, match="error: argument --foo: invalid int value:"
        ):
            parser.parse_args("--foo some_text".split())


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
        "no_kill": True,
        "requeue": False,
        "account": "<account>",
        "job_name": "serial_job_test",
        "mail_type": "END,FAIL",
        "mail_user": "email@somewhere.com",
        "mem": "1gb",
        "ntasks": 4,
        "output": "serial_test_%j.log",
        "time": "00:05:00",
        "wait_all_nodes": 0,
    }

    actual_dict = jobscript_to_dict(dummy_slurm_script)

    assert actual_dict == desired_dict


def test_jobscript_to_dict__raises_exception_for_unknown_parameter():
    """
    Test if jobscript_to_dict raises a ValueError when facing unknown parameters.
    """
    with pytest.raises(ValueError, match="Unrecognized SBATCH arguments:"):
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
        KeyError, match="Impossible to convert from SBATCH to Slurm REST API:"
    ):
        convert_sbatch_to_slurm_api(dict(foo=0, bar=1))


def test_get_job_parameters(dummy_slurm_script):
    """
    Test if all SBATCH parameters are properly extracted from a given job script,
    the name of each of them is mapped to Slurm Rest API namespace and returned
    in a dictionary. Notice get_job_parameters accepts extra keywords as
    default values that may be overwritten by the values at the job script.
    """
    extra_options = {"name": "name", "current_working_directory": "cwd"}

    desired_dict = extra_options.copy()

    desired_dict.update(
        {
            "no_kill": True,
            "requeue": False,
            "account": "<account>",
            "name": "serial_job_test",
            "mail_type": "END,FAIL",
            "mail_user": "email@somewhere.com",
            "memory_per_node": "1gb",
            "tasks": 4,
            "standard_output": "serial_test_%j.log",
            "time_limit": "00:05:00",
            "wait_all_nodes": 0,
        }
    )

    actual_dict = get_job_parameters(dummy_slurm_script, **extra_options)

    assert desired_dict == actual_dict


class TestBidictMapping:
    """
    Integration test with the requirement bidict (used for two-way mapping).
    """

    @pytest.fixture
    def dummy_mapping(self):
        """
        A dummy dictionary used for testing.
        """
        return {f"key_{i}": f"value_{i}" for i in range(5)}

    def test_bidict__is_mutable_mapping(self):
        """
        Check if bidict implements all the necessary protocols to be a MutableMapping.
        """
        assert issubclass(bidict, MutableMapping)

    def test_bidict__can_be_compared_to_a_dictionary(self, dummy_mapping):
        """
        Check if bidict can be really comparable to a dictionary.
        """
        assert dummy_mapping == bidict(dummy_mapping)

    def test_bidict__can_be_compared_to_a_dictionary_inverse(self, dummy_mapping):
        """
        Check if bidict can be comparable to a dictionary, this time checking
        its inverse capability (i.e., swapping keys and values).
        """
        desired_value = {value: key for key, value in dummy_mapping.items()}

        assert desired_value == bidict(dummy_mapping).inverse


class TestExclusiveParameter:
    """
    --exclusive is a special SBATCH parameter that can be used in some different ways:

    1. --exclusive as a flag, meaning the value 'exclusive' should be recovered for slurmd.
    2. --exclusive=<value>, meaning the value <value> should be recovered for slurmd.
    According to the Slurm documentation, the value can be 'user' or 'mcs'.
    3. On top of that, 'exclusive' is expected to be set to 'oversubscribe' when the
    flag --oversubscribe is used.

    Note: When both are used, the last of them takes precedence.
    """

    def test_empty_jobscript(self):
        """
        Base case: no --exclusive parameter at all.
        """
        jobscript = ""

        desired_dict = {}

        actual_dict = jobscript_to_dict(jobscript)

        assert actual_dict == desired_dict

    def test_exclusive_as_a_flag(self):
        """
        Test the first scenario: --exclusive as a flag.
        """
        jobscript = "#SBATCH --exclusive"

        desired_dict = {"exclusive": "exclusive"}

        actual_dict = jobscript_to_dict(jobscript)

        assert actual_dict == desired_dict

    @pytest.mark.parametrize(
        "exclusive_value", ["user", "mcs", "exclusive", "oversubscribe"]
    )
    def test_exclusive_with_string_value(self, exclusive_value):
        """
        Test the second scenario: --exclusive=<value>.
        """
        jobscript = f"#SBATCH --exclusive={exclusive_value}"

        desired_dict = {"exclusive": exclusive_value}

        actual_dict = jobscript_to_dict(jobscript)

        assert actual_dict == desired_dict

    def test_exclusive_with_incorrect_value(self):
        """
        Test the second scenario with an incorrect value, ValueError should be raised.
        """
        jobscript = "#SBATCH --exclusive=test-test"

        with pytest.raises(ValueError, match="invalid choice: 'test-test'"):
            jobscript_to_dict(jobscript)

    def test_oversubscribe(self):
        """
        Test the third scenario: --oversubscribe as a flag.
        """
        jobscript = "#SBATCH --oversubscribe"

        desired_dict = {"exclusive": "oversubscribe"}

        actual_dict = jobscript_to_dict(jobscript)

        assert actual_dict == desired_dict

    def test_oversubscribe_with_incorrect_value(self):
        """
        Test the second scenario with an incorrect value, ValueError should be raised.
        """
        jobscript = "#SBATCH --oversubscribe=test-test"

        with pytest.raises(
            ValueError, match="Unrecognized SBATCH arguments: test-test"
        ):
            jobscript_to_dict(jobscript)

    def test_both_exclusive_and_oversubscribe_1(self):
        """
        Test that when both are used, the last of them takes precedence.

        In this case, --exclusive is the last one.
        """
        jobscript = "#SBATCH --oversubscribe\n#SBATCH --exclusive"

        desired_dict = {"exclusive": "exclusive"}

        actual_dict = jobscript_to_dict(jobscript)

        assert actual_dict == desired_dict

    def test_both_exclusive_and_oversubscribe_2(self):
        """
        Test that when both are used, the last of them takes precedence.

        In this case, --oversubscribe is the last one.
        """
        jobscript = "#SBATCH --exclusive\n#SBATCH --oversubscribe"

        desired_dict = {"exclusive": "oversubscribe"}

        actual_dict = jobscript_to_dict(jobscript)

        assert actual_dict == desired_dict
