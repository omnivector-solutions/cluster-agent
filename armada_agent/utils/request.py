"""Core module for request processing operations"""
from armada_agent.utils import response

import requests


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

    if response.status_code == 401:

        raise requests.HTTPError("Authentication failed.")

    elif response.status_code == 200:

        payload = response.json()

    else:

        raise requests.RequestException("Unknown error.")

    return payload