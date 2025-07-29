# asyncio-addon

[![PyPI version](https://badge.fury.io/py/asyncio-addon.svg)](https://badge.fury.io/py/asyncio-addon)
[![Python versions](https://img.shields.io/pypi/pyversions/asyncio-addon.svg)](https://pypi.org/project/asyncio-addon/)

Some convenient utilities for asyncio.

Utilities include:

- [`@async_main`](src/asyncio_addon/decorator.py): A decorator to run an async function as the main entry point.
- [`run_sync`](src/asyncio_addon/sync.py): Run a coroutine in sync, even if the async event loop is running.
- [`run_async`](src/asyncio_addon/sync.py): An alias of `asyncio.to_thread`. Run a sync function in a separate thread.
- [`SemGroup`](src/asyncio_addon/task_group.py): A task group with a semaphore, allowing limited concurrency.
- [`gather_all`](src/asyncio_addon/task.py): Enhanced version of `asyncio.gather` with concurrency control and improved error handling.
