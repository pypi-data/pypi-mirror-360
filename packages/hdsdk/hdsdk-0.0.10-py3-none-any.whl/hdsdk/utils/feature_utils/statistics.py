import numpy as np
import pandas as pd
import math


def get_var(valLst):
    """
    计算一组数据的方差
    :param valLst: 输入数据
    :return: 输入数据的方差
    """
    result = np.var(valLst)
    if result is not None:
        return float(result)
    return result


def get_std(valLst):
    """
    计算一组数据的标准差
    :param valLst: 输入数据
    :return: 输入数据的标准差
    """
    result = np.std(valLst)
    if result is not None:
        return float(result)
    return result


def get_mean(valLst):
    """
    计算一组数据的均值
    :param valLst: 输入数据
    :return: 输入数据的均值
    """
    result = np.mean(valLst)
    if result is not None:
        return float(result)
    return result


def get_weighted_avg(valLst, weightedLst=None):
    """
    计算一组数据的带权重均值（加权平均值）
    :param valLst: 输入数据
    :param weightedLst: 权值
    :return: 输入数据的加权平均值
    """
    result = np.average(valLst, weights=weightedLst)
    if result is not None:
        return float(result)
    return result


def get_geometric_avg(valLst):
    """
    计算一组数据的几何平均值
    :param valLst: 输入数据
    :return: 输入数据的几何平均值
    """
    total = 1
    for i in valLst:
        total *= i
    return pow(total, 1 / len(valLst))


def get_rms(valLst):
    """
    均方根
    """
    return math.sqrt(sum([x ** 2 for x in valLst]) / len(valLst))


def get_cv(valLst):
    """
    离散系数:通常用来比较两组量纲差异明显的数据的离散程度
    """
    mean = np.mean(valLst)  # 平均值
    std = np.std(valLst, ddof=0)  # 标准差
    cv = std / mean
    return cv


def get_mode(valLst):
    """
    计算一组数据的众数
    :param valLst: 输入数据
    :return: 输入数据的众数
    """

    counts = np.bincount(valLst)
    result = np.argmax(counts)
    if result is not None:
        return float(result)
    return result


def get_median(valLst):
    """
    计算一组数据的中位数
    :param valLst: 输入数据
    :return: 输入数据的中位数
    """

    result = np.median(valLst)
    if result is not None:
        return float(result)
    return result


def get_fgf(valLst):
    """
    方根幅值
    """
    return ((np.mean(np.sqrt(np.abs(valLst))))) ** 2


def get_pp(valLst):
    """
    峰峰值
    """
    result = 0.5 * (np.max(valLst) - np.min(valLst))

    return result


def get_max(valLst):
    """
    最大值
    """
    result = np.max(valLst)
    if result is not None:
        return float(result)

    return result


def get_min(valLst):
    """
    最小值
    """
    result = np.min(valLst)
    if result is not None:
        return float(result)

    return result


def get_range(valLst):
    """
    极差
    """

    return get_max(valLst) - get_min(valLst)


def get_kl(x, y):
    """
    KL散度
    """

    return sum(x * np.log(x / y))


def get_crest(valLst):
    """
    峰值因子
    """
    result = np.max(np.abs(valLst)) / get_rms(valLst)

    return result


def get_clear(valLst):
    """
    裕度因子
    """
    result = np.max(np.abs(valLst)) / get_fgf(valLst)

    return result


def get_shape(valLst):
    """
    波形因子
    """
    result = (len(valLst) * get_rms(valLst)) / (np.sum(np.abs(valLst)))

    return result


def get_imp(valLst):
    """
    脉冲指数
    """
    result = (np.max(np.abs(valLst))) / (np.mean(np.abs(valLst)))

    return result


def get_slope(x, y):
    """
    斜率，numpy内置函数，线性拟合
    """
    slope, _ = np.polyfit(x, y, 1)
    return slope


def get_slope_with_normalization(x, y):
    """
    斜率，先进行线性归一化
    """
    if np.min(x) == np.max(x):
        return 0
    if np.min(y) == np.max(y):
        return -9999

    x_normalized = min_max_normalize(x)
    y_normalized = min_max_normalize(y)

    for val in x_normalized:
        if math.isnan(val):
            return -9999
    for val in y_normalized:
        if math.isnan(val):
            return -9999

    slope, _ = np.polyfit(x_normalized, y_normalized, 1)

    return slope


def get_stability_factor(x, t, corr_pw, corr_wh):
    """
    稳定系数
    :param x: 待计算时间序列数据
    :param corr_pw: 相关系数（有功）
    :param corr_wh: 相关系数（水头）
    :return: 稳定系数
    """
    if corr_wh == -10 and corr_pw != -10:
        if abs(corr_pw) > 0.8:
            corr = corr_pw
            return 1 - abs(corr)
        if abs(corr_pw) <= 0.8:
            slope = get_slope_with_normalization(x, t)
            return 1 - abs(math.tanh(slope))
    else:
        if abs(corr_pw) > 0.8 or abs(corr_wh) > 0.8:
            corr = corr_pw if corr_pw > corr_wh else corr_wh
            return 1 - abs(corr)
        if abs(corr_pw) <= 0.8 and abs(corr_wh) <= 0.8:
            slope = get_slope_with_normalization(x, t)
            return 1 - abs(math.tanh(slope))


def min_max_normalize(x, epsilon=0.001):
    data = np.asarray(x)
    min_val = np.min(data)
    max_val = np.max(data)
    if max_val - min_val == 0:
        max_val += epsilon
    data_normalized = (data - min_val) / (max_val - min_val)
    return data_normalized


def mean_std_normalize(data):
    mean_val = np.mean(data)
    std_val = np.std(data)
    normalized_data = (data - mean_val) / std_val
    return normalized_data


def log_normalize(data):
    max_val = np.max(data)
    normalized_data = np.log(data + 1) - np.log(max_val + 1)
    return normalized_data


def align(x, y):
    df1 = pd.DataFrame({
        'time': x['time'],
        'value': x['value']
    })

    df2 = pd.DataFrame({
        'time': y['time'],
        'value': y['value']
    })

    merge = pd.merge(df1, df2, on='time', how='inner')
    x_val, y_val, t = list(merge['value_x']), list(merge['value_y']), list(merge['time'])
    return x_val, y_val, t


if __name__ == '__main__':
    # 示例数据
    # x = np.array([1, 2, 3, 4, 5])
    # y = np.array([5, 6, 7, 8, 7, 9])

    # data = pd.DataFrame({"数据序列A": x, "数据序列B": y})
    # corrs = data.corr()

    # result = pd.merge_asof(df1, df2, on='time', by='time', direction='forward')
    # x = {
    #     'time': [1, 3, 6],
    #     'value': [10, 20, 40]
    # }
    # y = {
    #     'time': [1, 3, 5, 6],
    #     'value': [5, 10, 15, 20]
    # }
    # x, y, t = align(x, y)
    # print(x)
    # print(y)
    # print(t)

    # try:
    #     a = [1, 1, 1, 1.2, 1]
    #     # b = [0,0,0,3,0]
    #     b = [3.1, 3.3, 3.8, 4.3, 5]
    #     # r = get_slope(a,b)
    #     print(np.max(a))
    #     r = get_slope_with_normalization(a, b)
    #     print(r)
    # except Exception as e:
    #     print(e)
    a = [3.5, 3, 3]
    # b = [0,0,0,3,0]
    b = [0, 0.1, 0.14]
    # r = get_slope(a,b)

    r = get_slope_with_normalization(a, b)
    print(r)
