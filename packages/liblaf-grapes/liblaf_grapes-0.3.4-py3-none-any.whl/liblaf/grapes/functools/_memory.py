import datetime
import functools
from collections.abc import Callable
from typing import Any, Protocol, TypedDict, Unpack, overload

import joblib
import platformdirs


class MemorizedFunc[**P, T](Protocol):
    @property
    def memory(self) -> joblib.Memory: ...
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T: ...


class CacheKwargs(TypedDict, total=False):
    pass


class ReduceSizeKwargs(TypedDict, total=False):
    bytes_limit: int | str | None
    items_limit: int | None
    age_limit: datetime.timedelta | None


@overload
def cache[**P, T](
    *,
    memory: joblib.Memory | None = None,
    reduce_size: ReduceSizeKwargs | None = None,
    **kwargs: Unpack[CacheKwargs],
) -> Callable[[Callable[P, T]], MemorizedFunc[P, T]]: ...
@overload
def cache[**P, T](
    func: Callable[P, T],
    /,
    *,
    memory: joblib.Memory | None = None,
    reduce_size: ReduceSizeKwargs | None = None,
    **kwargs: Unpack[CacheKwargs],
) -> MemorizedFunc[P, T]: ...
def cache[**P, T](
    func: Callable[P, T] | None = None,
    /,
    *,
    memory: joblib.Memory | None = None,
    reduce_size: ReduceSizeKwargs | None = None,
    **kwargs: Unpack[CacheKwargs],
) -> Any:
    if func is None:
        return functools.partial(
            cache, memory=memory, reduce_size=reduce_size, **kwargs
        )
    if memory is None:
        memory = joblib.Memory(platformdirs.user_cache_path("joblib"))
    if reduce_size is None:
        reduce_size = {"bytes_limit": "1G"}

    @memory.cache(**kwargs)
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        ret: T = func(*args, **kwargs)
        memory.reduce_size(**reduce_size)
        return ret

    wrapper.memory = memory  # pyright: ignore[reportAttributeAccessIssue]
    return wrapper
