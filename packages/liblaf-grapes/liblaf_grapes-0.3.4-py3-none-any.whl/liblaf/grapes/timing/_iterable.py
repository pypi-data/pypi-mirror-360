from collections.abc import Iterable, Iterator

from liblaf.grapes.logging import depth_tracker

from ._base import BaseTimer


class TimedIterable[T]:
    timing: BaseTimer
    _iterable: Iterable[T]
    _total: int | None = None

    def __init__(
        self, iterable: Iterable[T], /, *, timing: BaseTimer, total: int | None = None
    ) -> None:
        self.timing = timing
        self._iterable = iterable
        self._total = total
        if self.timing.label is None:
            self.timing.label = "Iterable"

    def __contains__(self, x: object, /) -> bool:
        return x in self._iterable  # pyright: ignore[reportOperatorIssue]

    def __len__(self) -> int:
        if self._total is None:
            return len(self._iterable)  # pyright: ignore[reportArgumentType]
        return self._total

    def __iter__(self) -> Iterator[T]:
        with depth_tracker():
            self.timing.start()
            for item in self._iterable:
                yield item
                self.timing.stop()
                self.timing.start()
            self.timing.finish()
