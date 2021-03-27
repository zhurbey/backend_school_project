import itertools
import typing as t
from datetime import datetime


TIME_FORMAT = "%H:%M"


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


def datetime_to_string(datetime_obj: datetime) -> str:

    return datetime_obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
