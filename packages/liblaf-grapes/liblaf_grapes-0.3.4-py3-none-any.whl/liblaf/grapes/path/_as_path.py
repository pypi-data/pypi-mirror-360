import os
from pathlib import Path
from typing import Any

from typing_extensions import TypeIs

from liblaf.grapes.typed import PathLike


def as_path(path: PathLike, *, expend_user: bool = True) -> Path:
    path = Path(path)
    if expend_user:
        path = path.expanduser()
    return path


def is_path_like(obj: Any) -> TypeIs[PathLike]:
    return isinstance(obj, (str, os.PathLike))
