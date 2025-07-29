#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
一些日期时间处理工具

约定dt前缀表示python的datetime object.

约定任何时间获取在没有特别说明时区的情况下均为 utc时区.

约定时间戳指的是Unix时间戳, 即 1730693803 这样的整数秒数. 时间戳默认UTC时区.

"""

import time
import calendar
from datetime import datetime, timezone, timedelta

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY

timezone_shanghai = timezone(timedelta(hours=8), name='Asia/Shanghai')

def dt_current(tz=timezone.utc) -> datetime:
    """
    当前时间
    """
    return datetime.now(tz=tz)


def timestamp_current() -> int:
    """
    get current timestamp
    :return:
    """
    timestamp = time.time()

    return int(timestamp)


def dt_one_hour_ago(tz=timezone.utc):
    """
    当前时间一小时前
    """
    return dt_current(tz=tz) - relativedelta(hours=1)


def dt_one_day_ago(tz=timezone.utc):
    """
    当前时间一天前
    """
    return dt_current(tz=tz) - relativedelta(days=1)


def dt_two_day_ago(tz=timezone.utc):
    """
    当前时间两天前
    """
    return dt_current(tz=tz) - relativedelta(days=2)


def dt_one_week_ago(tz=timezone.utc):
    """
    当前时间一周前
    """
    return dt_current(tz=tz) - relativedelta(weeks=1)


def dt_one_month_ago(tz=timezone.utc):
    """
    当前时间一个月前
    """
    return dt_current(tz=tz) - relativedelta(months=1)


def dt_last_day(year, month, tz=timezone.utc):
    """
    获取某年某月的最后一天
    """
    new_dt = datetime(year=year, month=month, day=calendar.monthrange(year, month)[-1], tzinfo=tz)
    return new_dt


def dt_to_timestamp(dt):
    """
    change datetime object to timestamp
    """
    timestamp = dt.timestamp()

    return int(timestamp)


def timestamp_to_dt(timestamp: int | str, tz=timezone.utc):
    """
    change timestamp to datetime object
    """

    if isinstance(timestamp, str):
        timestamp = int(timestamp)

    dt = datetime.fromtimestamp(timestamp, tz=tz)

    return dt


def is_same_year(dt1: datetime, dt2: datetime):
    """
    is the two datetime objects are in the same year
    """
    if dt1.year == dt2.year:
        return True
    else:
        return False


def is_same_month(dt1, dt2):
    """
    is the two datetime objects are in the same month
    """
    if (dt1.year == dt2.year) and (dt1.month == dt2.month):
        return True
    else:
        return False


def is_same_day(dt1, dt2):
    """
    is the two datetime objects are in the same day
    """
    if (dt1.year == dt2.year) and (dt1.month == dt2.month) and (dt1.day == dt2.day):
        return True
    else:
        return False


def is_same_hour(dt1, dt2):
    """
    is the two datetime objects are in the same hour
    """
    if (
            (dt1.year == dt2.year)
            and (dt1.month == dt2.month)
            and (dt1.day == dt2.day)
            and (dt1.hour == dt2.hour)
    ):
        return True
    else:
        return False


def dt_normal_format(dt):
    """
    datetime object return string as normal format for example: '2018-12-21 15:39:20'
    """
    return dt.__format__("%Y-%m-%d %H:%M:%S")


def round_to_day(dt):
    """
    datetime object取整到天,其余比如小时等信息略去为0
    """
    res = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return res


def round_to_hour(dt):
    """
    datetime object取整到小时,其余比如分钟等信息略去为0
    """
    res = dt.replace(minute=0, second=0, microsecond=0)
    return res


def round_to_minute(dt):
    """
    datetime object取整到分钟,其余比如秒等信息略去为0
    """
    res = dt.replace(second=0, microsecond=0)
    return res


def round_to_second(dt):
    """
    datetime object取整到秒,其余比如微秒等信息略去为0
    """
    res = dt.replace(microsecond=0)
    return res


def get_datetime_range(months, tz=timezone.utc):
    """
    返回一系列的datetime object 列表, 从当前时间往前数几个月.

    >>> get_datetime_range(1) # doctest: +SKIP
    [datetime.datetime(2024, 10, 5, 14, 27, 46, tzinfo=datetime.timezone.utc),
    datetime.datetime(2024, 11, 5, 14, 27, 46, tzinfo=datetime.timezone.utc)]

    >>> get_datetime_range(0) # doctest: +SKIP
    [datetime.datetime(2024, 11, 5, 14, 27, 53, tzinfo=datetime.timezone.utc)]

    """
    start_dt = dt_current(tz=tz) - relativedelta(months=months)
    return list(rrule(freq=MONTHLY, dtstart=start_dt, until=dt_current(tz=tz)))
