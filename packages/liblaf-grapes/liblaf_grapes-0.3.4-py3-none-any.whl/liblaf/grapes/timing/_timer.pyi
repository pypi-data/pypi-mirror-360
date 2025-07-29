import contextlib
import types
from collections.abc import Callable, Iterable
from typing import Self, overload, override

from ._base import BaseTimer
from ._function import TimedFunction
from ._iterable import TimedIterable

class Timer(contextlib.AbstractContextManager, BaseTimer):
    @override
    def __enter__(self) -> Self: ...
    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
        /,
    ) -> None: ...
    @overload
    def __call__[**P, T](
        self, func: Callable[P, T], /, **kwargs
    ) -> TimedFunction[P, T]: ...
    @overload
    def __call__[T](
        self, iterable: Iterable[T], /, total: int | None = None, **kwargs
    ) -> TimedIterable[T]: ...
