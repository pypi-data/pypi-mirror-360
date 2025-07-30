import asyncio
import functools


def run_in_executor(func=None, *, context=None, executor=None):
    """
    Decorator to run synchronous function in the given or default executor

    Optionally within the given async context manager (e.g. to limit concurrency
    with `asyncio.Lock` or `asyncio.Semaphore`)
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Use dummy Lock() as contextlib.nullcontext for older python versions
            current_context = context or asyncio.Lock()

            loop = asyncio.get_running_loop()
            async with current_context:
                return await loop.run_in_executor(
                    executor, lambda: func(*args, **kwargs)
                )

        return wrapper

    return decorator(func) if func else decorator


run_in_executor_locked = functools.partial(run_in_executor, context=asyncio.Lock())
