import contextlib
import functools
import types
from collections.abc import Callable, Iterable
from typing import Any, Self, override

import attrs

from liblaf.grapes.error import DispatchLookupError
from liblaf.grapes.logging import depth_tracker

from ._base import BaseTimer
from ._function import TimedFunction
from ._iterable import TimedIterable


@attrs.define
class Timer(contextlib.AbstractContextManager, BaseTimer):
    @override
    @depth_tracker
    def __enter__(self) -> Self:
        self.start()
        return self

    @override
    @depth_tracker
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
        /,
    ) -> None:
        self.stop()

    @functools.singledispatchmethod
    def __call__(self, *args, **kwargs) -> Any:
        raise DispatchLookupError(self.__call__, args, kwargs)

    @__call__.register(Callable)
    def _[**P, T](self, func: Callable[P, T], /, **kwargs) -> TimedFunction[P, T]:
        return TimedFunction(func, timing=attrs.evolve(self, **kwargs))

    @__call__.register(Iterable)
    def _[T](
        self, iterable: Iterable[T], /, total: int | None = None, **kwargs
    ) -> TimedIterable[T]:
        return TimedIterable(iterable, timing=attrs.evolve(self, **kwargs), total=total)
