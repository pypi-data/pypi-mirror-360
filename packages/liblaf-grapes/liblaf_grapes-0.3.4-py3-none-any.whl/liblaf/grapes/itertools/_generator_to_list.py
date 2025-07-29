import functools
from collections.abc import Callable, Generator


def generator_to_list[**P, T](fn: Callable[P, Generator[T]]) -> Callable[P, list[T]]:
    @functools.wraps(fn)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> list[T]:
        return list(fn(*args, **kwargs))

    return wrapped
