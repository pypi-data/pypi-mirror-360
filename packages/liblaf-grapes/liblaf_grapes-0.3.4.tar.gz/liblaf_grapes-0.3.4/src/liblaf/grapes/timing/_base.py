import collections
from collections.abc import Callable, Generator, Iterable, Mapping, Sequence

import attrs
import loguru

from liblaf.grapes import const, human
from liblaf.grapes.logging import depth_tracker

from . import callback
from ._get_time import TimerName, get_time
from ._statistics import Statistics
from .defaults import DEFAULT_STATS, DEFAULT_TIMERS

type Callback = Callable[[BaseTimer], None] | const.NopType


@attrs.define
class BaseTimer:
    label: str | None = attrs.field(default=None)
    timers: Sequence[TimerName] = attrs.field(default=DEFAULT_TIMERS, kw_only=True)
    cb_start: Callback | None = attrs.field(default=None, kw_only=True)
    cb_stop: Callback | None = attrs.field(
        default=callback.log_record,
        converter=attrs.converters.default_if_none(callback.log_record),
        kw_only=True,
    )
    cb_finish: Callback | None = attrs.field(
        default=callback.log_summary,
        converter=attrs.converters.default_if_none(callback.log_summary),
        kw_only=True,
    )
    _records: collections.defaultdict[TimerName, list[float]] = attrs.field(
        init=False, factory=lambda: collections.defaultdict(list)
    )
    _time_start: dict[TimerName, float] = attrs.field(init=False, factory=dict)
    _time_stop: dict[TimerName, float] = attrs.field(init=False, factory=dict)

    @property
    def default_timer(self) -> TimerName:
        return self.timers[0]

    # region Timer

    def elapsed(self, timer: TimerName | None = None) -> float:
        timer = timer or self.default_timer
        time_stop: float
        if timer in self._time_stop:
            time_stop = self._time_stop[timer]
        else:
            time_stop = get_time(timer)
        return time_stop - self._time_start[timer]

    @depth_tracker
    def start(self) -> None:
        for timer in self.timers:
            self._time_start[timer] = get_time(timer)
        if callable(self.cb_start):
            self.cb_start(self)

    @depth_tracker
    def stop(self) -> None:
        for timer in self.timers:
            self._time_stop[timer] = get_time(timer)
            elapsed: float = self._time_stop[timer] - self._time_start[timer]
            self._records[timer].append(elapsed)
        if callable(self.cb_stop):
            self.cb_stop(self)

    @depth_tracker
    def finish(self) -> None:
        if callable(self.cb_finish):
            self.cb_finish(self)

    # endregion Timer

    # region Container

    @property
    def height(self) -> int:
        return len(self.column())

    @property
    def width(self) -> int:
        return len(self.timers)

    def clear(self) -> None:
        self._records.clear()
        self._time_start.clear()
        self._time_stop.clear()

    def column(self, timer: TimerName | None = None) -> Sequence[float]:
        timer = timer or self.default_timer
        return self._records[timer]

    def iter_columns(self) -> Generator[tuple[TimerName, Sequence[float]]]:
        for timer in self.timers:
            yield timer, self.column(timer)

    def iter_rows(self) -> Generator[Mapping[TimerName, float]]:
        for idx in range(self.height):
            yield self.row(idx)

    def row(self, idx: int = -1) -> Mapping[TimerName, float]:
        return {k: v[idx] for k, v in self._records.items()}

    # endregion Container

    # region Human-Readable

    def human_record(self, idx: int = -1) -> TimerName:
        label: TimerName = self.label or "Timer"
        items: list[TimerName] = []
        for k, v in self.row(idx).items():
            hd: TimerName = human.human_duration(v)
            items.append(f"{k}: {hd}")
        return f"{label} > {', '.join(items)}"

    def human_summary(self, stats: Iterable[str] = DEFAULT_STATS) -> str:
        label: TimerName = self.label or "Timer"
        header: TimerName = f"{label} (count: {self.height})"
        if self.height == 0:
            return header
        lines: list[TimerName] = []
        for timer in self.timers:
            stats_str: list[str] = []
            for stat in stats:
                stats_mapping: Statistics = self.stats(timer)
                name: str = stats_mapping.pretty_name(stat)
                value: str = stats_mapping[stat]
                stats_str.append(f"{name}: {value}")
            line: str = f"{timer} > {', '.join(stats_str)}"
            lines.append(line)
        if self.width == 1:
            return f"{header} {lines[0]}"
        return f"{header}\n" + "\n".join(lines)

    @depth_tracker
    def log_record(
        self,
        *,
        idx: int = -1,
        level: int | str = "DEBUG",
        logger: "loguru.Logger | None" = None,
        threshold: float = 0.1,  # seconds
    ) -> None:
        if self.elapsed() < threshold:
            return
        if logger is None:
            logger = loguru.logger.opt(depth=depth_tracker.depth)
        logger.log(level, self.human_record(idx))

    @depth_tracker
    def log_summary(
        self,
        *,
        level: int | str = "INFO",
        logger: "loguru.Logger | None" = None,
        stats: Iterable[str] = DEFAULT_STATS,
    ) -> None:
        if logger is None:
            logger = loguru.logger.opt(depth=depth_tracker.depth)
        logger.log(level, self.human_summary(stats))

    # endregion Human-Readable

    # region Statistics

    def stats(self, timer: TimerName | None = None) -> Statistics:
        return Statistics(self.column(timer))

    # endregion Statistics
