import re
from functools import lru_cache
from typing import Any, Iterable

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from arranges.segment import Segment, range_idx
from arranges.utils import inf, is_intlike, is_iterable, is_rangelike, try_hash


class Ranges(str):
    """
    A range set that can be hashed and converted to a string.
    """

    segments: tuple[Segment]

    def __init__(self, value: Any, stop: range_idx | None = None):
        """
        Construct a new string with the canonical form of the range.
        """
        self.segments = self.from_str(self)

    def __new__(cls, value: Any, stop: range_idx | None = None) -> str:
        """
        Construct a new string with the canonical form of the range.

        This becomes "self" in __init__, so we're always a string
        """
        val = cls.construct_str(value, stop)
        return str.__new__(cls, val)

    @classmethod
    def construct_str(cls, value, stop) -> str:
        """
        Create a string representation of a range series
        """
        start_and_stop = value is not None and stop is not None
        stop_only = value is None and stop is not None

        if start_and_stop or stop_only:
            return Segment(value, stop)

        if value is None:
            return ""

        if is_intlike(value):
            return Segment(0, value)

        if is_rangelike(value):
            if not value.step or value.step == 1:
                return Segment(value.start, value.stop)
            else:
                stepped_range = list(value)
                return cls.iterable_to_str(stepped_range)

        if hasattr(value, "segments"):
            return ",".join(value.segments)

        if isinstance(value, str):
            normalized = cls.from_str(value)
            return ",".join(str(v) for v in normalized)

        if is_iterable(value):
            return cls.iterable_to_str(value)

        raise TypeError(f"Cannot convert {value} into {cls.__name__}")

    @staticmethod
    def split_str(value: str) -> list[str]:
        return re.split(r",|;", value)

    @classmethod
    def from_str(cls, value: str) -> tuple[Segment]:
        """
        Construct from a string.
        """
        ret = []

        for s in cls.split_str(value):
            ret.append(Segment.from_str(s))

        cacheable = tuple(set(ret))

        return cls.from_hashable_iterable(cacheable)

    @classmethod
    def iterable_to_str(cls, iterable: Iterable) -> str:
        """
        Convert an iterable of ranges to a string
        """
        hashable = tuple(iterable)
        # contents might not be hashable
        if try_hash(hashable):
            vals = cls.from_hashable_iterable(hashable)
        else:
            vals = cls.from_iterable(hashable)

        return ",".join(str(v) for v in vals)

    @classmethod
    @lru_cache
    def from_hashable_iterable(cls, value: tuple[Any]) -> tuple[Segment]:
        """
        Cache the result of from_iterable
        """
        return cls.from_iterable(value)

    @staticmethod
    def _flatten(iterable: Iterable) -> Iterable[Segment]:
        """
        Flatten into RangeSegments
        """
        for item in iterable:
            if isinstance(item, Segment):
                yield item
            if isinstance(item, Ranges):
                yield from item.segments
            elif isinstance(item, str):
                if item:
                    yield from [Segment.from_str(s) for s in Ranges.split_str(item)]
            elif is_iterable(item):
                yield from Ranges._flatten(item)
            elif is_intlike(item):
                yield Segment(item, item + 1)
            else:
                yield from Ranges(item).segments

    @classmethod
    def from_iterable(cls, iterable: Iterable) -> tuple[Segment]:
        """
        Sort and merge a list of ranges.
        """
        segments: list[Segment] = []
        segments.extend(cls._flatten(iterable))
        segments.sort(key=Segment.sort_key)

        i = 1

        while i < len(segments):
            current = segments[i]
            last = segments[i - 1]
            if last.isconnected(current):
                segments[i - 1] = current | last
                del segments[i]
                i -= 1
            i += 1

        return tuple(segments)

    def __hash__(self):
        """
        The hash of the string (which is what these things are)
        """
        return super().__hash__()

    def __len__(self) -> int:
        """
        Get the total length of all ranges
        """
        return sum(len(segment) for segment in self.segments)

    def __bool__(self) -> bool:
        """
        True if this range has any elements
        """
        return any(bool(segment) for segment in self.segments)

    def __add__(self, other):
        s = self.iterable_to_str((self, other))
        return Ranges(s)

    def __eq__(self, other: Any) -> bool:
        """
        Compare the two lists based on their string representations
        """
        if not isinstance(other, Ranges):
            # hack: bypass external constructor, use nested iterable
            # otherwise we risk doing Ranges(int).
            # todo: break _flatten out and separate internal and external
            # constructors,
            other = Ranges((other,))
        return super().__eq__(other)

    def __contains__(self, other: Any) -> bool:
        """
        Are all of the other ranges in our ranges?
        """
        combined = str(self + other)

        return self and (combined == self)

    def __iter__(self):
        """
        Iterate over the values in our ranges.

        Note that this could be boundless.
        """
        for r in self.segments:
            for i in r:
                yield i

    def intersects(self, other: Any) -> bool:
        """
        True if this range overlaps with the other range
        """
        other: Ranges = Ranges(other)
        for r in self.segments:
            for o in other.segments:
                if r.intersects(o):
                    return True

        return False

    def union(self, other) -> "Ranges":
        """
        Return the union of this range and the other
        """
        return Ranges(self + other)

    def __or__(self, other: "Ranges") -> "Ranges":
        """
        Return the union of this range and the other
        """
        return self.union(other)

    def __and__(self, other: "Ranges") -> "Ranges":
        """
        Return the intersection of this range and the other
        """
        # Create a sorted list of all the boundary points from both ranges.
        boundary_points = sorted(
            set(
                [s.start for s in self.segments]
                + [s.stop for s in self.segments]
                + [s.start for s in other.segments]
                + [s.stop for s in other.segments]
            )
        )

        # Use these boundary points to find intersecting segments.
        intersected_segments = []
        for i in range(len(boundary_points) - 1):
            start, end = boundary_points[i], boundary_points[i + 1]
            new_seg = Segment(start, end)
            if new_seg in self and new_seg in other:
                intersected_segments.append(new_seg)

        return Ranges(intersected_segments)

    def __le__(self, other: "Ranges") -> bool:
        """
        Subset operator (<=): True if self is a subset of other
        """
        return self in other

    def __lt__(self, other: "Ranges") -> bool:
        """
        Proper subset operator (<): True if self is a proper subset of other
        """
        return self in other and self != other

    def __ge__(self, other: "Ranges") -> bool:
        """
        Superset operator (>=): True if self is a superset of other
        """
        return other in self

    def __gt__(self, other: "Ranges") -> bool:
        """
        Proper superset operator (>): True if self is a proper superset of other
        """
        return other in self and self != other

    def __sub__(self, other: "Ranges") -> "Ranges":
        """
        Relative complement operator (-): Return elements in self that are not in other
        """
        if not isinstance(other, Ranges):
            other = Ranges(other)

        return self & ~other

    def __invert__(self):
        """
        The inverse of this range
        """
        if not self:
            return Ranges(":")

        segments = []

        if self.first > 0:
            segments.append(Segment(0, self.first))

        for i in range(len(self.segments)):
            if i == len(self.segments) - 1:
                segments.append(Segment(self.segments[i].stop, inf))
            else:
                segments.append(
                    Segment(self.segments[i].stop, self.segments[i + 1].start)
                )

        return Ranges(segments)

    @classmethod
    def validate(cls, value: Any) -> "Ranges":
        """
        Validate a value and convert it to a Range
        """
        if isinstance(value, cls):
            return value

        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """
        For automatic validation in pydantic
        """
        return core_schema.no_info_after_validator_function(cls, handler(Any))

    @property
    def first(self):
        """
        The start value of the first segment
        """
        return self.segments[0].start

    @property
    def last(self):
        """
        The last value of the final segment
        """
        return self.segments[-1].last
