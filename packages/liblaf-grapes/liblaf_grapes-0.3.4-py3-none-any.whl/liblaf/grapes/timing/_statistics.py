import math
import statistics
from collections.abc import Iterator, Mapping, Sequence
from typing import ClassVar

import attrs

from liblaf.grapes import human


@attrs.define
class Statistics(Mapping[str, str]):
    STATISTICS: ClassVar[Sequence[str]] = (
        "max",
        "mean",
        "mean_std",
        "median",
        "min",
        "stdev",
        "sum",
    )
    data: Sequence[float] = attrs.field(factory=list)

    def __getitem__(self, key: str, /) -> str:
        try:
            value: float | str | None = getattr(self, key, None)
        except statistics.StatisticsError:
            return human.human_duration(math.nan)
        if value is None:
            raise KeyError(key)
        if isinstance(value, (int, float)):
            value = human.human_duration(value)
        return value

    def __iter__(self) -> Iterator[str]:
        yield from self.STATISTICS

    def __len__(self) -> int:
        return len(self.STATISTICS)

    def pretty_name(self, key: str) -> str:
        if key == "mean_std":
            return "mean"
        return key

    @property
    def max(self) -> float:
        return max(self.data)

    @property
    def mean(self) -> float:
        return statistics.mean(self.data)

    @property
    def mean_std(self) -> str:
        if len(self.data) == 0:
            return human.human_duration(math.nan)
        if len(self.data) == 1:
            return human.human_duration(self.data[0])
        human_mean: str = human.human_duration(self.mean)
        human_stdev: str = human.human_duration(self.stdev)
        return f"{human_mean} ± {human_stdev}"

    @property
    def median(self) -> float:
        return statistics.median(self.data)

    @property
    def min(self) -> float:
        return min(self.data)

    @property
    def stdev(self) -> float:
        return statistics.stdev(self.data)

    @property
    def sum(self) -> float:
        return sum(self.data)
