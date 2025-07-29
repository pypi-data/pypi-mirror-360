from collections.abc import Callable, Hashable

import loguru


def default_transform(record: "loguru.Record") -> Hashable:
    return (
        record["file"].path,
        record["function"],
        record["level"].no,
        record["line"],
        record["message"],
        record["module"],
        record["name"],
    )


def filter_once(
    as_hashable: "Callable[[loguru.Record], Hashable]" = default_transform,
) -> "loguru.FilterFunction":
    history: set[Hashable] = set()

    def filter_(record: "loguru.Record") -> bool:
        if not record["extra"].get("once", False):
            return True
        hashable: Hashable = as_hashable(record)
        if hashable in history:
            return False
        history.add(hashable)
        return True

    return filter_
