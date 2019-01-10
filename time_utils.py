from collections import namedtuple
from datetime import datetime, timedelta
from typing import Sequence, Union

import numpy as np
import skyfield
from skyfield.api import load

# Define types
Num = Union[int, float]
TimeSequence = Sequence[timedelta]
Time = skyfield.timelib.Time


TimeRange = namedtuple('TimeRange', ('time_pairs'))

def time_range(start_times: TimeSequence, end_times: TimeSequence) -> TimeRange:
    """
    Generate TimeRange class

    Parameters
    ---------
    start_times : Sequence[timedelta]
    end_times : Sequence[timedelta]
    """
    time_pairs = [(st, et) for st, et in zip(start_times, end_times)]
    return TimeRange(time_pairs)

def build_time_array(date_from: datetime, date_to: datetime, freq: Num) -> Time:
    """
    Build time_array of skyfield

    Parameters
    ---------
    date_from : datetime
    date_to : datetime
    freq : int or float
    """
    td = (date_to - date_from)
    seconds = date_from.second + np.arange(0, td.total_seconds(), freq)
    ts = load.timescale()
    time_array = ts.utc(year=date_from.year, 
                        month=date_from.month, 
                        day=date_from.day, 
                        hour=date_from.hour, 
                        minute=date_from.minute,
                        second=seconds)
    return time_array

def calc_local_time(dt: datetime, longitude: Num) -> timedelta:
    """
    Calculate local time

    Parameters
    ---------
    dt : datetime
    longitude : int or float
    """
    h = (longitude * 24) / 360
    # Calculate local time by subtracting the difference from UTC+0
    local_datetime = dt.replace(tzinfo=None) + timedelta(hours=h)
    local_time = timedelta(hours=local_datetime.hour, 
                           minutes=local_datetime.minute, 
                           seconds=local_datetime.second,
                           microseconds=local_datetime.microsecond)
    return local_time
