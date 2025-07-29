import asyncio as aio
import contextlib
from collections.abc import AsyncGenerator, Coroutine
from dataclasses import dataclass
from typing import Any, Self, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class SemGroup:
    """TaskGroup with semaphore support."""

    tg: aio.TaskGroup
    sem: aio.Semaphore | None

    @classmethod
    @contextlib.asynccontextmanager
    async def create(
        cls, *, concurrency: int | None = None
    ) -> AsyncGenerator[Self, None]:
        sem = aio.Semaphore(concurrency) if concurrency else None
        async with aio.TaskGroup() as tg:
            yield cls(tg=tg, sem=sem)

    def create_task(
        self,
        coro: Coroutine[Any, Any, T],
        *,
        timeout: float | None = None,
    ) -> aio.Task[T]:
        async def wrapper() -> T:
            coro_task = aio.wait_for(coro, timeout)

            if not self.sem:
                return await coro_task

            async with self.sem:
                return await coro_task

        return self.tg.create_task(wrapper())
