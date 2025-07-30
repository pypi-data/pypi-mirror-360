import asyncio
import time
import tracemalloc
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager, contextmanager
from functools import wraps
from typing import Any, TypeVar

from psutil import virtual_memory
from pyinstrument import Profiler

from .print_utils import print_style_time

__all__ = ["resource_profiler", "resource_profiler_async_ctx", "resource_profiler_ctx", "performance_async"]

T = TypeVar("T")


def performance_async(f: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    @wraps(f)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.time()
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            start_trace = True
        else:
            start_trace = False
        memory_before = virtual_memory()
        result = await f(*args, **kwargs)
        if start_trace:
            tracemalloc.stop()

        process_name = f"{args[0].__class__.__name__}-{f.__name__}"
        print_style_time(f"{process_name}: {time.time() - start}, mem total: {memory_before.total / 2**30} Gb, ")

        return result

    return wrapper


def resource_profiler(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    # Usage as a decorator
    @resource_profiler
    async def my_function():
        # Your code here
        pass

    @resource_profiler
    def my_function():
        # Your code here
        pass
    """

    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        profiler = Profiler()
        try:
            profiler.start()
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        finally:
            profiler.stop()
            print(profiler.output_text(unicode=True, color=True))

    return wrapper


@asynccontextmanager
async def resource_profiler_async_ctx(is_disabled: bool = False) -> Any:
    """
    Usage:
    async with resource_profiler_ctx():
        # Your code here
        pass
    """
    if is_disabled:
        yield
        return

    profiler = Profiler()
    try:
        profiler.start()
        yield
    finally:
        profiler.stop()
        print(profiler.output_text(unicode=True, color=True))


@contextmanager
def resource_profiler_ctx() -> Any:
    """
    Usage for sync context:
    with resource_profiler_sync_ctx():
        # Your sync code here
        pass
    """
    profiler = Profiler()
    try:
        profiler.start()
        yield
    finally:
        profiler.stop()
        print(profiler.output_text(unicode=True, color=True))
