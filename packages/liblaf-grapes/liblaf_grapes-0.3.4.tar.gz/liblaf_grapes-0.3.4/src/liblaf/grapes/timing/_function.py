import functools
from collections.abc import Callable

from liblaf.grapes import pretty
from liblaf.grapes.logging import depth_tracker

from ._base import BaseTimer


class TimedFunction[**P, T]:
    timing: BaseTimer
    __wrapped__: Callable[P, T]

    def __init__(self, fn: Callable[P, T], /, *, timing: BaseTimer) -> None:
        self.timing = timing
        if self.timing.label is None:
            self.timing.label = pretty.func(fn).plain or "Function"
        functools.update_wrapper(self, fn)

    @depth_tracker
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        self.timing.start()
        result: T = self.__wrapped__(*args, **kwargs)
        self.timing.stop()
        return result
