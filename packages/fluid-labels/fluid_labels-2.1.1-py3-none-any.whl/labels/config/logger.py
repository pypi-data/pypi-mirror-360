import logging
import sys

from bugsnag.handlers import (
    BugsnagHandler,
)

LOGGER_HANDLER = logging.StreamHandler()
LOGGER: logging.Logger = logging.getLogger()

FORMAT: str = "[%(levelname)s] %(message)s"

LOGGER_FORMATTER: logging.Formatter = logging.Formatter(FORMAT)

LOGGER_REMOTE_HANDLER = BugsnagHandler(extra_fields={"extra": ["extra"]})


def configure_logger(*, log_to_remote: bool) -> None:
    LOGGER_HANDLER.setStream(sys.stdout)
    LOGGER_HANDLER.setLevel(logging.INFO)
    LOGGER_HANDLER.setFormatter(LOGGER_FORMATTER)

    LOGGER.setLevel(logging.INFO)
    LOGGER.addHandler(LOGGER_HANDLER)

    if log_to_remote:
        LOGGER_REMOTE_HANDLER.setLevel(logging.ERROR)
        LOGGER.addFilter(LOGGER_REMOTE_HANDLER.leave_breadcrumbs)
        LOGGER.addHandler(LOGGER_REMOTE_HANDLER)


def modify_logger_level() -> None:
    LOGGER.setLevel(logging.DEBUG)
    LOGGER_HANDLER.setLevel(logging.DEBUG)
