import functools
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING

import loguru

from liblaf.grapes.logging import depth_tracker

from .defaults import DEFAULT_STATS

if TYPE_CHECKING:
    from ._base import BaseTimer


@depth_tracker
def log_record(
    records: "BaseTimer | None" = None,
    /,
    *,
    idx: int = -1,
    level: int | str = "DEBUG",
    logger: "loguru.Logger | None" = None,
    threshold: float = 0.1,  # seconds
) -> Callable | None:
    if records is None:
        return functools.partial(
            log_record, idx=idx, level=level, logger=logger, threshold=threshold
        )
    return records.log_record(idx=idx, level=level, logger=logger, threshold=threshold)


@depth_tracker
def log_summary(
    records: "BaseTimer | None" = None,
    /,
    *,
    level: int | str = "INFO",
    logger: "loguru.Logger | None" = None,
    stats: Iterable[str] = DEFAULT_STATS,
) -> Callable | None:
    if records is None:
        return functools.partial(log_summary, level=level, logger=logger, stats=stats)
    return records.log_summary(level=level, logger=logger, stats=stats)


__all__ = ["log_record", "log_summary"]
