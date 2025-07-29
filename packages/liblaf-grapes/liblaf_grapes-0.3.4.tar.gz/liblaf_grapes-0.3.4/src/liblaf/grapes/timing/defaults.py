from collections.abc import Sequence

from ._get_time import TimerName

DEFAULT_STATS: Sequence[str] = ("mean_std", "median", "min")
DEFAULT_TIMERS: Sequence[TimerName] = ("perf",)
