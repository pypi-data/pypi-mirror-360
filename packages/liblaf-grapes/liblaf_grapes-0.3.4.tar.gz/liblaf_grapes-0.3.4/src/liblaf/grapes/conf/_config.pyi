from collections.abc import Mapping
from pathlib import Path
from typing import Any, overload

import environs

class Config:
    env: environs.Env

    def dump(self) -> Mapping[str, Any]: ...

    # region Fields

    @overload
    def bool(
        self, name: str, default: bool = ..., *, module: str = "", **kwargs
    ) -> bool: ...
    @overload
    def bool(
        self, name: str, default: None, *, module: str = "", **kwargs
    ) -> bool | None: ...
    @overload
    def cache_dir(
        self,
        name: str,
        default: Path = ...,
        *,
        ensure_exists: bool = True,
        module: str = "",
        **kwargs,
    ) -> Path: ...
    @overload
    def cache_dir(
        self,
        name: str,
        default: None,
        *,
        ensure_exists: bool = True,
        module: str = "",
        **kwargs,
    ) -> Path | None: ...
    @overload
    def dir(
        self,
        name: str,
        default: Path = ...,
        *,
        ensure_exists: bool = True,
        module: str = "",
        **kwargs,
    ) -> Path: ...
    @overload
    def dir(
        self,
        name: str,
        default: None,
        *,
        ensure_exists: bool = True,
        module: str = "",
        **kwargs,
    ) -> Path: ...
    @overload
    def file(
        self,
        name: str,
        default: Path = ...,
        *,
        module: str = "",
        **kwargs,
    ) -> Path: ...
    @overload
    def file(
        self,
        name: str,
        default: None,
        *,
        module: str = "",
        **kwargs,
    ) -> Path | None: ...
    @overload
    def path(
        self,
        name: str,
        default: Path = ...,
        *,
        module: str = "",
        **kwargs,
    ) -> Path: ...
    @overload
    def path(
        self,
        name: str,
        default: None,
        *,
        module: str = "",
        **kwargs,
    ) -> Path | None: ...

    # endregion Fields

config: Config
