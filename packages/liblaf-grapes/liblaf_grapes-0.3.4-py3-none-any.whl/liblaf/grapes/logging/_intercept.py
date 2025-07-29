import inspect
import itertools
import logging
from collections.abc import Iterable

import loguru._logger
from loguru import logger


class InterceptHandler(logging.Handler):
    """A logging handler that intercepts log messages and redirects them to Loguru.

    This handler is designed to be compatible with the standard logging framework and allows the use of Loguru for logging while maintaining compatibility with existing logging configurations.

    References:
        1. [Overview — loguru documentation](https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging)
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record.

        This function is called by the logging framework to handle a log record.
        It maps the standard logging levels to Loguru levels and finds the caller
        frame from where the log message originated. Finally, it logs the message
        using Loguru.

        Args:
            record: The log record to be emitted.
        """
        if logger is None:
            # workaround for "Error ignored in: ..."
            return

        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_loguru_logging_intercept(
    level: int | str = logging.NOTSET, modules: Iterable[str] = ()
) -> None:
    """Sets up logging interception using Loguru.

    This function configures the logging module to use Loguru for handling log messages. It sets the logging level and replaces the handlers for the specified modules with an InterceptHandler that redirects log messages to Loguru.

    Args:
        level: The logging level to set.
        modules: A list of module names whose loggers should be intercepted.

    References:
        1. [loguru-logging-intercept/loguru_logging_intercept.py at f358b75ef4162ea903bf7a3298c22b1be83110da · MatthewScholefield/loguru-logging-intercept](https://github.com/MatthewScholefield/loguru-logging-intercept/blob/f358b75ef4162ea903bf7a3298c22b1be83110da/loguru_logging_intercept.py#L35C5-L42)
    """
    core: loguru._logger.Core = logger._core  # pyright: ignore[reportAttributeAccessIssue] # noqa: SLF001
    for lvl in core.levels.values():
        logging.addLevelName(lvl.no, lvl.name)
    logging.basicConfig(level=level, handlers=[InterceptHandler()])
    for logger_name in itertools.chain(("",), modules):
        mod_logger: logging.Logger = logging.getLogger(logger_name)
        mod_logger.handlers = [InterceptHandler(level=level)]
        mod_logger.propagate = False
