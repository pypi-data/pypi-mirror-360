#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/4 16:54
# @Author  : yh
# @File    : constants.py

# ----------------conf-----------------
VAR_STAT_FEATURE_FORMAT = {
    "mean": None,
    "std": None,
    "maximum": None,
    "minimum": None,
    "corr_pw": None,
    "corr_wh": None,
    "slope": None,
    "stability_factor": None,
}
WORKING_CONDITION_VAR_STAT_FEATURE_FORMAT = {
    "pw": {
        "mean": None,
        "std": None,
        "maximum": None,
        "minimum": None,
        "slope": None,
        "tendency": None,
    },
    "wh": {
        "mean": None,
        "std": None,
        "maximum": None,
        "minimum": None,
        "slope": None,
        "tendency": None,
    },
    "dykd": {
        "mean": None,
        "std": None,
        "maximum": None,
        "minimum": None,
        "slope": None,
        "tendency": None,
    }
}
# ----------------DTW-----------------
# 计算了多少班次
DTW_WARP = 1
# 在路径的非对称移动上应用的权重，随着s变大，扭曲路径越来越偏向对角线
DTW_S = 1.0
