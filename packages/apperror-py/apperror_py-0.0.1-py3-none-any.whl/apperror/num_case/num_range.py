from apperror.utils import check_arg


class NumRange:
    """Represents a number range which is from start to end, both inclusive."""

    def __init__(self, start: int, end: int) -> None:
        """Initialize a new NumRange.

        Args:
            start: The start of the range (inclusive)
            end: The end of the range (inclusive)

        Raises:
            ValueError: If start < 0, end < 0, or end < start
        """
        check_arg(start >= 0, "start < 0")
        check_arg(end >= 0, "end < 0")
        check_arg(end >= start, "end < start")
        self._start = start
        self._end = end

    @property
    def start(self) -> int:
        return self._start

    @property
    def end(self) -> int:
        return self._end

    def include(self, num: int) -> bool:
        """Check if a number is within this range."""
        return self._start <= num <= self._end

    def include_range(self, other: "NumRange") -> bool:
        """Check if another range is completely within this range."""
        return self._start <= other.start and other.end <= self._end

    def overlap(self, other: "NumRange") -> bool:
        """Check if this range overlaps with another range.

        Args:
            other: The other range to check

        Returns:
            True if the ranges overlap, False otherwise
        """
        return not (self._end < other.start or other.end < self._start)

    def __str__(self) -> str:
        """Get the string representation of the range.

        Returns:
            A string in the format "[start, end]"
        """
        return f"[{self._start}, {self._end}]"

    def __repr__(self) -> str:
        """Get the detailed string representation of the range.

        Returns:
            A string showing the range's start and end values
        """
        return f"NumRange(start={self._start}, end={self._end})"

    def __eq__(self, other: "NumRange") -> bool:
        """Check if this range is equal to another range."""
        return self._start == other.start and self._end == other.end

    def __hash__(self) -> int:
        return hash((self._start, self._end))
