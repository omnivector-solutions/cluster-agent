"""Core module for request processing operations"""
from armada_agent.settings import SETTINGS
from armada_agent.utils.logging import logger
from armada_agent.utils.slurmrestd import slurmrestd_header

from urllib.parse import urljoin
from typing import Dict, List
import requests
import asyncio

from aiohttp import ClientSession


LOOP = asyncio.get_event_loop()


# Semaphore is used to chunck the requests. Setting to
# 10 indicates that our framework will make 10 async
# requests, wait for the responses, make another 10
# and goes on
_SEM = asyncio.Semaphore(10, loop=LOOP)


def check_request_status(request):
    """
    Utility function to check whether the request
    was authorized or not

    Args:
        request (request.Response): Input response

    Returns:
        dict: request payload

    Raise:
        requests.HTTPError: Authorization against slurmrestd failed
        requests.RequestException: Unknown error
    """

    if request.status_code == 401:

        raise requests.HTTPError("Authentication failed.")

    elif request.status_code == 200:

        payload = request.json()

    else:

        raise requests.RequestException("Unknown error.")

    return payload


async def general_slurmrestd_request(endpoint: str):
    """
    Utility function to call a generic slurmrestd endpoint and
    get its payload response

    Args:
        endpoint (str): Slurmrestd endpoint, e.g. /slurm/v0.0.36/partitions

    Returns:
        Dict: response payload from slurmrestd endpoint
    """

    response = requests.get(
        urljoin(SETTINGS.BASE_SLURMRESTD_URL, endpoint),
        headers=await slurmrestd_header(),
    )

    data = check_request_status(response)

    return data


async def fetch(url: str, method: str, param: Dict, data: Dict, session: ClientSession):
    r = await session.request(method, url, params=param, data=data)
    return r


async def safe_fetch(url: str, method: str, param: Dict, data: Dict, session: ClientSession):
    async with _SEM:
        return await fetch(url, method, param, data, session)


async def async_req(
    urls: List[str],
    methods: List[str],
    header: Dict[str, str],
    params: List,
    data: List,
):

    assert len(urls) == len(params) == len(data), "You must set params for each URL"

    tasks = []

    async with ClientSession(headers=header) as session:
        for url, method, param, _data in zip(urls, methods, params, data):
            task = asyncio.ensure_future(safe_fetch(url, method, param, _data, session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        return responses
