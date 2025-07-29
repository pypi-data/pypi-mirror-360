import inspect
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import autoregistry
import rich
import rich.highlighter
from rich.style import Style
from rich.text import Text

_func = autoregistry.Registry(prefix="_func_")


def func(obj: Callable, *, style: Literal["short", "long"] = "short") -> Text:
    return _func[style](obj)


@_func
def _func_short(obj: Callable) -> Text:
    obj = inspect.unwrap(obj)
    text = Text()
    name: str = _get_name(obj)
    source_file: Path | None = _get_source_file(obj)
    lineno: int = _get_source_lineno(obj)
    if source_file and lineno:
        text.append(
            f"{name}()",
            style=Style(link=f"{source_file.as_uri()}#{lineno}"),
        )
    else:
        text.append(f"{name}()")
    return text


@_func
def _func_long(obj: Callable) -> Text:
    obj = inspect.unwrap(obj)
    text = Text()
    module: str = _get_module(obj)
    qualname: str = _get_qualname(obj)
    source_file: Path | None = _get_source_file(obj)
    lineno: int = _get_source_lineno(obj)
    if source_file:
        text.append(module, style=Style(link=source_file.as_uri()))
        text.append(".")
        text.append(
            f"{qualname}(...)",
            style=Style(link=f"{source_file.as_uri()}#{lineno}"),
        )
    else:
        text.append(f"{module}.{qualname}(...)")
    return text


highlighter = rich.highlighter.ReprHighlighter()


def call(fn: Callable, args: Sequence, kwargs: Mapping) -> Text:
    args, kwargs = _bind_safe(fn, args, kwargs)
    fn = inspect.unwrap(fn)
    name: str = _get_name(fn)
    source_file: Path | None = _get_source_file(fn)
    lineno: int = _get_source_lineno(fn)
    text: Text = Text()
    if source_file:
        text.append(name, style=Style(link=f"{source_file.as_uri()}#{lineno}"))
    else:
        text.append(name)
    text.append("(")
    parts: list[str] = [repr(value) for value in args]
    parts += [f"{key}={value!r}" for key, value in kwargs.items()]
    text.append(", ".join(parts))
    text.append(")")
    text = highlighter(text)
    return text


def _bind_safe(
    fn: Callable, args: Sequence, kwargs: Mapping
) -> tuple[Sequence, Mapping]:
    try:
        signature: inspect.Signature = inspect.signature(fn)
        arguments: inspect.BoundArguments = signature.bind(*args, **kwargs)
    except TypeError:
        return args, kwargs
    else:
        return arguments.args, arguments.kwargs


def _get_module(obj: Any) -> str:
    return getattr(obj, "__module__", "unknown")


def _get_name(obj: Any) -> str:
    return getattr(obj, "__name__", "<unknown>")


def _get_qualname(obj: Any) -> str:
    return getattr(obj, "__qualname__", "<unknown>")


def _get_source_file(obj: Any) -> Path | None:
    try:
        if source_file := inspect.getsourcefile(obj):
            return Path(source_file)
    except TypeError:
        pass
    return None


def _get_source_lineno(obj: Any) -> int:
    try:
        lineno: int
        _lines, lineno = inspect.getsourcelines(obj)
    except (OSError, TypeError):
        pass
    else:
        return lineno
    return 0
