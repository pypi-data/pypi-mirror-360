import re
import sys
from pathlib import Path

from environs import env
from typing_extensions import deprecated

from liblaf.grapes.typed import PathLike


@deprecated("Use `liblaf-cherries` instead.")
def project_root(
    start: Path | None = None, name: str | re.Pattern = r"\.git|src|playground"
) -> Path:
    if (root := env.path("PROJECT_ROOT", default=None)) and root.exists():
        return root
    if start is None:
        start = Path(sys.argv[0])
    start = start.absolute()
    path: Path = Path(start)
    if isinstance(name, str):
        name = re.compile(name)
    while name.match(path.name) is None:
        if path.parent == path:  # not found
            return start.parent
        path = path.parent
    return path.parent


@deprecated("Use `liblaf-cherries` instead.")
def resolve_project_path(
    relative: PathLike = ".",
    *,
    start: Path | None = None,
    name: str | re.Pattern = r"\.git|src|playground",
) -> Path:
    root: Path = project_root(start=start, name=name)
    return root / relative
