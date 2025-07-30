#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/15 13:17
# @Author  : yh
# @File    : api_client.py
import requests
import hdsdk.conf.url_config as url_config


class APIClient:
    requests_urls = {
        # 按测点查询实时数据
        '/data/real/val': 'cbba1bee-1856-49ec-be41-6016bd88da30',
        # 按测点查询历史数据
        '/data/his/val': '7326296b-b5e9-4656-aa4c-f1d1f4fa4e19',
        # 按测点组查询历史数据
        '/data/his/group/code': 'f9d1211d-c8b1-4a17-ae6e-87d5784fe430',
        # 根据功能标签获取测点
        '/global/function/points': '48a3908d-cc05-42f9-b813-9f850db555c4',
        # 写入数据特征表
        '/inc/property/data/write': 'f38e27e4-2b5b-4ce0-924f-738989e1252a',
        # 写入振动相关性特征
        '/inc/vib/relativity/write': 'cc78ae90-8bb4-4e7e-916f-662e31fcbd5b',
        # 写入工况数据特征表
        '/inc/working/data/query': '95da39a8-ee9f-4c06-9cef-6c739da5f40a',
        # 查询数据特征表数据
        '/inc/property/data/query/point': '8c70d305-fff1-4ad1-8e8f-1c45f8778a93',
        # 获取报警/异常功能所需测点
        '/global/warning/points': 'a5c8df4a-9135-4d41-837a-5a028f26433a',
        # 写入报警/异常事件
        '/inc/abnormity/write/event': '1e41ddce-b786-4556-92ac-136b40be84b7',
        # 写入报警时间
        '/inc/abnormity/write/record': '288ca54f-6ecb-492c-a724-7260a02a72aa',
        # 写入报警时间
        '/sdk/call': 'b43b8d51-eec1-4647-a2a1-fe3096f41ac5',

    }

    def __init__(self):
        self.org_domain = 'cvxa3663'
        self.token = ''
        self.login()

    def login(self):
        endpoint = url_config.BACKEND_CLIENT_URL + url_config.BACKEND_API_PATH
        data = {
            'account': url_config.CLIENT_USERNAME,
            'password': url_config.CLIENT_PASSWORD
        }
        res = self.post(endpoint, data=data)
        if res and res['code'] == 200 and res['data']:
            self.token = res['data']['token']

    def getExtApi(self, id='', url='', param=None):
        if param is None:
            param = {}
        endpoint = url_config.EXT_API_CLIENT_URL + url_config.EXT_API_BASE_PATH
        if id == '':
            id = self.requests_urls.get(url)
        data = {'id': id, 'param': param}
        res = self.post(endpoint, data=data)
        if res['code'] == 200 and res['data']:
            return res['data']
        return res

    def post(self, endpoint, data=None, headers=None):
        if headers == None:
            headers = {'token': self.token, 'org_domain': self.org_domain}
        response = requests.post(endpoint, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        return response


if __name__ == '__main__':
    api_client = APIClient()

    param = {
        'funName': 'vib_property',
        'unitNum': 1,
        'state': 1
    }
    res = api_client.getExtApi(url='/global/function/points', param=param)
    point_set = []
    for item in res['data'].values():
        for point in item.keys():
            point_set.append(point)
    print(res)
    print(point_set)
