"""Core module for request processing operations"""
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

    if request.status_code == 401:

        raise requests.HTTPError("Authentication failed.")

    elif request.status_code == 200:

        payload = request.json()

    else:

        raise requests.RequestException("Unknown error.")

    return payload