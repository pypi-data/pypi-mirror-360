import builtins
import functools
from collections.abc import Callable, Mapping

import loguru
from loguru import _filters, logger

from .typed import Filter

# ref: <https://github.com/Delgan/loguru/blob/a69bfc451413f71b81761a238db4b5833cf0a992/loguru/_logger.py#L899-L956>


@functools.singledispatch
def as_filter_func(filter_: Filter | None, /) -> "loguru.FilterFunction | None":
    msg: str = f"Invalid filter, it should be a function, a string or a dict, not: '{type(filter_).__name__}'"
    raise TypeError(msg)


@as_filter_func.register
def _(_f: None, /) -> None:
    return None


@as_filter_func.register(str)
def _(f: str, /) -> "loguru.FilterFunction":
    if f == "":
        return _filters.filter_none
    parent: str = f + "."
    length: int = len(parent)
    return functools.partial(_filters.filter_by_name, parent=parent, length=length)


@as_filter_func.register(Callable)  # pyright: ignore[reportArgumentType, reportCallIssue]
def _(f: Callable, /) -> "loguru.FilterFunction":
    if f == builtins.filter:
        msg = (
            "The built-in 'filter()' function cannot be used as a 'filter' parameter, "
            "this is most likely a mistake (please double-check the arguments passed "
            "to 'logger.add()')."
        )
        raise ValueError(msg)
    return f


@as_filter_func.register(Mapping)
def _(f: Mapping[str, int | str], /) -> "loguru.FilterFunction":
    level_per_module: dict[str, int] = {}
    for module, level_ in f.items():
        if module is not None and not isinstance(module, str):
            msg: str = (
                "The filter dict contains an invalid module, "
                f"it should be a string (or None), not: '{type(module).__name__}'"
            )
            raise TypeError(msg)
        if level_ is False:
            levelno_ = False
        elif level_ is True:
            levelno_ = 0
        elif isinstance(level_, str):
            try:
                levelno_: int = logger.level(level_).no
            except ValueError:
                msg = (
                    f"The filter dict contains a module '{module}' associated to a level name "
                    f"which does not exist: '{level_}'"
                )
                raise ValueError(msg) from None
        elif isinstance(level_, int):
            levelno_ = level_
        else:
            msg = (
                f"The filter dict contains a module '{module}' associated to an invalid level, "
                f"it should be an integer, a string or a boolean, not: '{type(level_).__name__}'"
            )
            raise TypeError(msg)
        if levelno_ < 0:
            msg = (
                f"The filter dict contains a module '{module}' associated to an invalid level, "
                f"it should be a positive integer, not: '{levelno_}'"
            )
            raise ValueError(msg)
        level_per_module[module] = levelno_
    return functools.partial(
        _filters.filter_by_level, level_per_module=level_per_module
    )
