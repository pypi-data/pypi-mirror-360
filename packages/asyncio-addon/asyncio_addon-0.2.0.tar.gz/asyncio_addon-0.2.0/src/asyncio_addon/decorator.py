import asyncio as aio
from collections.abc import Callable, Coroutine
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def async_main(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, R]:
    """
    Decorator that use `asyncio.run` to run the function.

    Usage:

    ```python
    from asyncio_addon import async_main

    @async_main()
    async def main(): ...

    if __name__ == "__main__":
        main() # `main` is run with `asyncio.run` here
    ```
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return aio.run(func(*args, **kwargs))

    return wrapper
