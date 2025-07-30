from hdsdk.client.api import Api
from hdsdk.utils.base_util import convert_time_to_unit

api = Api()


# 通过测点获取设备测点历史数据
def get_history_data_by_point(unit_num, start, end, codes):
    return api.query_history_val(
        {
            'unitNum': unit_num,
            'start': int(start * 1000),
            'end': int(end * 1000),
            'body': [{"code": item} for item in codes]
        }
    )


# 通过测点组获取设备测点历史数据
def get_history_data_by_group(unit_num, start, end, groups):
    return api.query_history_val_by_group(
        {
            'unitNum': unit_num,
            'start': int(start * 1000),
            'end': int(end * 1000),
            'body': [{"group": item} for item in groups]
        }
    )


# 获取判据配置
def get_judge_config(judge_id):
    param = {
        "method": "db.exec",
        "args": [f"select * from meta_rt_fault_judge_config where del_flag = 0 and judge_id = '{judge_id}'"]
    }
    res = api.sdk_call(param)
    if len(res) > 0:
        return res[0]
    return None


# 获取数据特征信息表
def get_device_data_information(code, start, end):
    # 增量表查询时间要转换纳秒
    start_time = convert_time_to_unit(start)
    end_time = convert_time_to_unit(end)
    param = {
        "method": "influxdb.queryRaw",
        "args": [
            f"select * from device_data_Information where code = '{code}' and time >= {start_time} and time <= {end_time}"]
    }
    res = api.sdk_call(param)
    return res


# 获取判据配置
def get_pw_point():
    param = {
        "method": "db.exec",
        "args": [
            f"select * from meta_rt_point_value where del_flag = 0 and meta_rt_point_value.point_id = 'Workingpower'"]
    }
    res = api.sdk_call(param)

    return res


# 获取阈值配置
def get_threshold_config(unit_num, group_id):
    param = {
        "method": "db.select",
        "args": ["meta_rt_threshold_config", {
            "unitNum": unit_num,
            "group_id": group_id,
            "del_flag": 0
        }]
    }
    return api.sdk_call(param)


def result(code=200, data={}, msg=""):
    res = {"code": code, "data": data, "msg": msg}
    print("诊断结果：", res)
    return res


if __name__ == '__main__':
    print(get_pw_point()[0]['val'])
    a = get_pw_point()
    threshold_config = get_threshold_config('1', 'upg_cow_wtp')
    print(threshold_config)
    # judge = get_judge_config('V01501')
    # print(judge)
