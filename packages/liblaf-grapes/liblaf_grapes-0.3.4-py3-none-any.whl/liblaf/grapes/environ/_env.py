import functools
from pathlib import Path

from environs import Env


@functools.lru_cache
def init_env(path: str | Path | None = ".env", prefix: str | None = None) -> Env:
    env = Env(prefix=prefix)
    env.read_env(path)
    return env
