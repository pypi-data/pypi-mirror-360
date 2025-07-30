#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/15 16:27
# @Author  : yh
# @File    : utc2timestamp.py
from datetime import datetime, timezone


def utc2timestamp(utc_time_str, unit="ms"):

    # 解析UTC时间字符串
    utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S')
    # utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    # 将UTC时间转换为timestamp
    timestamp = utc_time.replace(tzinfo=timezone.utc).timestamp()
    if unit == "ms":
        return int(timestamp * 1000)
    else:
        return int(timestamp)


if __name__ == '__main__':
    # 示例使用
    utc_time_str = '2023-01-01T12:00:00'
    # utc_time_str = '2023-01-01T12:00:00.000Z'
    timestamp = utc2timestamp(utc_time_str)
    print(timestamp)  # 输出时间戳
    # 1672574400.0
