"""Core module for Jobbergate API identity management"""

import subprocess
import typing

import httpx
import jwt

from cluster_agent.settings import SETTINGS
from cluster_agent.utils.exception import ProcessExecutionError
from cluster_agent.utils.logging import logger

CACHE_DIR = SETTINGS.CACHE_DIR / "slurmrestd"


def _load_token_from_cache(username: str) -> typing.Union[str, None]:
    """
    Looks for and returns a token from a cache file (if it exists).
    Returns None if::
    * The token does not exist
    * Can't read the token
    * The token is expired (or will expire within 10 seconds)
    """
    token_path = CACHE_DIR / f"{username}.token"
    logger.debug(f"Attempting to retrieve token from: {token_path}")
    if not token_path.exists():
        logger.debug("Cached token does not exist")
        return None

    try:
        token = token_path.read_text().strip()
        logger.debug(f"Retrieved token from {token_path} as {token}")
    except Exception:
        logger.warning(
            f"Couldn't load token from cache file {token_path}. Will acquire a new one"
        )
        return None

    try:
        jwt.decode(
            token, options=dict(verify_signature=False, verify_exp=True), leeway=-10
        )
    except jwt.ExpiredSignatureError:
        logger.warning("Cached token is expired. Will acquire a new one.")
        return None

    return token


def _write_token_to_cache(token: str, username: str):
    """
    Writes the token to the cache.
    """
    if not CACHE_DIR.exists():
        logger.debug("Attempting to create missing cache directory")
        try:
            CACHE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        except Exception:
            logger.warning(
                f"Couldn't create missing cache directory {CACHE_DIR}. Token will not be saved."
            )  # noqa
            return

    token_path = CACHE_DIR / f"{username}.token"
    try:
        token_path.write_text(token)
    except Exception:
        logger.warning(f"Couldn't save token to {token_path}")


def acquire_token(username: str) -> str:
    """
    Retrieves a token from Slurmrestd based on the app settings.
    """
    logger.debug("Attempting to use cached token")
    token = _load_token_from_cache(username)

    if token is None:
        logger.debug("Attempting to acquire token from Slurmrestd")
        proc = subprocess.Popen(
            f"scontrol token username={username}".split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate()
        ProcessExecutionError.require_condition(
            proc.returncode == 0, stderr.decode().strip()
        )
        token = stdout.decode().strip().split("=")[1]
        _write_token_to_cache(token, username)

    logger.debug("Successfully acquired auth token")
    return token


def inject_token(
    request: httpx.Request,
    username: typing.Optional[str] = None,
) -> httpx.Request:
    """
    Inject a token based on the provided username into the request.

    For requests that need to use something except the default username,
    this injector should be used at the request level (instead of at client
    initialization) like this:

    .. code-block:: python

       client.get(url, auth=lambda r: inject_token(r, username=username))
    """
    if username is None:
        username = SETTINGS.X_SLURM_USER_NAME

    token = SETTINGS.X_SLURM_USER_TOKEN
    if token is None:
        token = acquire_token(username)

    request.headers["x-slurm-user-name"] = username
    request.headers["x-slurm-user-token"] = token
    return request


class AsyncBackendClient(httpx.AsyncClient):
    """
    Extends the httpx.AsyncClient class with automatic token acquisition for requests.
    The token is acquired lazily on the first httpx request issued.
    This client should be used for most agent actions.
    """

    _token: typing.Optional[str]

    def __init__(self):
        super().__init__(
            base_url=SETTINGS.BASE_SLURMRESTD_URL,
            auth=inject_token,
            event_hooks=dict(
                request=[self._log_request],
                response=[self._log_response],
            ),
        )

    @staticmethod
    async def _log_request(request: httpx.Request):
        logger.debug(f"Making request: {request.method} {request.url}")

    @staticmethod
    async def _log_response(response: httpx.Response):
        logger.debug(
            f"Received response: {response.request.method} "
            f"{response.request.url} "
            f"{response.status_code}"
        )


backend_client = AsyncBackendClient()
