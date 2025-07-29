# asyncio-addon

[![PyPI version](https://badge.fury.io/py/asyncio-addon.svg)](https://badge.fury.io/py/asyncio-addon)
[![Python versions](https://img.shields.io/pypi/pyversions/asyncio-addon.svg)](https://pypi.org/project/asyncio-addon/)

Some convenient utilities for asyncio.

Utilities include:

- [`@async_main`](src/asyncio_addon/decorator.py): A decorator to run an async function as the main entry point.
- [`run_async`](src/asyncio_addon/sync.py): Run a coroutine in sync, even if the async event loop is running.
- [`run_sync`](src/asyncio_addon/sync.py): An alias of `asyncio.to_thread`. Run a coroutine in a separate thread, blocking until it's done.
- [`SemGroup`](src/asyncio_addon/task_group.py): A task group with a semaphore, allowing limited concurrency.
- [`gather`](src/asyncio_addon/task_group.py): A better `asyncio.gather` that supports limited concurrency and exception handling.
- [`gather_all`](src/asyncio_addon/task_group.py): A variant of `gather` that returns all results, including exceptions, without raising them.
