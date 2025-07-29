from collections.abc import Iterable
from typing import overload

import loguru

from ._base import BaseTimer, Callback

@overload
def log_record(
    *,
    idx: int = -1,
    level: int | str = "DEBUG",
    logger: loguru.Logger | None = None,
    threshold: float = 0.1,  # seconds
) -> Callback: ...
@overload
def log_record(
    records: BaseTimer,
    /,
    *,
    idx: int = -1,
    level: int | str = "DEBUG",
    logger: loguru.Logger | None = None,
    threshold: float = 0.1,  # seconds
) -> None: ...
@overload
def log_summary(
    *,
    level: int | str = "INFO",
    logger: loguru.Logger | None = None,
    stats: Iterable[str] = ...,
) -> Callback: ...
@overload
def log_summary(
    records: BaseTimer,
    /,
    *,
    level: int | str = "INFO",
    logger: loguru.Logger | None = None,
    stats: Iterable[str] = ...,
) -> None: ...

__all__ = ["log_record", "log_summary"]
