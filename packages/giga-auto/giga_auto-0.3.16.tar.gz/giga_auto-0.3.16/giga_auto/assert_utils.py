import json
import datetime
import logging

import allure

from giga_auto.constants import CaseTypeEnum
from giga_auto.assert_class.excel_assert import AssertExcel
from giga_auto.expect_utils import ExpectUtils
from giga_auto.base_class import SingletonMeta
from giga_auto.utils import to_date, deep_sort

logger = logging.getLogger('giga')


class AssertUtils(AssertExcel, metaclass=SingletonMeta):
    compare_map = {
        'eq': 'assert_equal', 'gt': 'assert_greater', 'ge': 'assert_greater_equal',
        'lt': 'assert_less', 'le': 'assert_less_equal', 'ne': 'assert_not_equal',
        'in': 'assert_in', 'not_in': 'assert_not_in', 'Length': 'assert_length',
        'eqFormat': 'assert_format', 'length': 'assert_length'
    }

    @staticmethod
    def assert_equal(actual, expected, msg=None):
        """
        断言两个值相等
        """
        assert actual == expected, f"{msg or ''} \nAssert Equal Failed: Expected:{expected},Actual:{actual}"

    @staticmethod
    def assert_not_equal(actual, expected, msg=None):
        """
        断言两个值不相等
        """
        assert actual != expected, f"{msg or ''} \nAssert Not Equal Failed: Expected:{expected},Actual:{actual}"

    @staticmethod
    def assert_in(expected, actual, msg=None):
        """
        断言actual在expected中，支持字符串和列表
        """
        if isinstance(actual, list) and isinstance(expected, list):
            assert all(item in actual for item in expected), \
                f"{msg or ''} \nAssert In Failed: Expected items {expected} not all in Actual:{actual}"
        else:
            assert expected in actual, \
                f"{msg or ''} \nAssert In Failed: Expected:{expected}"

    @staticmethod
    def assert_not_in(expect, actual, msg=None):
        """
        断言actual不在expected中
        """
        if isinstance(actual, list) and isinstance(expect, list):
            assert all(item not in actual for item in expect), \
                f"{msg or ''} \nAssert In Failed: Expected items {expect} not all in Actual:{actual}"
        else:
            assert expect not in actual, f"{msg or ''} \nAssert Not In Failed"

    @staticmethod
    def assert_not_none(actual, msg=None):
        assert actual is not None, f"{msg or ''} \nAssert Not None Failed: Actual:{actual}"

    @staticmethod
    def assert_is_none(actual, msg=None):
        assert actual is None, f"{msg or ''} \nAssert Not None Failed: Actual:{actual}"

    @staticmethod
    def assert_true(actual, msg=None):
        assert actual is True, f"{msg or ''} \nAssert True Failed: Actual:{actual}"

    @staticmethod
    def assert_false(actual, msg=None):
        assert actual is False, f"{msg or ''} \nAssert False Failed: Actual:{actual}"

    @staticmethod
    def assert_equal_ignore_type(actual, expected, msg=None):
        try:
            # 尝试将两者作为数值进行比较
            assert float(actual) == float(
                expected), f"{msg or ''} \nAssert Equal (Ignore Type) Failed: Expected:{expected}, Actual:{actual}"
        except (ValueError, TypeError):
            # 如果无法转成 float，则回退到字符串比较
            assert str(actual) == str(
                expected), f"{msg or ''} \nAssert Equal (Ignore Type) Failed: Expected:{expected}, Actual:{actual}"

    @staticmethod
    def assert_is_empty(value, msg=None):
        assert value in (None, '', [], {}, set()), f"{msg or ''} \nAssert Empty Failed: Actual:{value}"

    @staticmethod
    def assert_not_empty(value, msg=None):
        """
        断言值不为空
        """
        assert value not in [None, '', [], {}, set()], f"{msg or ''} \nAssert Not Empty Failed: Actual:{value}"

    @staticmethod
    def assert_deep_not_empty(value, msg=None):
        """
        断言值不为空，支持基本类型、字符串、列表、字典、集合以及列表中包含字典的情况。
        排除 None、空字符串、空列表、空字典、空集合。
        注意：该方法只支持最多二层嵌套的字典和列表。
        断言失败：
        ex: [[0,1],[None,1]] ，[None,1]
        [{a:1,b:2},{a:None,b:2}]，{a:None,b:2}
        {"a": None, "b": 2}
        """
        empty_conditions = [None, '', [], {}, set()]

        def check_value(val):
            # 如果是列表，检查每个元素
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, (list, dict)):
                        check_value(item)  # 递归检查
                    assert item not in empty_conditions, msg or "Value is empty"  # 断言元素不为空
            # 如果是字典，检查每个键值对
            elif isinstance(val, dict):
                for key, item in val.items():
                    if isinstance(item, (list, dict)):
                        check_value(item)  # 递归检查
                    assert item not in empty_conditions, msg or f"Key '{key}' value is empty"  # 断言值不为空
            # 对于其他类型，直接检查值
            assert val not in empty_conditions, msg or "Value is empty"

        # Start checking the value
        check_value(value)

    @staticmethod
    def assert_greater(actual, expected, msg=None):
        """
        断言actual大于expected
        """
        assert actual > expected, f"{msg or ''} \nAssert Greater Failed: Expected greater than {expected}, Actual:{actual}"

    @staticmethod
    def assert_greater_equal(actual, expected, msg=None):
        """
        断言actual大于expected
        """
        assert actual >= expected, f"{msg or ''} \nAssert Greater Failed: Expected greater or equal {expected}, Actual:{actual}"

    @staticmethod
    def assert_less(actual, expected, msg=None):
        """
        断言actual小于expected
        """
        assert actual < expected, f"{msg or ''} \nAssert Less Failed: Expected less than {expected}, Actual:{actual}"

    @staticmethod
    def assert_less_equal(actual, expected, msg=None):
        """
        断言actual小于expected
        """
        assert actual <= expected, f"{msg or ''} \nAssert Less Failed: Expected less or equal {expected}, Actual:{actual}"

    @staticmethod
    def assert_between(actual, min_value, max_value, msg=None):
        """
        断言actual在min_value和max_value之间
        """
        assert min_value <= actual <= max_value, f"{msg or ''} \nAssert Between Failed: Expected between {min_value} and {max_value}, Actual:{actual}"

    @staticmethod
    def assert_starts_with(actual, prefix, msg=None):
        """
        断言actual以prefix开头
        """
        assert str(actual).startswith(
            str(prefix)), f"{msg or ''} \nAssert Starts With Failed: Expected prefix {prefix}, Actual:{actual}"

    @staticmethod
    def assert_ends_with(actual, suffix, msg=None):
        """
        断言actual以suffix结尾
        """
        assert str(actual).endswith(
            str(suffix)), f"{msg or ''} \nAssert Ends With Failed: Expected suffix {suffix}, Actual:{actual}"

    @staticmethod
    def assert_regex_match(actual, pattern, msg=None):
        import re
        assert re.match(pattern,
                        str(actual)), f"{msg or ''} \nAssert Regex Match Failed: Expected pattern {pattern}, Actual:{actual}"

    @staticmethod
    def assert_date_equal(expected, actual):
        """
        通用日期比较方法，支持 str、datetime、date 类型，精确度到天
        """
        expected_date = to_date(expected)
        actual_date = to_date(actual)

        assert expected_date == actual_date, f"Expected: {expected_date}, Actual: {actual_date}"

    @staticmethod
    def assert_time_range(start_time, end_time, actual_time, msg=None):
        """
        断言时间范围
        """
        start_time = to_date(start_time)
        end_time = to_date(end_time)
        actual_time = to_date(actual_time)
        assert start_time <= actual_time <= end_time, f"{msg or ''} \nAssert Time Range Failed: Expected between {start_time} and {end_time}, Actual:{actual_time}"

    @staticmethod
    def assert_date_has_overlap(period1, period2, label='', msg=None):
        # 将字符串转换为 datetime 对象
        if isinstance(period1, str):
            period1 = period1.split(label)
        if isinstance(period2, str):
            period2 = period2.split(label)
        start1, end1 = map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"), period1)
        start2, end2 = map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"), period2)
        # 判断是否有交集
        assert max(start1, start2) <= min(end1,
                                          end2), f"{msg or ''} \nAssert Date Has Overlap Failed: Expected no overlap, Actual:{period1} and {period2}"

    @staticmethod
    def assert_sorted_data(data, reverse=False):
        """
        利用sorted()辅助函数，用于判断数据是否按顺序排列
        """
        assert data == sorted(data, reverse=reverse)

    # 判断两个列表排序后是否相等
    @staticmethod
    def assert_sorted_equal(actual, expected, msg=None):
        """
        断言实际值和预期值在排序后是否相等，适用于多种数据结构（包括嵌套结构）

        :param actual: 实际值（支持 list, dict, tuple, set 等）
        :param expected: 预期值
        :param msg: 自定义错误信息
        :raises AssertionError: 如果排序后不相等
        """
        # 对数据进行深度排序
        actual_sorted = deep_sort(actual)
        expected_sorted = deep_sort(expected)
        assert actual_sorted == expected_sorted, \
            f"{msg or ''} \nSorted data mismatch:\nActual: {actual_sorted}\nExpected: {expected_sorted}"

    @staticmethod
    def assert_msg_code(response, expect):
        """统一校验响应码"""
        expect_msg = expect.get('msg') or expect.get('message')
        resp_msg = response.get('msg') or response.get('message')
        expect_code = expect.get('code')

        assert expect_code == response.get('code'), f"响应码校验失败: 预期 {expect_code}, 实际 {response.get('code')}"
        assert expect_msg == resp_msg, f"响应消息校验失败: 预期 {expect_msg}, 实际 {resp_msg}"

    @staticmethod
    def assert_msg(resp: dict, expect, msg=""):
        """通用响应msg断言"""
        response_msg = resp.get('msg') or resp.get('message')
        if isinstance(expect, str):
            expect_msg = expect
        elif isinstance(expect, dict):
            expect_msg = expect.get('msg') or expect.get('message')
        else:
            raise TypeError("expect参数类型错误")
        AssertUtils.assert_equal(response_msg, expect_msg,
                                 f"resp_msg: {response_msg},expect_msg: {expect_msg}, {msg}响应msg不符")

    @staticmethod
    def assert_code(resp: dict, expect: dict, msg=""):
        """通用响应code断言"""
        AssertUtils.assert_equal(resp.get('code'), expect.get('code'),
                                 f"resp_code: {resp.get('code')},expect_code: {expect.get('code')}, {msg}响应code不符")

    @staticmethod
    def assert_length(actual, expected, assert_method):
        """
        断言长度,如果一个为列表，另一个为数字或字符串等
        """
        if type(actual) != type(expected):
            actual_len = len(actual) if isinstance(actual, (list,tuple)) else int(actual)
            expected_len = len(expected) if isinstance(expected, (list,tuple)) else int(expected)
        else:
            actual_len, expected_len = len(actual), len(expected)
        assert_method(actual_len, expected_len, msg=f'比较actual:{actual},expected:{expected}长度相等')

    def assert_format(self, actual, expected):
        if isinstance(actual, str): actual = json.loads(actual)
        if isinstance(expected, str): expected = json.loads(expected)
        diff_key = self.diff_data(actual, expected)
        logger.info(f'格式断言actual:{actual},expected:{expected},diff_key:{diff_key}')
        # 如果diff_key为空，代表无任何格式异常，通过校验
        self.assert_is_empty(diff_key, msg=f'格式断言actual:{actual},expected:{expected}')

    def assert_format_value(self,actual, expected):
        if isinstance(actual, str): actual = json.loads(actual)
        if isinstance(expected, str): expected = json.loads(expected)
        diff_key = self.diff_data(actual, expected,check_value=True)
        logger.info(f'格式断言actual:{actual},expected:{expected},diff_key:{diff_key}')
        # 如果diff_key为空，代表无任何格式异常，通过校验
        self.assert_is_empty(diff_key, msg=f'格式断言actual:{actual},expected:{expected}')

    def diff_data(self, actual, expect, path='$', diff_key=None, check_value=False):
        if diff_key is None: diff_key = []
        if isinstance(expect, list):
            if type(actual) != list:
                diff_key.append(f'{path}该路径类型不一致')
            new_path = path + '.0'
            if isinstance(expect[0], list):
                self.diff_data(actual[0], expect[0], path=new_path, diff_key=diff_key, check_value=check_value)
            elif isinstance(expect[0], dict):
                self.diff_data(actual[0], expect[0], path=new_path, diff_key=diff_key, check_value=check_value)
            elif check_value and not actual[0]:
                diff_key.append(f'{new_path}该路径值不能为空')
        elif isinstance(expect, dict):
            if type(actual) != dict:
                diff_key.append(f'{path}该路径类型不一致')
            for k, v in expect.items():
                new_path = path + '.' + str(k)
                if k not in actual:
                    diff_key.append(f'{new_path}该路径key不存在期望格式中')
                elif isinstance(v, dict):
                    self.diff_data(actual[k], v, new_path, diff_key, check_value=check_value)
                elif isinstance(v, list):
                    self.diff_data(actual[k], v, new_path, diff_key, check_value=check_value)
                elif check_value and not actual[k]:
                    diff_key.append(f'{new_path}该路径值不能为空')
        return diff_key

    def get_assert_method(self, key):
        if self.compare_map.get(key, None) is not None:
            return self.compare_map[key]
        if getattr(self, key, None) is not None:
            return key
        return None

    def map_assert_method(self, key: str):
        """
        eqLength
        """
        method = self.get_assert_method(key)
        if method is None:
            compare, value = self.get_assert_method(key[:2]), self.get_assert_method(key[2:])
            self.assert_not_none(compare, msg=f'获取断言方法{key}异常')
            self.assert_not_none(value, msg=f'获取断言方法{key}异常')
            logger.info(f'获取方法:{compare},{value}')
            return getattr(self, compare), getattr(self, value)
        logger.info(f'获取方法{method}')
        return getattr(self, method)

    def validate(self, validates):
        for val in validates:
            for k, v in val.items():
                actual, expected,*others = v
                methods = self.map_assert_method(k)
                logger.info(f'断言关键字:{k}获取断言方法成功,actual:{actual},expected:{expected}')
                allure.attach(f'断言关键字:{k}获取断言方法成功,actual:{actual},expected:{expected}', '开始断言')
                if isinstance(methods, tuple):
                    methods[1](actual, expected, methods[0],*others)
                else:
                    methods(actual, expected,*others)


class ListQueryValidator:

    def __int__(self, data_key='data', records_key='records', total_key='total'):
        self.data_key = data_key
        self.records_key = records_key
        self.total_key = total_key

    @staticmethod
    def validate(scene_type, response, expect=None, payload=None,
        data=None,records=None,total=None):
        """
        通用列表查询验证入口
        :param scene_type: 场景类型
            - 'emptyFilter' 空筛选项查询
            - 'exactMatch' 精确查询
            - 'fuzzySearch' 模糊查询
            - 'emptyResult' 空结果查询
            - 'timeRange' 查询创建时间范围
        :param response: 接口响应字典
        :param expect: 预期值配置
                value: 需要验证的值/字段
                total: 预期总数
                startTime: 开始时间（仅对查询创建时间有效）
                endTime: 结束时间（仅对查询创建时间有效）
        :param payload: 请求参数（模糊查询需传递）
        :param payload: 判断是否为时间范围查询
        :param data: 响应数据字典，默认为response中的data
        :param records: 响应记录列表，默认为response中的records
        :param total: 响应总数，默认为response中的total
        """
        data = data or response.get('data', {})
        records = records or data.get('records', []) or data.get('data', [])
        total = total or data.get('total', 0)
        strategies = {
            CaseTypeEnum.emptyFilter: lambda: ListQueryValidator._validate_empty_filter(records, total, expect),
            CaseTypeEnum.exactMatch: lambda: ListQueryValidator._validate_exact_match(records, total, expect, payload),
            CaseTypeEnum.fuzzySearch: lambda: ListQueryValidator._validate_fuzzy_search(records, expect, payload),
            CaseTypeEnum.emptyResult: lambda: ListQueryValidator._validate_empty_result(records, total),
            CaseTypeEnum.timeRange: lambda: ListQueryValidator._validate_time_range(records, expect, payload),
        }
        if scene_type not in strategies:
            raise ValueError(f"未知的场景类型: {scene_type}")
        return strategies[scene_type]()

    @staticmethod
    def _expected_fields(expect, payload, key='checkValueField'):
        """
        获取checkValueField字段
        :return:
        yaml配置示:
        expect:
            checkValueField:  #检查值不为空字段key
                - text
                - value
        当checkValueField字段值为'&payload'时，表示使用payload中的字段:示例如下：
        expect:
            checkValueField: &payload
        """
        check_value_field = expect.get(key, {})
        # 兼容精确匹配时入参和返回值字段完全一致的场景,无需额外定义一遍checkValueField
        if check_value_field == '&payload':
            check_value_field = payload
        return check_value_field

    @staticmethod
    def _validate_empty_filter(records, total, expect):
        """空筛选项验证
        yaml配置示例:
        expect:
            checkValueField:  #检查值不为空字段key
                - text
                - value
            checkField: #检查key存在,value允许为空
                - remark
                - relationOrder
        """
        assert records, "空筛选项查询结果不能为空"
        AssertUtils.assert_true(total > 0, "空筛选项查询结果应大于0")
        check_value_field = expect.get('checkValueField', [])  # 需要检查值不为空字段key
        check_field = expect.get('checkField', [])
        assert check_value_field or check_field, "空筛选项查询需配置至少一个检查字段"
        if check_value_field:
            ExpectUtils.assert_fields(records[0], check_value_field, check_value=True, subset=True,
                                      msg=f"空筛选项查询结果字段不符")
        if check_field:
            ExpectUtils.assert_fields(records[0], check_field, check_value=False, subset=True,
                                      msg=f"空筛选项查询结果字段不符")

    @staticmethod
    def _validate_exact_match(records, total, expect, payload=None):
        """精确匹配验证(输入参数的查询)
        """
        expected_total = expect.get('total', 1)
        # 校验总数,如果预期总数为-1表示不定长，则不进行校验
        if int(expected_total) != -1:
            AssertUtils.assert_equal(total, expected_total, "精确查询总数不符")
            AssertUtils.assert_equal(len(records), expected_total, "返回记录数不符")
        else:
            AssertUtils.assert_greater(total, 0, "精确查询结果不能为空")
            AssertUtils.assert_greater(len(records), 0, "返回记录数不符")
        # 获取期待值
        expected_equal_fields = ListQueryValidator._expected_fields(expect, payload)
        expected_grater_fields = ListQueryValidator._expected_fields(expect, payload, key='checkGraterField')
        expected_less_fields = ListQueryValidator._expected_fields(expect, payload, key='checkLessField')
        assert expected_equal_fields or expected_grater_fields or expected_less_fields, "精确查询需配置至少一个检查字段"
        for record in records:
            for field, expected_value in expected_equal_fields.items():
                AssertUtils.assert_equal(record.get(field), expected_value, f"字段 {field} 值不匹配")

            for field, expected_value in expected_grater_fields.items():
                AssertUtils.assert_greater(record.get(field), expected_value, f"字段 {field} 值不匹配")

            for field, expected_value in expected_less_fields.items():
                AssertUtils.assert_less(record.get(field), expected_value, f"字段 {field} 值不匹配")

    @staticmethod
    def _validate_fuzzy_search(records, expect, payload):
        """模糊查询验证"""
        # 获取期待值
        expected_fields = ListQueryValidator._expected_fields(expect, payload)
        # 校验总数
        AssertUtils.assert_greater(len(records), 0, "模糊查询结果不能为空")
        # 遍历所有记录进行校验
        for record in records:
            for field, value in expected_fields.items():
                actual_value = str(record.get(field, ''))
                AssertUtils.assert_in(str(value), actual_value, f"模糊匹配失败,字段: {field} ")

    @staticmethod
    def _validate_empty_result(records, total):
        """空结果验证"""
        assert total in [0, None], f"空结果总数应等于0或者null, 当前值: {total}"
        assert records in [[], None], f"记录列表应为空，或者为null, 当前值: {records}"

    @staticmethod
    def _validate_time_range(records, expect, payload):
        """创建时间范围验证
        time_key: 时间范围字段名列表，默认['startTime', 'endTime']
        为了支持时间独立查询或者组合查询，yaml中expect断言时间单独配置checkDateTime。
        如checkDateTime和payload一直,则直接使用payload中的时间字段进行断言。
        yaml配置示例:
        expect:
            checkDateTime:
                startTime: 2023-10-01 00:00:00  #如果使用payload中的时间字段，
                endTime: 2023-10-31 23:59:59
            timeField: createTime
        #支持直接校验payload中的时间字段
         expect:
            checkDateTime: $payload
            timeField: createTime
        """

        check_date_fields = ListQueryValidator._expected_fields(expect, payload, 'checkDateTime')
        time_range = check_date_fields.values()
        time_field = expect.get('timeField')
        assert time_range, "时间范围字段不能为空"
        assert time_field, "需要校验的时间字段不能为空"

        # 将时间字符串转换为 datetime 对象，为了确认时间大小
        datetime_range = [to_date(time_value) for time_value in time_range]

        # 判断datetime_range中的两个时间大小,分别赋值为start_time 和end_time
        if datetime_range[0] > datetime_range[1]:
            datetime_range[0], datetime_range[1] = datetime_range[1], datetime_range[0]

        start_time, end_time = datetime_range

        # 3. 遍历记录并验证时间范围
        for record in records:
            # 获取记录中的时间字段值
            time_field_str = record.get(time_field)
            if not time_field_str:
                raise ValueError(f"接口返回缺少字段 '{time_field}'")
            # 将记录时间转为 datetime 对象
            record_time = to_date(time_field_str)
            # 4. 调用断言方法（传递 datetime 对象）
            AssertUtils.assert_time_range(start_time, end_time, record_time, '时间范围不符')
