import asyncio
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")


def run_async(func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any) -> T:
    """Run an async function synchronously, blocking the event loop until it completes."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(func(*args, **kwargs))
