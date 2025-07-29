from pathlib import Path
from types import FrameType
from typing import Literal

from loguru._get_frame import get_frame
from rich.style import Style
from rich.text import Text

from liblaf.grapes.typed import PathLike


def location(
    name: str | None,
    function: str | None,
    line: int | None,
    file: PathLike | None = None,
    *,
    enable_link: bool = True,
    style: Literal["long", "short"] = "long",
) -> Text:
    text = Text()
    file: Path | None = Path(file) if file is not None else None
    function = function or "<unknown>"
    line = line or 0
    if (style == "short") and (name is not None):
        name = name.split(".")[-1]
    if enable_link and file is not None and file.exists():
        text.append(
            f"{name}:{function}:{line}", style=Style(link=f"{file.as_uri()}#{line}")
        )
    else:
        text.append(f"{name}:{function}:{line}")
    return text


def caller_location(depth: int = 1, style: Literal["long", "short"] = "long") -> Text:
    frame: FrameType | None
    try:
        frame = get_frame(depth)
    except ValueError:
        frame = None
    file: str | None = None
    function: str | None = None
    line: int | None = None
    name: str | None = None
    if frame is not None:
        file = frame.f_code.co_filename
        function = frame.f_code.co_name
        line = frame.f_lineno
        name = frame.f_globals.get("__name__", "unknown")
    text: Text = location(
        function=function, line=line, name=name, file=file, style=style
    )
    return text
