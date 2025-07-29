from collections.abc import Collection, Iterable, Iterator


class IterableWrapper[T](Collection[T]):
    iterable: Iterable[T]

    def __init__(self, iterable: Iterable[T], /) -> None:
        self.iterable = iterable

    def __contains__(self, x: object, /) -> bool:
        return x in self.iterable  # pyright: ignore[reportOperatorIssue]

    def __iter__(self) -> Iterator[T]:
        return iter(self.iterable)

    def __len__(self) -> int:
        return len(self.iterable)  # pyright: ignore[reportArgumentType]
