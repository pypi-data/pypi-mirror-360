from typing import overload

import loguru

from .typed import Filter

@overload
def as_filter_func(filter_: None, /) -> None: ...
@overload
def as_filter_func(filter_: Filter, /) -> loguru.FilterFunction: ...
