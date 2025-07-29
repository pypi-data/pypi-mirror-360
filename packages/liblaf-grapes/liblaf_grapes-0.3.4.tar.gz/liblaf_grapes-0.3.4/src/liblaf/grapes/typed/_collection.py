from collections.abc import Iterator
from typing import Protocol, runtime_checkable


@runtime_checkable
class SizedIterable[T](Protocol):
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[T]: ...
