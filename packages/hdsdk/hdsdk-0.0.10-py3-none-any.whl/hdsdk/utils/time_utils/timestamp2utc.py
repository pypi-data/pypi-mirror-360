#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/27 10:51
# @Author  : yh
# @File    : timestamp2utc.py
from datetime import datetime, timedelta


def timestamp2utc(ms_timestamp):
    # 毫秒级时间戳转换为秒
    timestamp_in_seconds = ms_timestamp / 1000.0
    utc_time = datetime.fromtimestamp(timestamp_in_seconds)
    return utc_time.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    # 示例使用
    ms_timestamp = 1615112345321  # 假设这是一个毫秒级时间戳
    utc_time = timestamp2utc(ms_timestamp)
    print(utc_time)  # 输出转换后的UTC时间
