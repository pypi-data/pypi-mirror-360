from collections.abc import Callable
from typing import Protocol, overload


class Decorator(Protocol):
    def __call__[**P, T](self, fn: Callable[P, T], /) -> Callable[P, T]: ...


class DecoratorWithArguments[**P](Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Decorator: ...


class DecoratorWithOptionalArguments[**Q](Protocol):
    @overload
    def __call__[**P, T](
        self, fn: Callable[P, T], /, *args: Q.args, **kwargs: Q.kwargs
    ) -> Callable[P, T]: ...
    @overload
    def __call__(self, *args: Q.args, **kwargs: Q.kwargs) -> Decorator: ...
