import functools
import sys
from typing import IO, Literal, TypedDict, Unpack

import rich
from environs import env
from rich.console import Console
from rich.style import Style
from rich.theme import Theme

from liblaf.grapes import path
from liblaf.grapes.typed import PathLike


def theme() -> Theme:
    return Theme(
        {
            "logging.level.notset": Style(dim=True),
            "logging.level.trace": Style(color="cyan", bold=True),
            "logging.level.debug": Style(color="blue", bold=True),
            "logging.level.icecream": Style(color="magenta", bold=True),
            "logging.level.info": Style(bold=True),
            "logging.level.success": Style(color="green", bold=True),
            "logging.level.warning": Style(color="yellow", bold=True),
            "logging.level.error": Style(color="red", bold=True),
            "logging.level.critical": Style(color="red", bold=True, reverse=True),
        },
        inherit=True,
    )


class ConsoleKwargs(TypedDict, total=False):
    theme: Theme | None
    stderr: bool | None
    file: IO | PathLike | None
    width: int | None


@functools.cache
def get_console(**kwargs: Unpack[ConsoleKwargs]) -> Console:
    kwargs.setdefault("theme", theme())
    file: IO | PathLike | None = kwargs.get("file")
    if _is_stdout(**kwargs):
        kwargs = _ci(**kwargs)
        rich.reconfigure(**kwargs)
        return rich.get_console()
    if _is_stderr(**kwargs):
        kwargs = _ci(**kwargs)
        kwargs.pop("file", None)
        kwargs["stderr"] = True
        return Console(**kwargs)  # pyright: ignore[reportArgumentType]
    if path.is_path_like(file):
        kwargs["file"] = path.as_path(file).open("w")
    return Console(**kwargs)  # pyright: ignore[reportArgumentType]


def _is_stdout(**kwargs: Unpack[ConsoleKwargs]) -> bool:
    file: IO | PathLike | None = kwargs.get("file")
    return (
        (file is None and not kwargs.get("stderr", False))
        or (file in ("stdout", "<stdout>", sys.stdout))
        or getattr(file, "name", None) in ("stdout", "<stdout>")
    )


def _is_stderr(**kwargs: Unpack[ConsoleKwargs]) -> bool:
    file: IO | PathLike | None = kwargs.get("file")
    return (
        (file is None and kwargs.get("stderr", False))
        or (file in ("stderr", "<stderr>", sys.stderr))
        or getattr(file, "name", None) in ("stderr", "<stderr>")
    )


def _ci(**kwargs: Unpack[ConsoleKwargs]) -> ConsoleKwargs:
    if not env.bool("GITHUB_ACTIONS", False):
        return kwargs
    kwargs.setdefault("width", 128)
    return kwargs


def force_terminal(file: Literal["stdout", "stderr"] | IO | PathLike) -> bool | None:
    """...

    References:
        1. <https://force-color.org/>
        2. <https://no-color.org/>
    """
    if file not in ("stdout", "stderr"):
        return None
    if env.bool("FORCE_COLOR", None):
        return True
    if env.bool("NO_COLOR", None):
        return False
    if env.bool("GITHUB_ACTIONS", None):
        return True
    return None
