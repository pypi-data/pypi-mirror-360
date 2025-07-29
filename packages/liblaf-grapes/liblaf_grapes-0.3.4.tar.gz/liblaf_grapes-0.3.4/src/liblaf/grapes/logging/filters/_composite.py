import loguru

from ._as_filter_func import as_filter_func
from .typed import Filter


def filter_all(*filters: Filter | None) -> "loguru.FilterFunction":
    filters: list[loguru.FilterFunction] = [
        fn for f in filters if (fn := as_filter_func(f)) is not None
    ]

    def filter_(record: "loguru.Record") -> bool:
        return all(fn(record) for fn in filters)

    return filter_


def filter_any(*filters: Filter | None) -> "loguru.FilterFunction":
    filters: list[loguru.FilterFunction] = [
        fn for f in filters if (fn := as_filter_func(f)) is not None
    ]

    def filter_(record: "loguru.Record") -> bool:
        return any(fn(record) for fn in filters)

    return filter_
