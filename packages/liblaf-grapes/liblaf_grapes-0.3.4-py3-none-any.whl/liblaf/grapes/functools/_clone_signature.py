from collections.abc import Callable
from typing import Any


def clone_signature[C](_source: C, /) -> Callable[[Any], C]:
    def wrapper(obj: Any) -> C:
        return obj

    return wrapper
