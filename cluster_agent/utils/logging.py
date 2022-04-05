"""Core module for logging operations"""

from traceback import format_tb

from loguru import logger
from buzz import DoExceptParams


def log_error(params: DoExceptParams):
    """
    Provide a utility function to log a Buzz-based exception and the stack-trace of
    the error's context.

    :param: params: A DoExceptParams instance containing the original exception, a
                    message describing it, and the stack trace of the error.
    """
    logger.error(
        "\n".join(
            [
                params.final_message,
                "--------",
                "Traceback:",
                "".join(format_tb(params.trace)),
            ]
        )
    )
