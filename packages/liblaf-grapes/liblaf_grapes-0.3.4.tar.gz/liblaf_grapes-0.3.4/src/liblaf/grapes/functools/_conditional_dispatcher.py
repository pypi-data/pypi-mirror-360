import functools
from collections.abc import Callable, Mapping
from typing import Any, NoReturn, overload

import attrs
import sortedcontainers
from rich.text import Text

from liblaf.grapes import pretty
from liblaf.grapes.typed import Decorator


@attrs.frozen
class Function:
    condition: Callable[..., bool]
    function: Callable
    precedence: int = 0


class NotFoundLookupError(LookupError):
    func: Callable
    args: tuple
    kwargs: Mapping

    def __init__(self, func: Callable, args: tuple, kwargs: Mapping) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        return f"{self.pretty_call.plain} could not be resolved."

    @property
    def pretty_call(self) -> Text:
        return pretty.call(self.func, self.args, self.kwargs)


def _fallback(func: Callable) -> Callable[..., NoReturn]:
    def fallback(*args, **kwargs) -> NoReturn:
        raise NotFoundLookupError(func, args, kwargs)

    return fallback


class ConditionalDispatcher:
    fallback: Callable
    functions: sortedcontainers.SortedList[Function]

    def __init__(self) -> None:
        self.functions = sortedcontainers.SortedList(key=lambda f: -f.precedence)

    def __call__(self, *args, **kwargs) -> Any:
        for func in self.functions:
            try:
                if func.condition(*args, **kwargs):
                    return func.function(*args, **kwargs)
            except TypeError:
                continue
        return self.fallback(*args, **kwargs)

    @overload
    def final[**P, T](
        self, fn: Callable[P, T], /, *, fallback: bool = False
    ) -> Callable[P, T]: ...
    @overload
    def final(self, /, *, fallback: bool = False) -> Decorator: ...
    def final[**P, T](
        self, fn: Callable[P, T] | None = None, /, *, fallback: bool = False
    ) -> Callable:
        if fn is None:
            return functools.partial(self.final, fallback=fallback)
        if fallback:
            self.fallback = fn
        else:
            self.fallback = _fallback(fn)
        functools.update_wrapper(self, fn)
        return self

    def register(
        self, condition: Callable[..., bool], *, precedence: int = 0
    ) -> Decorator:
        def decorator[**P, T](fn: Callable[P, T]) -> Callable[P, T]:
            self.functions.add(Function(condition, fn, precedence))
            return fn

        return decorator
