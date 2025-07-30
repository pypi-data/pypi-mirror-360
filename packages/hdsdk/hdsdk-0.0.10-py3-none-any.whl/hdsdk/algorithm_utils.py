
import json
import os
from hdsdk.conf.url_config import update_client_url
from hdsdk.utils.data_util import get_judge_config
from hdsdk.utils.data_util import api, get_history_data_by_group, get_threshold_config, get_pw_point
from hdsdk.utils.feature_utils.statistics import get_mean
from hdsdk.conf.common_config import DNY_HIGH, DNY_LOW, ALERT_LOW_1, ALERT_LOW_2, ALERT_HIGH_1, \
    ALERT_HIGH_2, PW_STABILITY_FACTOR, PW_STABILITY_LIMIT_VALUE, DEFAULT_FALSE_PROP
from hdsdk.exceptions import GroupNumError, GroupDataError, PowerDataError, StableOperationError, \
    ThresholdError, ThresholdDataError, ThresholdZeroError, PointsError, ParamZeroError, JudgeConfigError


class AlgorithmUtils:
    def __init__(self, request_data=None, client_url=None):
        self.request_data = None
        self.judge_id = None
        self.start = 0
        self.end = 0
        self.algorithm_fitting = 0
        self.algorithms = []
        self.desc = ''
        self.groups = []
        self.name = ""
        self.param = []
        self.probability = 0.0
        self.judge_type = ""
        self.unit_num = ""
        self.threshold = {}
        self.data = {}
        self.working_power = []
        self.work_data = {}
        #
        self.diagnosis_result = None
        self.pw_data = None
        self.points = []
        self.groups_data = {}
        self.group_data = {}
        self.threshold_dict = {}

        # 如果初始数据存在，调用 updateData 进行初始化
        if request_data:
            self.update_data(request_data)

        if client_url:
            update_client_url(client_url)
            api.api_client.login()


    def update_data(self, request_data):
        self.request_data = request_data
        self.judge_id = request_data.get('judge_id')
        self.start = int(request_data.get('start', 0))
        self.end = int(request_data.get('end', 0))

        debugMode = os.getenv('DEBUG_MODE', '')
        # 调试模式
        if debugMode == '1':
            judge_config = get_judge_config(self.judge_id)
            # 检查配置是否存在
            self.check_judge_config_data(judge_config)
            # 处理json数据
            judge_config["param"] = json.loads(judge_config.get('param', []))
            judge_config["groups"] = json.loads(judge_config.get('groups', []))
            judge_config["algorithms"] = json.loads(judge_config.get('algorithms', []))
            # 测点数据
            groups_result = get_history_data_by_group(judge_config.get('unitNum', ''), self.start, self.end, judge_config.get('groups'))
            if groups_result.get('code') == 200:
                judge_config["data"] = groups_result.get('data', {}).get('points', [])
            # 工况数据
            pw_point = get_pw_point()
            judge_config["working_power"] = [pw_point[0]['val']] if pw_point else []
            # 查询15min内有功功率测点数据
            judge_config["work_data"] = get_history_data_by_group(judge_config.get('unitNum', ''), self.start, self.end, judge_config["working_power"])

            # 赋值给request_data
            self.request_data = judge_config

        self.param = self.request_data.get('param', [])
        self.groups = self.request_data.get('groups', [])
        self.algorithms = self.request_data.get('algorithms', [])

        self.algorithm_fitting = int(self.request_data.get('algorithm_fitting', 0))
        self.desc = self.request_data.get('desc', '')
        self.name = self.request_data.get('name', "")
        self.probability = self.request_data.get('probability', 0.0)
        self.judge_type = self.request_data.get('type', "")
        self.unit_num = self.request_data.get("unitNum", "")
        self.threshold = self.request_data.get('threshold', {})

        # 接口获取
        self.data = self.request_data.get('data', {})
        self.working_power = self.request_data.get("working_power", [])
        self.work_data = self.request_data.get("work_data", {})
        #
        # 更新输出结果
        self.diagnosis_result = {
            "judge_id": self.judge_id,
            "value": self.get_default_value()
        }

    def get_default_value(self):
        if self.judge_type == 'C':
            return False
        else:  # 默认 P 类型
            return DEFAULT_FALSE_PROP

    # 数据预处理
    def dataPreprocessing(self, request_data=None):
        if request_data:
            self.update_data(request_data)

        # 检测绑定测点组是否为空
        self.check_group_number(self.groups)

        # 如果传入 data 为空，读取数据库设备测点数据
        if not self.data:
            groups_result = get_history_data_by_group(self.unit_num, self.start, self.end, self.groups)
            if groups_result.get('code') == 200:
                self.groups_data = groups_result.get('data', {}).get('points', [])
        else:
            self.groups_data = self.data

        # 检测组历史数据是否为空
        self.check_group_data(self.groups_data)
        print("测点数据：", self.groups_data)

        # 如果传入 working_power、work_data为空，读取数据库有功功率测点数据
        if not self.working_power:
            pw_point = get_pw_point()
            self.working_power =  [pw_point[0]['val']] if pw_point else []

        if not self.work_data or self.work_data.get('code') != 200:
            # 查询15min内有功功率测点数据
            self.work_data = get_history_data_by_group(self.unit_num, self.start, self.end, self.working_power)

        if self.work_data.get('code') == 200:
            data_points = self.work_data.get('data', {}).get('points', {})
            self.pw_data = data_points.get(self.working_power[0])

        # 检测有功功率测点数据是否为空
        self.check_power_data(self.pw_data)

    # 稳定性分析
    def stabilityAnalysis(self):
        pw_list = []
        for value in self.pw_data.values():
            pw_list = list(value.values())
        matched_pw_list = list(filter(lambda x: x > PW_STABILITY_LIMIT_VALUE, pw_list))

        # 检测机组稳定性
        self.check_stable_operation_data(matched_pw_list, pw_list)

    def preCriterion(self):
        # 单个测点组，取测点组名称
        group_name = self.groups[0]
        # 获取测点组数据
        self.group_data = self.groups_data.get(group_name)
        # 获取测点组包含的全部测点列表
        self.points = list(self.group_data.keys())

        self.threshold_dict = self.threshold.get(group_name, {})

        if not self.threshold_dict:
            # 查询预警值
            thresholds = get_threshold_config(self.unit_num, group_name)
            # 检查是否为空
            self.check_threshold_data(thresholds)

            # 预警值处理
            for point in self.points:
                # 查找匹配的阈值
                threshold = next((threshold for threshold in thresholds if threshold.get('points_id') == point), None)
                if threshold:
                    self.threshold_dict[point] = {
                        DNY_HIGH: threshold.get(DNY_HIGH),
                        DNY_LOW: threshold.get(DNY_LOW),
                        ALERT_HIGH_1: threshold.get(ALERT_HIGH_1),
                        ALERT_HIGH_2: threshold.get(ALERT_HIGH_2),
                        ALERT_LOW_1: threshold.get(ALERT_LOW_1),
                        ALERT_LOW_2: threshold.get(ALERT_LOW_2)
                    }

        # 检测动态阈值条数与测点条数是否匹配
        self.check_threshold_number_data(self.threshold_dict, self.points)

        # 检查动态阈值是否为0，动态阈值为0表示未进行赋值
        for dny_value in self.threshold_dict.values():
            self.check_threshold_zero_data(dny_value)

    def criterion_avg_dny_high(self):
        self.preCriterion()

        self.check_param_zero_data(self.param)

        algorithm_param = self.param[0]

        flag = False
        for point in self.points:
            datadict = self.group_data.get(point)
            # 检查数据是否存在
            self.check_points_data(datadict)

            datalist = list(datadict.values())
            avg = get_mean(datalist)
            dny_high = self.threshold_dict.get(point).get(DNY_HIGH)
            if avg > algorithm_param * dny_high:
                flag = True
                break

        self.diagnosis_result.update({"value": flag})

        return self.diagnosis_result

    def criterion_prob_dny_high(self):
        self.preCriterion()

        self.check_param_zero_data(self.param)

        algorithm_param = self.param[0]

        probs = []
        for point in self.points:
            datadict = self.group_data.get(point)
            # 检查数据是否存在
            self.check_points_data(datadict)

            datalist = list(datadict.values())
            limit = self.threshold_dict.get(point).get(DNY_HIGH)
            matched_datalist = list(filter(lambda x: x > algorithm_param * limit, datalist))
            prob = len(matched_datalist) / len(datalist)
            probs.append(prob)

        final_prob = max(probs)

        self.diagnosis_result.update({"value": final_prob})

        return self.diagnosis_result

    def criterion_prob_dny_low(self):
        self.preCriterion()

        self.check_param_zero_data(self.param)

        algorithm_param = self.param[0]

        probs = []
        for point in self.points:
            datadict = self.group_data.get(point)
            # 检查数据是否存在
            self.check_points_data(datadict)

            datalist = list(datadict.values())
            limit = self.threshold_dict.get(point).get(DNY_LOW)
            matched_datalist = list(filter(lambda x: x < algorithm_param * limit, datalist))
            prob = len(matched_datalist) / len(datalist)
            probs.append(prob)

        final_prob = max(probs)

        self.diagnosis_result.update({"value": final_prob})

        return self.diagnosis_result

    def criterion_prob_nonzero(self):
        self.preCriterion()

        probs = []
        for point in self.points:
            datadict = self.group_data.get(point)
            # 检查数据是否存在
            self.check_points_data(datadict)

            datalist = list(datadict.values())
            matched_datalist = list(filter(lambda x: x != 0, datalist))
            prob = len(matched_datalist) / len(datalist)
            probs.append(prob)

        final_prob = max(probs)

        self.diagnosis_result.update({"value": final_prob})

        return self.diagnosis_result

    def criterion_prob_above_min(self):
        self.preCriterion()

        self.check_param_zero_data(self.param)

        algorithm_param = self.param[0]

        probs = []
        for point in self.points:
            datadict = self.group_data.get(point)
            # 检查数据是否存在
            self.check_points_data(datadict)

            datalist = list(datadict.values())
            minimum = min(datalist)
            matched_datalist = list(filter(lambda x: x - minimum > algorithm_param, datalist))
            prob = len(matched_datalist) / len(datalist)
            probs.append(prob)

        final_prob = max(probs)

        self.diagnosis_result.update({"value": final_prob})

        return self.diagnosis_result

    def criterion_prob_alert_high(self):
        self.preCriterion()

        probs = []
        for point in self.points:
            datadict = self.group_data.get(point)
            # 检查数据是否存在
            self.check_points_data(datadict)

            datalist = list(datadict.values())
            limit = self.threshold_dict.get(point).get(ALERT_HIGH_1)
            matched_datalist = list(filter(lambda x: x >= limit, datalist))
            prob = len(matched_datalist) / len(datalist)
            probs.append(prob)

        final_prob = max(probs)

        self.diagnosis_result.update({"value": final_prob})

        return self.diagnosis_result

    def criterion_check_empty(self):
        self.preCriterion()

        flag = self.get_default_value()

        for point in self.points:
            if self.group_data.get(point) is None or len(self.group_data.get(point)) == 0:
                flag = 1

        self.diagnosis_result.update({"value": flag })

        return self.diagnosis_result

    def criterion_custom(self, calc_method):
        self.preCriterion()

        final_prob = calc_method(self)

        self.diagnosis_result.update({"value": final_prob })

        return self.diagnosis_result


    # 检查测点组是否为空
    def check_group_number(self, groups):
        if groups is None or len(groups) == 0:
            raise GroupNumError(groups, self.diagnosis_result)
        return groups

    def check_group_data(self, groups_data):
        if groups_data is None or len(groups_data) == 0:
            raise GroupDataError(groups_data, self.diagnosis_result)
        return groups_data

    def check_stable_operation_data(self, matched_pw_list, pw_list):
        if len(matched_pw_list) / len(pw_list) < PW_STABILITY_FACTOR:
            raise StableOperationError(len(matched_pw_list) / len(pw_list), self.diagnosis_result)
        return len(matched_pw_list) / len(pw_list)

    # 测点组预警值配置不存在
    def check_threshold_data(self, thresholds):
        if thresholds is None or len(thresholds) == 0:
            return ThresholdDataError(thresholds, self.diagnosis_result)
        return thresholds

    # 检测动态阈值条数与测点条数是否匹配
    def check_threshold_number_data(self, threshold, points):
        if len(threshold) != len(points):
            raise ThresholdError([len(threshold), len(points)], self.diagnosis_result)
        return [len(threshold), len(points)]

    # 检查动态阈值是否为0，动态阈值为0表示未进行赋值
    def check_threshold_zero_data(self, dny_value):
        if dny_value.get(DNY_HIGH, 0) == 0 or dny_value.get(DNY_LOW, 0) == 0:
            raise ThresholdZeroError(dny_value, self.diagnosis_result)
        return dny_value

    def check_points_data(self, points_data):
        if points_data is None:
            raise PointsError(points_data, self.diagnosis_result)
        return points_data

    def check_power_data(self, pw_data):
        if pw_data is None or len(pw_data) == 0 or any(value is None for value in pw_data.values()):
            raise PowerDataError(pw_data, self.diagnosis_result)
        return pw_data

    def check_param_zero_data(self, param):
        if param is None or len(param) == 0:
            raise ParamZeroError(param, self.diagnosis_result)
        return param

    def check_judge_config_data(self, config):
        if config is None:
            raise JudgeConfigError(config, self.diagnosis_result)
        return config