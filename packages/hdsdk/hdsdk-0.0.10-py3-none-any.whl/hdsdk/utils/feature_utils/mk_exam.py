import pymannkendall as pymk


def mk(x):
    result = pymk.original_test(x)
    # p小于0.05,则可以拒绝原假设,即该数据序列存在变化趋势。
    trend = result.trend
    if trend == "increasing":
        trend = 1
    if trend == "decreasing":
        trend = 2
    if trend == "no trend":
        trend = 3

    return trend


if __name__ == "__main__":
    arr = [36.5, 36.6, 36.7, 36.1, 38, 37.2, 36.2, 36.5, 37.1, 38, 39, 41, 38.39, 37, 38, 38, 37, 36, 36]
    arr1 = []
    print(mk(arr))
