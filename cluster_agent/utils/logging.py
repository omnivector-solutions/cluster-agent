"""Core module for logging operations"""

import logging
from traceback import format_tb

from buzz import DoExceptParams
from loguru import logger


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


class InterceptHandler(logging.Handler):
    """
    Intercept python logging messages and forward them to loguru.

    Reference:
    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


logging.basicConfig(handlers=[InterceptHandler()], level=0)
