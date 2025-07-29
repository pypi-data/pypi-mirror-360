import math
import statistics
from collections.abc import Sequence

UNITS: dict[str, float] = {
    "ns": 1e-9,
    "us": 1e-6,
    "ms": 1e-3,
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
    "y": 31536000,
}


def get_unit_seconds(unit: str) -> float:
    """Convert a time unit to its equivalent in seconds.

    Args:
        unit : The time unit to convert (e.g., 'm', 'h').

    Returns:
        The equivalent time in seconds.

    Raises:
        KeyError: If the provided unit is not found in the `UNITS` dictionary.
    """
    return UNITS[unit.lower()]


def human_duration_unit_precision(seconds: float) -> tuple[str, int]:  # noqa: C901, PLR0911, PLR0912
    """Determine the appropriate human-readable duration unit and precision for a given time in seconds.

    Args:
        seconds: The duration in seconds.

    Returns:
        A tuple containing the unit of time as a string and the precision as an integer. The unit can be "ns" (nanoseconds), "us" (microseconds), "ms" (milliseconds), "s" (seconds), "m" (minutes), or "h" (hours). The precision indicates the number of decimal places to display for the given unit.
    """
    if seconds <= 0:
        return "s", 0
    if seconds < 1e-09:
        return "ns", 3  # .999 ns
    if seconds < 1e-08:
        return "ns", 2  # 9.99 ns
    if seconds < 1e-07:
        return "ns", 1  # 99.9 ns
    if seconds < 1e-06:
        return "ns", 0  # 999. ns
    if seconds < 1e-05:
        return "us", 2  # 9.99 us
    if seconds < 1e-04:
        return "us", 1  # 99.9 us
    if seconds < 1e-03:
        return "us", 0  # 999. us
    if seconds < 1e-02:
        return "ms", 2  # 9.99 ms
    if seconds < 1e-01:
        return "ms", 1  # 99.9 ms
    if seconds < 1:
        return "ms", 0  # 999. ms
    if seconds < 10:
        return "s", 2  # 9.99 s
    if seconds < 60:
        return "s", 1  # 59.9 s
    if seconds < 3600:
        return "m", 0  # 59:59
    if seconds < 86400:
        return "h", 0  # 23:59:59
    return "h", 0


def human_duration(
    seconds: float, unit: str | None = None, precision: int | None = None
) -> str:
    """Convert a duration in seconds to a human-readable string format.

    Args:
        seconds: The duration in seconds to be converted.
        unit: The unit of time to use for the output. Can be one of {"ns", "us", "ms", "s", "m"}. If `None`, the unit will be determined automatically based on the duration.
        precision: The number of decimal places to include in the output. If `None`, the precision will be determined automatically based on the duration.

    Returns:
        The human-readable duration string.

    Notes:
        - For units "ns", "us", "ms", and "s", the output will be a floating-point number followed by the unit.
        - For unit "m", the output will be in the format "MM:SS".
        - For durations longer than an hour, the output will be in the format "HH:MM:SS".
        - The function currently does not handle durations longer than a day.
    """
    if not math.isfinite(seconds):
        return "?? sec"
    if (unit is None) or (precision is None):
        unit, precision = human_duration_unit_precision(seconds)
    if unit in {"ns", "us", "ms", "s"}:
        unit_seconds: float = get_unit_seconds(unit)
        value: float = seconds / unit_seconds
        human: str = f"{value:.{precision}f}".lstrip("0")
        if precision == 0:
            human += "."
        if unit == "us":
            unit = "µs"
        human += f" {unit}"
        return human
    if unit == "m":
        minutes: int = int(seconds // 60)
        seconds %= 60
        return f"{minutes}:{seconds:02.0f}"
    hours: int = int(seconds // 3600)
    seconds %= 3600
    minutes: int = int(seconds // 60)
    seconds %= 60
    return f"{hours}:{minutes:02.0f}:{seconds:02.0f}"
    # TODO: handle longer durations


def human_duration_with_variance(mean: float, std: float) -> str:
    """Returns a human-readable string representing a duration with variance.

    Args:
        mean: The mean duration.
        std: The standard deviation of the duration.

    Returns:
        A string representing the mean duration with its variance in the format "mean ± std". If the standard deviation is not finite, only the mean duration is returned.
    """
    if not math.isfinite(std):
        return human_duration(mean)
    return f"{human_duration(mean)} ± {human_duration(std)}"


def human_duration_series(series: Sequence[float]) -> str:
    """Convert a series of durations into a human-readable string.

    Args:
        series: An array-like object containing duration values.

    Returns:
        A human-readable string representing the duration. If the series contains only one element, it returns the human-readable format of that single duration. If the series contains more than one element, it returns the mean duration with its variance in a human-readable format.
    """
    if len(series) == 0:
        return "NaN"
    if len(series) <= 1:
        return human_duration(series[0])
    return human_duration_with_variance(
        statistics.mean(series), statistics.stdev(series)
    )
