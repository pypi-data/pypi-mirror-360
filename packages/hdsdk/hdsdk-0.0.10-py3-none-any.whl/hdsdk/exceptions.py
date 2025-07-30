
from hdsdk.conf.common_config import UNPROCESSABLE_ENTITY


class GroupNumError(Exception):
    def __init__(self, value, diagnosis_result):
        self.value = value
        self.message = f"获取不到判据绑定测点组。"
        self.code = UNPROCESSABLE_ENTITY
        self.result = diagnosis_result
        super().__init__(self.message)


class GroupDataError(Exception):
    def __init__(self, value, diagnosis_result):
        self.value = value
        self.code = UNPROCESSABLE_ENTITY
        self.result = diagnosis_result
        self.message = f"测点组历史数据不存在。"
        super().__init__(self.message)


class PowerDataError(Exception):
    def __init__(self, value, diagnosis_result):
        self.value = value
        self.code = UNPROCESSABLE_ENTITY
        self.result = diagnosis_result
        self.message = f"有功功率历史数据不存在。"
        super().__init__(self.message)


# 这是机组启动判断
class StableOperationError(Exception):
    def __init__(self, value, diagnosis_result):
        self.value = value
        self.code = UNPROCESSABLE_ENTITY
        self.result = diagnosis_result
        self.message = f"机组不在启机阶段，不进行数据分析"
        super().__init__(self.message)


class ThresholdDataError(Exception):
    def __init__(self, value, diagnosis_result):
        self.value = value
        self.code = UNPROCESSABLE_ENTITY
        self.result = diagnosis_result
        self.message = f"测点组预警值配置不存在。"
        super().__init__(self.message)

class ThresholdError(Exception):
    def __init__(self, value, diagnosis_result):
        self.value = value
        self.code = UNPROCESSABLE_ENTITY
        self.result = diagnosis_result
        self.message = f"动态阈值条数与测点条数不匹配。"
        super().__init__(self.message)


class ThresholdZeroError(Exception):
    def __init__(self, value, diagnosis_result):
        self.value = value
        self.code = UNPROCESSABLE_ENTITY
        self.result = diagnosis_result
        self.message = f"动态阈值限值为0，无效阈值。"
        super().__init__(self.message)


class PointsError(Exception):
    def __init__(self, value, diagnosis_result):
        self.value = value
        self.message = f"获取不到判据绑定测点数据。"
        self.code = UNPROCESSABLE_ENTITY
        self.result = diagnosis_result
        super().__init__(self.message)

class ParamZeroError(Exception):
    def __init__(self, value, diagnosis_result):
        self.value = value
        self.code = UNPROCESSABLE_ENTITY
        self.result = diagnosis_result
        self.message = f"判据参数值为空"
        super().__init__(self.message)


class JudgeConfigError(Exception):
    def __init__(self, value, diagnosis_result):
        self.value = value
        self.code = UNPROCESSABLE_ENTITY
        self.result = diagnosis_result
        self.message = f"故障判据配置不存在"
        super().__init__(self.message)