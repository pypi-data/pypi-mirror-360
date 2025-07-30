from datetime import datetime
import pytz
import json


def parse_json(json_string, default_value=None):
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Failed to parse JSON: {e}")
        return default_value


def convert_time_to_unit(time_value, target_unit='ns'):
    if isinstance(time_value, str):
        time_value = int(time_value.strip())
    elif not isinstance(time_value, (int, float)):
        raise time_value

    time_str = str(time_value)
    length = len(time_str)

    if length > 19:
        time_str = time_str[:19]
        length = 19

    if length < 19:
        time_str = time_str + '0' * (19 - length)

    time_in_ns = int(time_str)

    if target_unit == 's':  # 转换为秒
        return time_in_ns / 1_000_000_000
    elif target_unit == 'ms':  # 转换为毫秒
        return time_in_ns / 1_000_000
    elif target_unit == 'ns':  # 保持为纳秒
        return time_in_ns
    else:
        raise time_value


def convert_to_china_time(date_string):
    # 定义 UTC 时区和中国时区
    utc_timezone = pytz.utc
    china_timezone = pytz.timezone('Asia/Shanghai')

    # 将日期时间字符串转换为 datetime 对象，并设置为 UTC 时区
    dt_utc = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
    dt_utc = utc_timezone.localize(dt_utc)

    # 转换为中国时区
    dt_china = dt_utc.astimezone(china_timezone)

    # 格式化为指定格式的字符串并返回
    china_time_string = dt_china.strftime('%Y-%m-%d %H:%M:%S')
    return china_time_string


def convert_to_china_timestamp(date_string):
    # 定义 UTC 时区和中国时区
    utc_timezone = pytz.utc
    china_timezone = pytz.timezone('Asia/Shanghai')

    # 将日期时间字符串转换为 datetime 对象，并设置为 UTC 时区
    dt_utc = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
    dt_utc = utc_timezone.localize(dt_utc)

    # 转换为中国时区
    dt_china = dt_utc.astimezone(china_timezone)

    # 转换为 UTC 时间戳
    timestamp = int(dt_china.timestamp())
    return timestamp
