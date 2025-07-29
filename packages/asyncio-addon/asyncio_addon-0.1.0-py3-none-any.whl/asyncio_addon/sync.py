import asyncio as aio
import threading
from collections.abc import Coroutine
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

T = TypeVar("T")


def run_sync(
    coroutine: Coroutine[Any, Any, T],
    *,
    timeout: float = 60,
) -> T:
    """
    Run a coroutine in sync, even if the async event loop is running.

    From <https://stackoverflow.com/a/78911765>, start a new thread so that we can create a new event loop.
    """

    def run_in_new_loop() -> T:
        new_loop = aio.new_event_loop()
        aio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coroutine)
        finally:
            new_loop.close()

    try:
        loop = aio.get_running_loop()
    except RuntimeError:
        return aio.run(coroutine)

    if threading.current_thread() is threading.main_thread():
        if not loop.is_running():
            return loop.run_until_complete(coroutine)
        else:
            with ThreadPoolExecutor() as pool:
                future = pool.submit(run_in_new_loop)
                return future.result(timeout=timeout)
    else:
        return aio.run_coroutine_threadsafe(coroutine, loop).result()


run_async = aio.to_thread
