from pathlib import Path
from typing import Unpack

import loguru

from liblaf.grapes.conf import config
from liblaf.grapes.logging.filters import make_filter


def file_handler(
    **kwargs: Unpack["loguru.FileHandlerConfig"],
) -> "loguru.FileHandlerConfig":
    kwargs.setdefault("sink", config.file("LOGGING_FILE", Path("run.log")))
    kwargs["filter"] = make_filter(kwargs.get("filter"))
    kwargs.setdefault("mode", "w")
    return kwargs
