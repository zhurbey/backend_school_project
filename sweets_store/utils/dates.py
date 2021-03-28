import itertools
import typing as t
from datetime import datetime, timedelta

import pytz


TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


def match_hours_interval_format(interval: str) -> bool:
    """Check if provided hours interval follow pattern HH:MM-HH:MM"""

    try:
        left, right = interval.split("-")
        datetime.strptime(left, TIME_FORMAT)
        datetime.strptime(right, TIME_FORMAT)
    except ValueError:
        return False

    # Right moment is bigger then the left one
    if left >= right:
        return False

    return True


def pydantic_match_hours_interval_validator(interval: str) -> str:

    if not match_hours_interval_format(interval):
        raise ValueError(
            f"Time period '{interval}' definition doesn't "
            f"follow format HH:MM-HH:MM. "
            f"0 <= hour < 24, 0 <= minute < 60, left moment is less then the right"
        )

    return interval


def do_time_intervals_intersect(intervals_set1: t.List[str], intervals_set2: t.List[str]) -> bool:

    for period1, period2 in itertools.product(intervals_set1, intervals_set2):

        left1, right1 = period1.split("-")
        left2, right2 = period2.split("-")

        # Time intervals intersect condition. Compare as strings
        if left1 < right2 and left2 < right1:
            return True

    return False


def any_timezone_to_GMT(dt: datetime) -> datetime:
    """Convert datetime with timezone info from any timezone to +00:00"""

    result = dt.astimezone(pytz.UTC)
    result = result.replace(tzinfo=None)

    return result


def string_to_GMT_datetime(dt_str: str) -> datetime:

    dt = datetime.strptime(dt_str, DATETIME_FORMAT)
    return any_timezone_to_GMT(dt)


def datetime_to_string(dt: datetime) -> str:

    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def datetime_delta_to_seconds(dt: timedelta) -> float:

    return dt.seconds + dt.microseconds / 10 ** 6
