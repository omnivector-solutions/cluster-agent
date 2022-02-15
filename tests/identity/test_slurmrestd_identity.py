from datetime import datetime, timezone
from unittest import mock

import jwt
import pytest

from cluster_agent.identity.slurmrestd import (
    _load_token_from_cache,
    _write_token_to_cache,
    acquire_token,
)
from cluster_agent.utils.exception import ProcessExecutionError


def test__write_token_to_cache__caches_a_token(mock_slurmrestd_api_cache_dir):
    """
    Verifies that the auth token can be saved in the cache.
    """
    mock_slurmrestd_api_cache_dir.mkdir(parents=True)
    _write_token_to_cache("dummy-token")
    token_path = mock_slurmrestd_api_cache_dir / "token"
    assert token_path.exists()
    assert token_path.read_text() == "dummy-token"


def test__write_token_to_cache__creates_cache_directory_if_does_not_exist(
    mock_slurmrestd_api_cache_dir,
):  # noqa
    """
    Verifies that the cache directory will be created if it does not already exist.
    """
    assert not mock_slurmrestd_api_cache_dir.exists()
    _write_token_to_cache("dummy-token")
    assert mock_slurmrestd_api_cache_dir.exists()


def test__load_token_from_cache__loads_token_data_from_the_cache(mock_slurmrestd_api_cache_dir):
    """
    Verifies that a token can be retrieved from the cache.
    """
    mock_slurmrestd_api_cache_dir.mkdir(parents=True)
    token_path = mock_slurmrestd_api_cache_dir / "token"
    one_minute_from_now = int(datetime.now(tz=timezone.utc).timestamp()) + 60
    created_token = jwt.encode(
        dict(exp=one_minute_from_now),
        key="dummy-key",
        algorithm="HS256",
    )
    token_path.write_text(created_token)
    retrieved_token = _load_token_from_cache()
    assert retrieved_token == created_token


def test__load_token_from_cache__returns_none_if_cached_token_does_not_exist(
    mock_slurmrestd_api_cache_dir,
):  # noqa
    """
    Verifies that None is returned if the cached token does not exist.
    """
    mock_slurmrestd_api_cache_dir.mkdir(parents=True)
    retrieved_token = _load_token_from_cache()
    assert retrieved_token is None


def test__load_token_from_cache__returns_none_if_cached_token_cannot_be_read(
    mock_slurmrestd_api_cache_dir,
):
    """
    Verifies that None is returned if the token cannot be read.
    """
    mock_slurmrestd_api_cache_dir.mkdir(parents=True)
    token_path = mock_slurmrestd_api_cache_dir / "token"
    token_path.write_text("pre-existing data")
    token_path.chmod(0o000)

    retrieved_token = _load_token_from_cache()

    assert retrieved_token is None


def test__load_token_from_cache__returns_none_if_cached_token_is_expired(
    mock_slurmrestd_api_cache_dir,
):  # noqa
    """
    Verifies that None is returned if the token is expired.
    """
    mock_slurmrestd_api_cache_dir.mkdir(parents=True)
    token_path = mock_slurmrestd_api_cache_dir / "token"
    one_second_ago = int(datetime.now(tz=timezone.utc).timestamp()) - 1
    expired_token = jwt.encode(dict(exp=one_second_ago), key="dummy-key", algorithm="HS256")
    token_path.write_text(expired_token)

    retrieved_token = _load_token_from_cache()

    assert retrieved_token is None


def test__load_token_from_cache__returns_none_cached_token_will_expire_soon(
    mock_slurmrestd_api_cache_dir,
):
    """
    Verifies that None is returned if the token will expired soon.
    """
    mock_slurmrestd_api_cache_dir.mkdir(parents=True)
    token_path = mock_slurmrestd_api_cache_dir / "token"
    nine_seconds_from_now = int(datetime.now(tz=timezone.utc).timestamp()) + 9
    expired_token = jwt.encode(dict(exp=nine_seconds_from_now), key="dummy-key", algorithm="HS256")
    token_path.write_text(expired_token)

    retrieved_token = _load_token_from_cache()

    assert retrieved_token is None


def test_acquire_token__gets_a_token_from_the_cache(mock_slurmrestd_api_cache_dir):
    """
    Verifies that the token is retrieved from the cache if it is found there.
    """
    mock_slurmrestd_api_cache_dir.mkdir(parents=True)
    token_path = mock_slurmrestd_api_cache_dir / "token"
    one_minute_from_now = int(datetime.now(tz=timezone.utc).timestamp()) + 60
    created_token = jwt.encode(
        dict(exp=one_minute_from_now),
        key="dummy-key",
        algorithm="HS256",
    )
    token_path.write_text(created_token)
    retrieved_token = acquire_token()
    assert retrieved_token == created_token


@mock.patch("cluster_agent.identity.slurmrestd.subprocess.Popen")
def test_acquire_token__gets_a_token_from_slurm_if_one_is_not_in_the_cache(
    mock_subprocess_popen, mock_slurmrestd_api_cache_dir
):  # noqa
    """
    Verifies that a token is pulled from Slurm if it is not found in the cache.
    Also checks to make sure the token is cached.
    """
    mock_slurmrestd_api_cache_dir.mkdir(parents=True)
    token_path = mock_slurmrestd_api_cache_dir / "token"
    assert not token_path.exists()

    process_mock = mock.Mock()
    process_mock.communicate.return_value = (
        bytes("SLURM_JWT=dummy-token\n".encode("utf-8")),
        bytes(str().encode("utf-8")),
    )
    process_mock.returncode = 0

    mock_subprocess_popen.return_value = process_mock

    retrieved_token = acquire_token()
    assert retrieved_token == "dummy-token"

    token_path = mock_slurmrestd_api_cache_dir / "token"
    assert token_path.read_text() == retrieved_token


@mock.patch("cluster_agent.identity.slurmrestd.subprocess.Popen")
def test_acquire_token__raise_error_if_subprocess_command_failed(
    mock_subprocess_popen, mock_slurmrestd_api_cache_dir
):  # noqa
    """
    Verifies whether an error is raised or not in case "scontrol token" subprocess call fails.
    """
    mock_slurmrestd_api_cache_dir.mkdir(parents=True)
    token_path = mock_slurmrestd_api_cache_dir / "token"
    assert not token_path.exists()

    process_mock = mock.Mock()
    process_mock.communicate.return_value = (
        bytes(str().encode("utf-8")),
        bytes("This is a dummy error message".encode("utf-8")),
    )
    process_mock.returncode = 1

    mock_subprocess_popen.return_value = process_mock

    with pytest.raises(ProcessExecutionError) as error:
        acquire_token()

    assert "This is a dummy error message" in str(error.value)