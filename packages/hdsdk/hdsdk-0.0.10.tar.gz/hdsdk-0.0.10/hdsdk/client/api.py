#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/22 16:00
# @Author  : yh
# @File    : api.py
from hdsdk.client.api_client import APIClient
import time


class Api(object):
    def __init__(self):
        self.api_client = APIClient()

    def query_realtime_val(self, param):
        """
        查询实时测点数据
        :param param:
        :return:
        """
        res = self.api_client.getExtApi(url='/data/real/val', param=param)
        if res['code'] == 200:
            return res['data']
        return {}

    def query_history_val(self, param):
        """
        查询实时测点数据
        :param param:
        :return:
        """
        res = self.api_client.getExtApi(url='/data/his/val', param=param)
        # if res['code'] == 200:
        #     return res['data']
        return res

    '/data/his/group/code'

    def query_history_val_by_group(self, param):
        """
        按测点组查询历史数据
        :param param:
        :return:
        """
        res = self.api_client.getExtApi(url='/data/his/group/code', param=param)
        # if res['code'] == 200:
        #     return res['data']
        return res

    def query_point_by_tag(self, param):
        """
        按标签查询测点集合
        :param param:
        :return:
        """
        # param = {
        #     'funName': 'vib_property',
        #     'unitNum': 1,
        #     'state': 1
        # }
        res = self.api_client.getExtApi(url='/global/function/points', param=param)
        point_set = []
        for item in res['data'].values():
            for point in item.keys():
                point_set.append(point)
        return point_set

    def save_inc_features(self, param):
        """
        写入数据特征增量表
        :param param:
        :return:
        """
        res = self.api_client.getExtApi(url='/inc/property/data/write', param=param)
        return res

    def save_inc_vib_relativity(self, param):
        """
        写入振动相关性特征增量表
        :param param:
        :return:
        """
        res = self.api_client.getExtApi(url='/inc/vib/relativity/write', param=param)
        return res

    def save_inc_working_condition_analysis(self, param):
        """
        写入工况数据特征表增量表
        :param param:
        :return:
        """
        res = self.api_client.getExtApi(url='/inc/working/data/query', param=param)
        return res

    def query_inc_features(self, param):
        """
        查询数据特征增量表
        :param param:
        :return:
        """
        res = self.api_client.getExtApi(url='/inc/property/data/query/point', param=param)
        return res

    def query_alert_point(self, param):
        """
        获取报警/异常功能所需测点
        :param param:
        :return:
        """
        res = self.api_client.getExtApi(url='/global/warning/points', param=param)
        keys = []
        for key in res['data'].keys():
            keys.append(key)
        return keys

    def save_inc_alert_event(self, param):
        """
        写入报警/异常事件
        :param param:
        :return:
        """
        res = self.api_client.getExtApi(url='/inc/abnormity/write/event', param=param)
        return res

    def save_inc_alert_span(self, param):
        """
        写入报警时间
        :param param:
        :return:
        """
        res = self.api_client.getExtApi(url='/inc/abnormity/write/record', param=param)
        return res

    def sdk_call(self, param):
        """
        调用sdk
        :param param:
        :return:
        """
        res = self.api_client.getExtApi(url='/sdk/call', param=param)
        return res


if __name__ == '__main__':
    api = Api()
    res = Api().query_history_val(
        {
            'unitNum': 1,
            'start': int((time.time() - 600) * 1000),
            'end': int(time.time() * 1000),
            'body': [
                {
                    'code': 'aco_cow_liq_2'
                },
                {
                    'code': 'ace_pow_1'
                }
            ]
        }
    )
    print(res)
    # 测点组查历史数据
    group = [
        {
            'group': 'upg_cow_liq'
        },
        {
            'group': 'ace_pow'
        },
    ]
    param = {
        'unitNum': 1,
        'start': int((time.time() - 600) * 1000),
        'end': int(time.time() * 1000),
        'body': group
    }
    history_data = api.query_history_val_by_group(param)
    print(history_data)
