# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/19 17:17

@Author  : wangchao
"""
import datetime
import time


def get_time_hour_update(n):
    """
    获取当前小时偏移时间
    e.g. 2024-03-20 15:13:04
    """
    return (datetime.datetime.now() + datetime.timedelta(hours=n)).strftime("%Y-%m-%d %H:%M:%S")


def get_time_minutes_update(n):
    """
    获取当前分钟偏移时间
    e.g. 2024-03-20 15:13:04
    """
    return (datetime.datetime.now() + datetime.timedelta(minutes=n)).strftime("%Y-%m-%d %H:%M:%S")


def timestamp_YmdHMS():
    """
    当前时间戳年月日_时分秒
    e.g. 20240320_151304
    """
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def timestamp_YmdHMSns():
    """
    当前时间戳年月日_时分秒.纳秒
    e.g. 20240320_151304.846874624
    """
    nanos = time.time_ns()
    dt = datetime.datetime.fromtimestamp(nanos / 1e9)
    return f"{dt.strftime('%Y%m%d_%H%M%S')}.{round(nanos % 1e9)}"


def wait(times=15):
    """
    接口设置等待时间
    """
    time.sleep(times)


class TimeFunction:
    @classmethod
    def get_time_hour_update(cls, n):
        return get_time_hour_update(n)

    @classmethod
    def get_time_minutes_update(cls, n):
        return get_time_minutes_update(n)

    @classmethod
    def timestamp_YmdHMS(cls):
        return timestamp_YmdHMS()

    @classmethod
    def timestamp_YmdHMSns(cls):
        return timestamp_YmdHMSns()

    @classmethod
    def wait(cls, times=15):
        wait(times)


__all__ = [
    "TimeFunction",
    "get_time_hour_update", "get_time_minutes_update", "timestamp_YmdHMS", "timestamp_YmdHMSns", "wait"
]
