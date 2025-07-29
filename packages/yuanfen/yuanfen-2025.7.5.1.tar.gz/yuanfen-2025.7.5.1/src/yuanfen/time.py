import time as py_time
from datetime import datetime

import pytz


def now(tz: str = "Asia/Shanghai", with_tz: bool = False) -> datetime:
    now_with_tz = datetime.now(tz=pytz.timezone(tz))
    return now_with_tz if with_tz else now_with_tz.replace(tzinfo=None)


# get current timestamp
def current_timestamp(length: int = 16) -> int:
    return get_timestamp(None, length)


# get timestamp from datetime
def get_timestamp(dt: datetime = None, length: int = 16) -> int:
    _timestamp = dt.timestamp() if dt else py_time.time()
    return int(_timestamp * 10 ** (length - 10))


def format(dt: datetime = None, format: str = "%Y-%m-%dT%H:%M:%S.%f") -> str:
    if dt is None:
        dt = now()
    return dt.strftime(format)


def parse(dt_str: str, format: str = "%Y-%m-%dT%H:%M:%S.%f") -> datetime:
    return datetime.strptime(dt_str, format)


def remove_tz(dt: datetime, tz: str = "Asia/Shanghai") -> datetime:
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(pytz.timezone(tz)).replace(tzinfo=None)


def format_duration(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def sleep(secs: float):
    py_time.sleep(secs)


def time():
    return py_time.time()
