from __future__ import annotations
import datetime
from typing import Union


class InvalidIntervalError(ValueError):
    """Custom exception raised when an interval string is invalid."""


def parse_iso_utc(s: str) -> datetime.datetime:
    """Parses a date or datetime string and returns a UTC-aware datetime.

    Args:
        s (str): ISO 8601 date or datetime string. If only a date is given, time defaults to 00:00.

    Returns:
        datetime.datetime: A timezone-aware datetime object in UTC.
    """
    if "T" not in s:
        s += "T00:00"
    return datetime.datetime.fromisoformat(s).replace(tzinfo=datetime.timezone.utc)


class Interval:
    """Represents a time interval between two datetime values."""

    def __init__(self, start: datetime.datetime, end: datetime.datetime):
        """
        Initialize an Interval object.

        Args:
            start (datetime.datetime): The start of the interval.
            end (datetime.datetime): The end of the interval.
        """

        self.start: datetime.datetime = start
        self.end: datetime.datetime = end

    @classmethod
    def from_string(cls, interval_str: str) -> Union[Interval, datetime.datetime]:
        """Parses an ISO 8601 interval or date string into an Interval or datetime object.

        Args:
            interval_str (str): A string in the format 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS',
                                or an interval like 'start/end'.

        Returns:
            Union[Interval, datetime.datetime]: An `Interval` if input is a range, or a single UTC datetime.

        Raises:
            InvalidIntervalError: If the string cannot be parsed.
        """
        try:
            if "/" in interval_str:
                start_str, end_str = interval_str.split("/")
                start_datetime = parse_iso_utc(start_str)
                end_datetime = parse_iso_utc(end_str)
                return cls(start=start_datetime, end=end_datetime)
            else:
                return parse_iso_utc(interval_str)
        except ValueError:
            raise InvalidIntervalError(f"Invalid interval string: {interval_str}")

    def to_string(self):
        """Convert the Interval into an ISO 8601 interval string.

        Returns:
            str: A string in the format 'start/end'.
        """
        start_str = self.start.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = self.end.strftime("%Y-%m-%dT%H:%M:%S") if self.end else str()
        return start_str + "/" + end_str

    def __repr__(self) -> str:
        """Returns a string representation of the Interval.

        Returns:
            str: A string in the format 'Interval(start=..., end=...)'.
        """
        if self.end is None:
            return f"Interval(start={self.start.isoformat()})"
        else:
            return (
                f"Interval(start={self.start.isoformat()}, end={self.end.isoformat()})"
            )
