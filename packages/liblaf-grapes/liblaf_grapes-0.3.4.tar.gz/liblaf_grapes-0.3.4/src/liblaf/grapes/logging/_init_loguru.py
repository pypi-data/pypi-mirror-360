import functools
import logging
import sys
import types
from collections.abc import Sequence
from typing import Protocol, Unpack

import loguru
from loguru import logger

from liblaf.grapes.conf import config

from ._intercept import setup_loguru_logging_intercept
from ._level import DEFAULT_LEVELS, add_level
from ._std import clear_handlers
from .handler import file_handler, jsonl_handler, rich_handler


def init_loguru(
    handlers: Sequence["loguru.HandlerConfig"] | None = None,
    levels: Sequence["loguru.LevelConfig"] | None = None,
    *,
    enable_link: bool = True,
    **kwargs: Unpack["loguru.BasicHandlerConfig"],
) -> None:
    traceback_install()
    if handlers is None:
        handlers: list[loguru.HandlerConfig] = [
            rich_handler(enable_link=enable_link, **kwargs)
        ]
        if config.file("LOGGING_FILE", default=None):
            handlers.append(file_handler(**kwargs))  # pyright: ignore[reportArgumentType]
        if config.file("LOGGING_JSONL", default=None):
            handlers.append(jsonl_handler(**kwargs))  # pyright: ignore[reportArgumentType]
    logger.configure(handlers=handlers)
    for lvl in levels or DEFAULT_LEVELS:
        add_level(**lvl)
    setup_loguru_logging_intercept(kwargs.get("level", logging.NOTSET))
    clear_handlers()


def traceback_install(
    except_level: int | str | None = "CRITICAL",
    except_message: str = "",
    *,
    unraisable_level: int | str | None = "ERROR",
) -> None:
    if except_level is not None:
        sys.excepthook = functools.partial(
            excepthook, level=except_level, message=except_message
        )
    if unraisable_level is not None:
        sys.unraisablehook = functools.partial(unraisablehook, level=unraisable_level)


def excepthook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    traceback: types.TracebackType,
    *,
    level: int | str = "CRITICAL",
    message: str = "",
) -> None:
    logger.opt(exception=(exc_type, exc_value, traceback)).log(level, message)


class UnraisableHookArgs(Protocol):
    exc_type: type[BaseException]
    exc_value: BaseException | None
    exc_traceback: types.TracebackType | None
    err_msg: str | None
    object: object


def unraisablehook(
    unraisable: UnraisableHookArgs, /, *, level: int | str = "ERROR"
) -> None:
    if logger is None:
        # workaround for "Error ignored in: ..."
        return
    logger.opt(
        exception=(unraisable.exc_type, unraisable.exc_value, unraisable.exc_traceback)
    ).log(
        level,
        "{err_msg}: {object!r}",
        err_msg=unraisable.err_msg or "Exception ignored in",
        object=unraisable.object,
    )
