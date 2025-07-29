from collections.abc import Sequence
from typing import Unpack

import loguru
from rich.console import Console

from liblaf.grapes import pretty
from liblaf.grapes.logging.filters import make_filter
from liblaf.grapes.logging.sink import (
    LevelColumn,
    LocationColumn,
    LoguruRichHandler,
    MessageColumn,
    RichLoggingColumn,
    TimeColumn,
)


def rich_handler(
    console: Console | None = None,
    columns: Sequence[RichLoggingColumn] | None = None,
    *,
    enable_link: bool = True,
    **kwargs: Unpack["loguru.BasicHandlerConfig"],
) -> "loguru.BasicHandlerConfig":
    if console is None:
        console = pretty.get_console(stderr=True)
    if columns is None:
        columns = [
            TimeColumn(),
            LevelColumn(),
            LocationColumn(enable_link=enable_link),
            MessageColumn(),
        ]
    kwargs["sink"] = LoguruRichHandler(console=console, columns=columns)
    kwargs["format"] = ""
    kwargs["filter"] = make_filter(kwargs.get("filter"))
    return kwargs
