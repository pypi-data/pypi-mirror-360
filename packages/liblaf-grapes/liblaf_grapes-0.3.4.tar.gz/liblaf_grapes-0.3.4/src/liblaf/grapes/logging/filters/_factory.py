from collections.abc import Mapping

import loguru

from ._as_filter_func import as_filter_func
from ._composite import filter_all
from ._once import filter_once
from .typed import Filter

DEFAULT_FILTER: "loguru.FilterDict" = {
    "": "INFO",
    "__main__": "TRACE",
    "liblaf": "DEBUG",
}


def make_filter(
    filter_: Filter | None = None, *, inherit: bool = True
) -> "loguru.FilterFunction | None":
    if inherit:
        if filter_ is None:
            filter_ = DEFAULT_FILTER
        elif isinstance(filter_, Mapping):
            filter_ = {**DEFAULT_FILTER, **filter_}
    filter_ = as_filter_func(filter_)  # pyright: ignore[reportArgumentType]
    if inherit:
        filter_ = filter_all(filter_, filter_once())
    return filter_
