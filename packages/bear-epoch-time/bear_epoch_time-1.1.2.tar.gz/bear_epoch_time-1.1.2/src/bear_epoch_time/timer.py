"""Tools related to timers and performance measurement."""

from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import asynccontextmanager, contextmanager
from functools import wraps
from time import perf_counter
from typing import Any


def create_timer(**defaults) -> Callable:
    """A way to set defaults for a frequently used timer decorator."""

    def timer_decorator(func: Callable) -> Any:
        """Decorator to time the execution of a function."""

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            defaults["name"] = func.__name__
            with timer(**defaults):
                return func(*args, **kwargs)

        return wrapper

    return timer_decorator


def create_async_timer(**defaults) -> Callable:
    """Set defaults for an async timer decorator."""

    def timer_decorator(func: Callable) -> Any:
        """Decorator to time the execution of an async function."""

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            """Async wrapper to time the execution of an async function."""
            defaults["name"] = func.__name__
            async with async_timer(**defaults):
                return await func(*args, **kwargs)

        return wrapper

    return timer_decorator


@contextmanager
def timer(**kwargs) -> Generator["TimerData"]:
    """Context manager to time the execution of a block of code."""
    data: TimerData = kwargs.get("data") or TimerData(**kwargs)
    data.start()
    try:
        yield data
    finally:
        data.stop()


@asynccontextmanager
async def async_timer(**kwargs) -> AsyncGenerator["TimerData"]:
    """Async context manager to time the execution of an async block of code."""
    data: TimerData = kwargs.get("data") or TimerData(**kwargs)
    data.start()
    try:
        yield data
    finally:
        data.stop()


class TimerData:
    """Container for timing information."""

    def __init__(self, name: str, console: bool = False, callback: Callable | None = None, **kwargs) -> None:
        """Initialize the timer data.

        Args:
            name (str): The name of the timer.
            console (bool): Indicates whether to log to the console.
            callback (Callable | None): A callable to invoke when the timer stops.
            **kwargs: Optional keyword arguments.
                ``print_function`` is the function used to print logs.
        """
        self.name: str = name
        self.console: bool = console
        self.callback: Callable | None = callback
        self.print_func: Callable = kwargs.get("print_function", print)
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self._raw_elapsed_time: float = 0.0

    def start(self) -> None:
        """Record the starting time using ``perf_counter``."""
        self.start_time = perf_counter()

    def send_callback(self) -> None:
        """Invoke the callback if one was provided."""
        if self.callback is not None:
            self.callback(self)

    def stop(self) -> None:
        """Stop the timer and optionally log the result."""
        self.end_time = perf_counter()
        self._raw_elapsed_time = self.end_time - self.start_time
        if self.callback:
            self.send_callback()
        if self.console:
            self.print_func(f"[{self.name}] Elapsed time: {self.elapsed_seconds:.6f} seconds")

    @property
    def elapsed_milliseconds(self) -> float:
        """Return the elapsed time in milliseconds."""
        if self._raw_elapsed_time:
            return self._raw_elapsed_time * 1000
        return -1.0

    @property
    def elapsed_seconds(self) -> float:
        """Return the elapsed time in seconds."""
        if self._raw_elapsed_time:
            return self._raw_elapsed_time
        return -1.0


__all__ = ["TimerData", "timer"]
