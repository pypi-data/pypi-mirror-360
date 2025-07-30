from collections import Counter


class ExpectUtils:

    @staticmethod
    def assert_fields(resp_data: dict, expect_fields, msg=None,subset=False,check_value=False):
        """
        校验接口返回字段是否符合预期
        :param resp_data: 接口返回数据
        :param expect_fields: 预期字段
        :param msg: 错误信息
        :param subset: 是否为子集
        :param check_value: 是否校验字段值为空
        """
        #
        if isinstance(expect_fields, list):
            resp_keys = list(resp_data.keys())
            if subset:
                # 允许部分字段匹配
                assert set(expect_fields).issubset(resp_keys), (
                    f"response data:{resp_data}\n expect_fields:{expect_fields} \n {msg}")
            else:
                assert Counter(resp_keys) == Counter(
                    expect_fields), f"response data:{resp_data}\n expect_fields:{expect_fields} \n {msg}"

            if check_value:
                empty =  [None, '', [], {}, set()]
                empty_fields = [field for field in expect_fields if resp_data.get(field) in empty]
                assert not empty_fields, f"字段值为空: {', '.join(empty_fields)}"

        elif isinstance(expect_fields, dict):
            for key, value in expect_fields.items():
                assert key in resp_data, f"Key '{key}' not found in response data. {msg}"
                if isinstance(value, dict) and isinstance(resp_data[key], dict):
                    # 递归检查嵌套字典
                    ExpectUtils.assert_fields(resp_data[key], value, msg)
                else:
                    assert resp_data[key] == value, (
                        f"response data:{resp_data}\n expect_fields:{expect_fields} \n {msg}")

