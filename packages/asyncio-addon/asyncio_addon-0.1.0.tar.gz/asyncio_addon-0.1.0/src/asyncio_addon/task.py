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


async def gather_all(
    coros: Iterable[Coroutine[Any, Any, T]],
    *,
    concurrency: int | None = None,
    return_exceptions: bool = False,
) -> Sequence[T | BaseException]:
    """Just a better `asyncio.gather`"""

    async def task(coro: Coroutine[Any, Any, T]) -> T | BaseException:
        if not return_exceptions:
            return await coro

        try:
            return await coro
        except Exception as e:
            return e

    async with SemGroup.create(concurrency=concurrency) as tg:
        tasks = [tg.create_task(task(coro)) for coro in coros]
    return [task.result() for task in tasks]


async def gather(*coros: Coroutine[Any, Any, T]) -> Sequence[T]:
    return await gather_all(coros, return_exceptions=False)
