from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import environs
import platformdirs


class Config:
    env: environs.Env

    def __init__(self) -> None:
        self.env = environs.Env()
        self.env.read_env()

    def dump(self) -> Mapping[str, Any]:
        return self.env.dump()

    def _field_name(self, name: str, module: str = "") -> str:
        parts: list[str] = _remove_private_prefix(module)
        parts.append(name)
        return "_".join(parts).upper()

    # region Fields

    def bool(
        self,
        name: str,
        default: bool = ...,  # pyright: ignore[reportArgumentType]
        *,
        module: str = "",
        **kwargs,
    ) -> bool:
        name: str = self._field_name(name, module)
        value: bool = self.env.bool(name, default=default, **kwargs)
        return value

    def cache_dir(
        self,
        name: str,
        default: Path = ...,  # pyright: ignore[reportArgumentType]
        *,
        ensure_exists: bool = True,
        module: str = "",
        **kwargs,
    ) -> Path:
        if default is Ellipsis:
            default = platformdirs.user_cache_path(
                "/".join(_remove_private_prefix(module))
            )
        return self.dir(
            name, default=default, ensure_exists=ensure_exists, module=module, **kwargs
        )

    def dir(
        self,
        name: str,
        default: Path | None = ...,  # pyright: ignore[reportArgumentType]
        *,
        ensure_exists: bool = True,
        module: str = "",
        **kwargs,
    ) -> Path:
        value: Path = self.path(name, default=default, module=module, **kwargs)
        if ensure_exists:
            value.mkdir(parents=True, exist_ok=True)
        return value

    def file(
        self,
        name: str,
        default: Path | None = ...,  # pyright: ignore[reportArgumentType]
        *,
        module: str = "",
        **kwargs,
    ) -> Path:
        value: Path = self.path(name, default=default, module=module, **kwargs)
        return value

    def path(
        self,
        name: str,
        default: Path | None = ...,  # pyright: ignore[reportArgumentType]
        *,
        module: str = "",
        **kwargs,
    ) -> Path:
        name: str = self._field_name(name, module)
        value: Path = self.env.path(name, default=default, **kwargs)
        return value

    # endregion Fields


def _remove_private_prefix(
    s: str, /, sep: str | None = ".", prefix: str = "_"
) -> list[str]:
    parts: list[str] = s.split(sep)
    parts = [part for part in parts if part and not part.startswith(prefix)]
    return parts


config = Config()
