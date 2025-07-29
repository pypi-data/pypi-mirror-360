from pathlib import Path
from typing import Unpack

import loguru

from liblaf.grapes.conf import config
from liblaf.grapes.logging.filters import make_filter


def jsonl_handler(
    **kwargs: Unpack["loguru.FileHandlerConfig"],
) -> "loguru.FileHandlerConfig":
    kwargs.setdefault("sink", config.file("LOGGING_JSONL", Path("run.log.jsonl")))
    kwargs["filter"] = make_filter(kwargs.get("filter"))
    kwargs.setdefault("serialize", True)
    kwargs.setdefault("mode", "w")
    return kwargs
