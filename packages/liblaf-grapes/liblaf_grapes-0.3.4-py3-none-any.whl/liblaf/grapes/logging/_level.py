import contextlib
import enum
from collections.abc import Sequence
from typing import override

import loguru
from loguru import logger


class LogLevel(enum.StrEnum):
    @override
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.upper()

    # ref: <https://github.com/Delgan/loguru/blob/master/loguru/_defaults.py>
    TRACE = enum.auto()
    DEBUG = enum.auto()
    INFO = enum.auto()
    SUCCESS = enum.auto()
    WARNING = enum.auto()
    ERROR = enum.auto()
    CRITICAL = enum.auto()


DEFAULT_LEVELS: Sequence["loguru.LevelConfig"] = [
    {"name": "ICECREAM", "no": 15, "color": "<magenta><bold>", "icon": "🍦"}
]


def add_level(
    name: str, no: int, color: str | None = None, icon: str | None = None
) -> None:
    """Add a new logging level to the logger.

    Args:
        name: The name of the new logging level.
        no: The numeric value of the new logging level.
        color: The color associated with the new logging level.
        icon: The icon associated with the new logging level.
    """
    with contextlib.suppress(ValueError):
        logger.level(name, no, color=color, icon=icon)
