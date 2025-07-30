#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/4 18:40
# @Author  : yh
# @File    : corr.py
import pandas as pd
from hdsdk.utils.feature_utils.statistics import align


def get_corr(x, y):
    """
    计算两组时间序列数据的相关系数
    :param x: 数据x
    :param y: 数据y
    :return: 相关系数
    """
    x, y, _ = align(x, y)
    data = pd.DataFrame({"数据序列A": x, "数据序列B": y})
    corrs = data.corr()
    corr = corrs["数据序列A"]["数据序列B"]
    return corr


def get_corr_without_align(x, y):
    """
    计算两组时间序列数据的相关系数
    :param x: 数据x
    :param y: 数据y
    :return: 相关系数
    """
    data = pd.DataFrame({"数据序列A": x, "数据序列B": y})
    corrs = data.corr()
    corr = corrs["数据序列A"]["数据序列B"]
    return corr


def get_corr_multi(xList, y) -> list:
    """
    计算多个时间序列数据与某时间序列的相关系数
    :param xList: 多个时间序列数据列表，array_like
    :param y: 单个时间序列数据，array_like
    :return: 相关系数列表
    """
    result = []

    if isinstance(y, dict):
        y = list(y.values())

    for x in xList:
        if isinstance(x, dict):
            x = list(x.values())
        result.append(get_corr(x, y))

    return result


def get_corr_multi_by_name(xList, nameList, y) -> dict:
    """
    计算多个时间序列数据与某时间序列的相关系数，以hashmap形式返回，带测点名称
    :param xList: 多个时间序列数据列表，array_like
    :param nameList: 多个时间序列数据对应测点名称列表，array_like
    :param y: 单个时间序列数据，array_like
    :return:
    """
    result = {}

    if isinstance(y, dict):
        y = list(y.values())

    for x, name in zip(xList, nameList):
        if isinstance(x, dict):
            x = list(x.values())
        result[name] = get_corr(x, y)

    return result


if __name__ == '__main__':
    x = [1, 2, 3, 4, 7, ]
    y = [2, 3, 4.1, 5, 8]
    # data = np.array([x,y]).transpose()
    # data1 = np.array([x,y])
    # # data = np.concatenate((np.array(x),np.array(y)))
    # print(data)
    # df = pd.DataFrame(data,index= ["001","002","003","004"],columns=["a","b"]).transpose()
    # print(df)
    c = get_corr(x, y)

    print(c)
