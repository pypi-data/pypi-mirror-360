from collections.abc import Coroutine, Iterable, Sequence
from typing import Any, Literal, TypeVar, overload

from .task_group import SemGroup

T = TypeVar("T")


@overload
async def gather_all(
    coros: Iterable[Coroutine[Any, Any, T]],
    *,
    concurrency: int | None = None,
    return_exceptions: Literal[True],
) -> Sequence[T | BaseException]: ...


@overload
async def gather_all(
    coros: Iterable[Coroutine[Any, Any, T]],
    *,
    concurrency: int | None = None,
    return_exceptions: Literal[False] = ...,
) -> Sequence[T]: ...


@overload
async def gather_all(
    *coro: Coroutine[Any, Any, T],
    concurrency: int | None = ...,
    return_exceptions: Literal[True] = ...,
) -> Sequence[T | BaseException]: ...


@overload
async def gather_all(
    *coro: Coroutine[Any, Any, T],
    concurrency: int | None = ...,
    return_exceptions: Literal[False] = ...,
) -> Sequence[T]: ...


async def gather_all(
    coros: Iterable[Coroutine[Any, Any, T]] | Coroutine[Any, Any, T],
    *coro: Coroutine[Any, Any, T],
    concurrency: int | None = None,
    return_exceptions: bool = False,
) -> Sequence[T | BaseException]:
    """Enhanced version of asyncio.gather with concurrency control.

    Executes multiple coroutines concurrently with optional concurrency limiting
    and improved error handling. Unlike asyncio.gather, this function allows you
    to control the maximum number of concurrent tasks.

    Args:
        *coro: Additional coroutines to execute (can be iterable or variadic arguments).
        concurrency: Maximum number of concurrent tasks. If None, all tasks
            run concurrently without limit. Defaults to None.
        return_exceptions: If True, exceptions are returned as results instead
            of being raised. If False, the first exception encountered will
            be raised. Defaults to False.

    Returns:
        A sequence containing the results of all coroutines. If return_exceptions
        is True, both successful results and exceptions are included. If False,
        only successful results are returned (exceptions are raised).

    Raises:
        Exception: Any exception from the coroutines if return_exceptions is False.

    Examples:
        Basic usage with multiple coroutines:

        >>> async def fetch_data(url):
        ...     # Simulate async operation
        ...     await asyncio.sleep(1)
        ...     return f"Data from {url}"

        >>> async def main():
        ...     urls = ["url1", "url2", "url3"]
        ...     coros = [fetch_data(url) for url in urls]
        ...     results = await gather_all(coros)
        ...     print(results)

        With concurrency control:

        >>> async def main():
        ...     # Limit to 2 concurrent requests
        ...     results = await gather_all(
        ...         (fetch_data(f"url{i}") for i in range(10)),
        ...         concurrency=2
        ...     )

        With exception handling:

        >>> async def may_fail(x):
        ...     if x % 2 == 0:
        ...         raise ValueError(f"Error with {x}")
        ...     return x * 2

        >>> async def main():
        ...     results = await gather_all(
        ...         [may_fail(i) for i in range(5)],
        ...         return_exceptions=True
        ...     )
        ...     # Results will contain both values and exceptions

        Using variadic arguments:

        >>> async def main():
        ...     result = await gather_all(
        ...         fetch_data("url1"),
        ...         fetch_data("url2"),
        ...         fetch_data("url3"),
        ...         concurrency=2
        ...     )
    """

    async def task(coro: Coroutine[Any, Any, T]) -> T | BaseException:
        if not return_exceptions:
            return await coro

        try:
            return await coro
        except Exception as e:
            return e

    coros = [coros] if isinstance(coros, Coroutine) else list(coros)
    coros = [*coros, *coro]

    async with SemGroup.create(concurrency=concurrency) as tg:
        tasks = [tg.create_task(task(coro)) for coro in coros]
    return [task.result() for task in tasks]
