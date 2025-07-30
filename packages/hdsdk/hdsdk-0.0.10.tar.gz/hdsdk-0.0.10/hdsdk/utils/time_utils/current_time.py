#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/11/13 8:52
# @Author  : yh
# @File    : current_time.py
from datetime import datetime


def curr_time():
    # 获取当前时间
    now = datetime.now()
    # 格式化当前时间为年月日时分秒
    formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time

