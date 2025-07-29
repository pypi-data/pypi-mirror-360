import re
from functools import lru_cache
from typing import Any

from arranges.utils import as_type, inf, is_intlike, is_iterable, is_rangelike, to_int

range_idx = int | float


def fix_start_stop(start: range_idx, stop: range_idx) -> tuple[range_idx, range_idx]:
    start = 0 if start is None else (int(start) if start != inf else inf)
    stop = inf if stop in (None, inf) else int(stop)

    if start > stop:
        raise ValueError(f"Stop ({stop}) can't be before start ({start})")

    if start < 0 or stop < 0:
        raise ValueError("Can't have a range with negative values")

    return start, stop


def start_stop_to_str(start: range_idx, stop: range_idx) -> str:
    """
    Returns a string representation of a range from start to stop.
    """
    start, stop = fix_start_stop(start, stop)

    if start == stop:
        return ""

    if stop == start + 1:
        return str(int(start))

    start_str = str(int(start)) if start else ""
    stop_str = str(int(stop)) if stop is not inf else ""

    return f"{start_str}:{stop_str}"


class Segment(str):
    """
    A single range segment that's a string and can be hashed.
    """

    start: int = 0
    stop: int = inf
    step: int = 1

    def __init__(self, start: range_idx, stop: range_idx = None):
        """
        Construct a new string with the canonical form of the range.
        """
        self.start, self.stop = fix_start_stop(start, stop)

    def __new__(cls, start: range_idx, stop: range_idx = None) -> str:
        """
        Construct a new string with the canonical form of the range.
        """
        return str.__new__(cls, start_stop_to_str(start, stop))

    def __hash__(self):
        return hash(str(self))

    def __or__(self, other: "Segment") -> "Segment":
        """
        Return the union of this range and the other range
        """
        if not other:
            return self

        if not self:
            return other

        if not self.isconnected(other):
            raise ValueError(f"{self} and {other} aren't touching")

        start = min(self.start, other.start)
        stop = max(self.stop, other.stop)

        return Segment(start, stop)

    def __iter__(self):
        """
        Iterate over the values in this range
        """
        i = self.start
        while i < self.stop:
            yield i
            i += 1

    def __len__(self) -> int:
        """
        Get the length of this range
        """
        if self.start == self.stop:
            return 0

        if self.stop == inf:
            return inf.__index__()

        return self.stop - self.start

    def __bool__(self) -> bool:
        """
        True if this range has a length
        """
        return len(self) > 0

    @property
    def last(self) -> int:
        """
        Gets the last value in this range. Will return inf if the range
        has no end, and -1 if it has no contents,
        """
        if not self:
            return -1
        return self.stop - 1

    @classmethod
    @lru_cache
    def from_str(cls, value: str) -> "Segment":
        """
        Construct from a string.
        """
        vals = [v.strip() for v in re.split(r":|\-", value)]

        if len(vals) > 2:
            raise ValueError(f"Too many values in {value} ({vals})")

        if len(vals) == 1:
            if vals[0] == "":
                # Empty range
                start = stop = 0
            else:
                # single value
                start = to_int(vals[0], 0)
                stop = start + 1
        else:
            # start:stop
            start = to_int(vals[0], 0)
            stop = to_int(vals[1], inf)

        return cls(start, stop)

    @staticmethod
    def sort_key(value: "Segment") -> tuple[int, int]:
        """
        Sort key function for sorting ranges
        """
        return value.start, value.stop

    @staticmethod
    def _coerce(other: Any) -> Any:
        """
        Coerce other to Segment if possible.
        Returns the original value if already a Segment.
        For Ranges, only convert if it's a single-segment range.
        """
        # circular :(
        from arranges import Ranges

        if isinstance(other, Segment):
            return other

        if isinstance(other, Ranges):
            # Only convert single-segment Ranges to Segment for comparison
            if len(other.segments) == 1:
                seg = other.segments[0]
                return Segment(seg.start, seg.stop)
            return other

        # Special handling for integers - treat as single value [n, n+1)
        if is_intlike(other):
            return Segment(int(other), int(other) + 1)

        # Handle strings - use from_str to parse correctly
        if isinstance(other, str):
            return Segment.from_str(other)

        # Handle Python range objects
        if isinstance(other, range):
            return Segment(other.start, other.stop)

        # Try to convert to Segment
        try:
            return as_type(Segment, other)
        except (TypeError, ValueError):
            return other

    def isdisjoint(self, other: Any) -> bool:
        """
        Return True if this range is disjoint from the other range
        """
        if isinstance(other, str):
            other = Segment.from_str(other)
        else:
            other = as_type(Segment, other)
        return not self.intersects(other)

    def __eq__(self, other: Any) -> bool:
        """
        Compare two segments
        """
        # circular :(

        if is_intlike(other):
            return self.start == other and self.stop == other + 1
        if isinstance(other, str):
            return str(self) == str(other)
        if not self and not other:
            return True

        other = self._coerce(other)
        if isinstance(other, Segment):
            return self.start == other.start and self.stop == other.stop
        # _coerce should always return a Segment for anything that gets here
        return False  # pragma: no cover

    def isconnected(self, other: "Segment") -> bool:
        """
        True if this range is adjacent to or overlaps the other range, and so they
        can be joined together.
        """
        return self.isadjacent(other) or self.intersects(other)

    def isadjacent(self, other: "Segment") -> bool:
        """
        True if this range is adjacent to the other range
        """
        if self.stop == other.start or other.stop == self.start:
            return True

        return False

    def intersects(self, other: "Segment") -> bool:
        """
        True if this range intersects the other range.
        """
        if self in other or other in self:
            return True

        if self.start in other or other.start in self:
            return True

        return False

    def __lt__(self, other: "Segment") -> bool:
        """
        Compare segments by (start, stop) tuple
        """
        other = self._coerce(other)
        if isinstance(other, Segment):
            return (self.start, self.stop) < (other.start, other.stop)
        return NotImplemented

    def __le__(self, other: "Segment") -> bool:
        """
        Compare segments by (start, stop) tuple
        """
        other = self._coerce(other)
        if isinstance(other, Segment):
            return (self.start, self.stop) <= (other.start, other.stop)
        return NotImplemented

    def __gt__(self, other: "Segment") -> bool:
        """
        Compare segments by (start, stop) tuple
        """
        other = self._coerce(other)
        if isinstance(other, Segment):
            return (self.start, self.stop) > (other.start, other.stop)
        return NotImplemented

    def __ge__(self, other: "Segment") -> bool:
        """
        Compare segments by (start, stop) tuple
        """
        other = self._coerce(other)
        if isinstance(other, Segment):
            return (self.start, self.stop) >= (other.start, other.stop)
        return NotImplemented

    def __contains__(self, other: Any) -> bool:
        """
        Membership test. Supports integers, strings, ranges and iterables.
        """
        # circular :(
        from arranges import Ranges

        if is_intlike(other):
            return self.start <= other <= self.last

        if not self:  # nothing fits in an empty set
            return False

        # Check for Ranges before rangelike/iterable
        if isinstance(other, Ranges):
            # Delegate to Ranges' logic
            return other in Ranges(self)

        if is_rangelike(other):
            if not other:
                return True  # the empty set is a subset of all other sets

            inf_stop = other.stop or inf
            start_inside = not self.start or other.start in self
            last_inside = self.stop is None or (inf_stop - 1) in self

            return start_inside and last_inside

        if isinstance(other, str):
            return self.__class__.from_str(other) in self

        if is_iterable(other):
            for o in other:
                if o not in self:
                    return False
            return True

        raise TypeError(f"Unsupported type {type(other)}")
