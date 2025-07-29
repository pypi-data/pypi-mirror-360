"""
Some quacky type helpers so we don't have to use isinstance everywhere
"""

import math
import sys
from typing import Any, Type, TypeVar

T = TypeVar("T")


class _Boundless(float):
    """
    A class that represents a boundless end of a range
    """

    huge = sys.maxsize
    """
    An enormous number that's used as a stand-in for infinity
    """

    def __eq__(self, other) -> bool:
        """
        Is this boundless?
        """
        return other == math.inf or other == self.huge

    def __index__(self) -> int:
        """
        When used as an index, return a huge integer rather than infinity.

        This is necessary because CPython doesn't allow lengths larger than
        sys.maxsize, and Python has no way to represent infinity as an integer.
        """
        return self.huge

    def __hash__(self) -> int:
        """
        Make this hashable so it can be used in sets
        """
        return hash(float(math.inf))


inf = _Boundless(math.inf)
"""
A boundless end of a range. When used as a stop value it's infinite, but when
used as a length it's the largest index integer possible in cpython.
"""


def to_int(value: str, default: int) -> int:
    """
    Convert a string to an integer. If the string is empty, return the default
    """
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        if "0x" in value:
            return int(value, 16)
        elif "0o" in value:
            return int(value, 8)
        elif "0b" in value:
            return int(value, 2)
        elif value in ("inf", "end"):
            return inf
        elif value == "start":
            return 0
        else:
            raise ValueError(f"Invalid integer value {value}")


def is_rangelike(obj: Any) -> bool:
    """
    Check if a value is a range-like object
    """
    return all(hasattr(obj, attr) for attr in ("start", "stop", "step"))


def is_intlike(value: Any) -> bool:
    """
    Can this object be converted to an integer?
    """
    return hasattr(value, "__int__")


def is_iterable(value: Any) -> bool:
    """
    Is this object iterable?
    """
    return hasattr(value, "__iter__")


def as_type(cls: Type[T], value: Any) -> T:
    """
    Convert a value to a type, if necessary.

    Saves a bit of construction time if the value is already the right type.
    """
    if isinstance(value, cls):
        return value
    return cls(value)


def try_hash(obj: Any) -> int | None:
    """
    Try to hash an object. If it can't be hashed, return None
    """
    try:
        return hash(obj)
    except TypeError:
        return None
