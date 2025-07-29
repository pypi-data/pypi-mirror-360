import datetime
import types
import unittest.mock
from collections.abc import Generator, Sequence
from typing import Protocol, override

import attrs
import loguru
import wadler_lindig as wl
from rich.console import Console, RenderableType
from rich.highlighter import Highlighter, ReprHighlighter
from rich.text import Text
from rich.traceback import Traceback

from liblaf.grapes import pretty


class RichLoggingColumn(Protocol):
    def render(self, record: "loguru.Record") -> RenderableType: ...


@attrs.define
class LoguruRichHandler:
    console: Console = attrs.field(factory=lambda: pretty.get_console(stderr=True))
    columns: Sequence[RichLoggingColumn] = attrs.field(
        factory=lambda: [TimeColumn(), LevelColumn(), LocationColumn(), MessageColumn()]
    )

    def __call__(self, message: "loguru.Message") -> None:
        record: loguru.Record = message.record
        # TODO: `console.print()` is slow
        self.console.print(
            *self.render(record), overflow="ignore", no_wrap=True, crop=False
        )
        if (excpetion := self.render_exception(record)) is not None:
            self.console.print(excpetion)

    def render(self, record: "loguru.Record") -> Generator[RenderableType]:
        for column in self.columns:
            yield column.render(record)

    def render_exception(self, record: "loguru.Record") -> RenderableType | None:
        exception: loguru.RecordException | None = record["exception"]
        if exception is None:
            return None
        exc_type: type[BaseException] | None
        exc_value: BaseException | None
        traceback: types.TracebackType | None
        exc_type, exc_value, traceback = exception
        if exc_type is None or exc_value is None:
            return None

        # ? dirty hack to avoid long `repr()` output
        # ref: <https://github.com/Textualize/rich/discussions/3774>
        with unittest.mock.patch("rich.pretty.repr", new=wl.pformat):
            rich_tb: Traceback = Traceback.from_exception(
                exc_type=exc_type,
                exc_value=exc_value,
                traceback=traceback,
                width=self.console.width,
                code_width=self.console.width,
                show_locals=True,
            )

        # ? dirty hack to support ANSI in exception messages
        for stack in rich_tb.trace.stacks:
            if pretty.has_ansi(stack.exc_value):
                stack.exc_value = Text.from_ansi(stack.exc_value)  # pyright: ignore[reportAttributeAccessIssue]
        return rich_tb


class TimeColumn(RichLoggingColumn):
    @override
    def render(self, record: "loguru.Record") -> RenderableType:
        elapsed: datetime.timedelta = record["elapsed"]
        hh: int
        mm: int
        ss: int
        mm, ss = divmod(int(elapsed.total_seconds()), 60)
        hh, mm = divmod(mm, 60)
        return Text(
            f"{hh:02d}:{mm:02d}:{ss:02d}.{elapsed.microseconds:06d}", style="log.time"
        )


@attrs.define
class LevelColumn(RichLoggingColumn):
    @override
    def render(self, record: "loguru.Record") -> RenderableType:
        level: str = record["level"].name
        return Text(f"{level:<8}", style=f"logging.level.{level.lower()}")


@attrs.define
class LocationColumn(RichLoggingColumn):
    enable_link: bool = attrs.field(default=True)

    @override
    def render(self, record: "loguru.Record") -> RenderableType:
        location: Text = pretty.location(
            name=record["name"],
            function=record["function"],
            line=record["line"],
            file=record["file"].path,
            enable_link=self.enable_link,
        )
        location.style = "log.path"
        return location


@attrs.define
class MessageColumn(RichLoggingColumn):
    highlighter: Highlighter = attrs.field(factory=ReprHighlighter)

    @override
    def render(self, record: "loguru.Record") -> RenderableType:
        if (rich := record["extra"].get("rich")) is not None:
            return rich
        message: RenderableType = record["message"].strip()
        if "\x1b" in message:
            return Text.from_ansi(message)
        if record["extra"].get("markup", True):
            message = Text.from_markup(message)
        if highlighter := record["extra"].get("highlighter", self.highlighter):
            message = highlighter(message)
        return message
