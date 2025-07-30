from datetime import timedelta
import re

from .constants.time_related import (
    SECONDS_IN_DAY,
    SECONDS_IN_HOUR,
    SECONDS_IN_MINUTE,
    SECONDS_IN_MONTH,
)


def convert_to_seconds(time_str: str) -> int:
    """Convert a time string to seconds.

    Examples:
    --------
    >>> convert_to_seconds("1M 30m")
    2610000

    Notes:
    -----
    * ``M`` or ``mo`` denotes **months**.
    * ``m`` denotes **minutes**.
    """
    time_parts: list[tuple[str, str]] = re.findall(r"(\d+)\s*(M|mo|[dhms])", time_str)
    total_seconds = 0
    for value, unit in time_parts:
        if not value.isdigit():
            raise ValueError(f"Invalid time value: {value}")
        v = int(value)

        if unit == "M" or unit.lower() == "mo":
            total_seconds += v * SECONDS_IN_MONTH
        elif unit == "d":
            total_seconds += v * SECONDS_IN_DAY
        elif unit == "h":
            total_seconds += v * SECONDS_IN_HOUR
        elif unit == "m":
            total_seconds += v * SECONDS_IN_MINUTE
        elif unit == "s":
            total_seconds += v
        else:
            raise ValueError(f"Invalid time unit: {unit}")
    return total_seconds


def timedelta_to_seconds(td: timedelta) -> int:
    """Convert a timedelta object to seconds."""
    if not isinstance(td, timedelta):
        raise TypeError("Expected a timedelta object")
    return int(td.total_seconds())


def convert_to_milliseconds(time_str: str) -> int:
    return convert_to_seconds(time_str=time_str) * 1000


def milliseconds_to_time(milliseconds: int) -> str:
    """Convert milliseconds to a human-readable time string."""
    if milliseconds < 0:
        raise ValueError("Milliseconds cannot be negative")
    seconds = milliseconds // 1000
    return seconds_to_time(seconds=seconds)


def seconds_to_timedelta(seconds: int) -> timedelta:
    """Convert seconds to a timedelta object."""
    if seconds < 0:
        raise ValueError("Seconds cannot be negative")
    return timedelta(seconds=seconds)


def seconds_to_time(seconds: int) -> str:
    """Convert seconds to a human-readable time string.

    Months are represented with ``M`` while minutes use ``m``.
    """
    if seconds < 0:
        raise ValueError("Seconds cannot be negative")
    months, remainder = divmod(seconds, SECONDS_IN_MONTH)
    days, remainder = divmod(remainder, SECONDS_IN_DAY)
    hours, remainder = divmod(remainder, SECONDS_IN_HOUR)
    minutes, seconds = divmod(remainder, SECONDS_IN_MINUTE)
    time_parts: list[str] = []
    if months > 0:
        time_parts.append(f"{months}M")
    if days > 0:
        time_parts.append(f"{days}d")
    if hours > 0:
        time_parts.append(f"{hours}h")
    if minutes > 0:
        time_parts.append(f"{minutes}m")
    if seconds > 0:
        time_parts.append(f"{seconds}s")
    return " ".join(time_parts)
