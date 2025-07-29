import asyncio as aio
import contextlib
from collections.abc import AsyncGenerator, Coroutine, Iterable, Sequence
from dataclasses import dataclass
from typing import Any, Literal, Self, TypeVar, overload

T = TypeVar("T")


@dataclass(frozen=True)
class SemGroup:
    """TaskGroup with semaphore support."""

    tg: aio.TaskGroup
    sem: aio.Semaphore | None

    @classmethod
    @contextlib.asynccontextmanager
    async def create(
        cls,
        *,
        concurrency: int | None = None,
    ) -> AsyncGenerator[Self, None]:
        sem = aio.Semaphore(concurrency) if concurrency else None
        async with aio.TaskGroup() as tg:
            yield cls(tg=tg, sem=sem)

    def create_task(self, coro: Coroutine[Any, Any, T]) -> aio.Task[T]:
        async def wrapper() -> T:
            if not self.sem:
                return await coro

            async with self.sem:
                return await coro

        return self.tg.create_task(wrapper())


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
    """A better `asyncio.gather`"""

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
