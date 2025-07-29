import os
from typing import Any

import allure

from giga_auto.base_class import Response
from giga_auto.parse.parse_base import ParseBase
from giga_auto.conf.settings import settings


class ParseStep(ParseBase):

    def __init__(self, step_data, case_variables, business, db):
        self.variables = case_variables
        self.step_data = step_data
        self.business = business
        self.business.db = db

    def parse_params(self, key='params'):
        params = self.step_data.get(key, {})
        if isinstance(params, str):
            self.step_data[key] = self.traversal_assignments(params)
        else:
            self.traversal_assignments(params)

    def parse_files(self):
        files = self.step_data.get('files', None)
        if files is None:
            return {}
        file_values=[]
        for k, path in files.items():
            if isinstance(path,str): path=[path]
            # path不是列表就是字符串，传错了会直接抛异常文件不存在
            for p in path:
                p=os.path.join(settings.Constants.STATIC_DIR, p.replace('\\', os.sep).replace('/', os.sep))
                file_values.append((k,(os.path.basename(p),open(p, 'rb'))))
        return {'files': file_values}

    def parse_validate(self, response):
        """处理断言，先处理数据库或者变量取值，在处理content开头的值"""
        validate = self.step_data.get('validate', [])
        self.traversal_assignments(validate)
        self._content_validate(validate, response)
        self.step_data['validate'] = validate

    def _content_validate(self, validates, res):
        """根据规则解析"""
        res = Response(res)
        for val in validates:
            for k, v in val.items():
                actual = v[0]
                if isinstance(actual, str):
                    if actual.startswith('content'):
                        actual = getattr(res, actual)
                    elif actual.startswith('response.'):
                        actual = getattr(res, actual.split('.', 1)[-1])
                v[0] = actual

    def parse_extract(self, response):
        """获取吐出变量更新到variables"""
        response = Response(response)
        extract = self.step_data.get('extract', {})
        for k, v in extract.items():
            allure.attach(f'获取变量key:{k},值路径：{v}')
            extract[k] = getattr(response, v)
        self.variables.update(extract)

    def parse_function(self):
        """解析除接口请求之外的步骤,只可能调用business函数,必须以function作为步骤标识"""
        self.step_data['function'] = self.traversal_assignments(self.step_data['function'])
        return self.step_data['function']

    def get_func(self, value: str) -> Any:
        method = getattr(self.business, value)
        if method:
            return method
        else:
            raise AttributeError(f'business未获取到属性{value}')

    def get_var(self, value: str) -> Any:
        mid_value = self.variables
        if '.' in value:
            for k in value.split('.'):
                if not k.strip(): continue
                mid_value = mid_value[k] if isinstance(mid_value, dict) else mid_value[int(k)]
        else:
            mid_value = mid_value[value]
        return mid_value


if __name__ == '__main__':
    from common.db_utils import DBInitUtils

    wdb = DBInitUtils().init_db('WMS_US')
    variables = {
        "find_unload_port": "select id,warehouse_id,unloading_port,status from tbl_warehouse_unloading_port  where unloading_port=%s and warehouseId=%s",
        "delete_unload_port": "delete from tbl_warehouse_unloading_port where unloading_port= %s and warehouseId=%s",
        "unloadingPort": "autotest123456",
        "warehouseId": 666,
        "anotherWarehouseId": 777
    }
    test_add_unloading_port = {
        "setup": "${execute($delete_unload_port,$unloadingPort)}",
        "params": {
            "unloadingPort": "$unloadingPort",
            "warehouseId": "$warehouseId"
        },
        "desc": "正常新增卸货口",
        "teardown": None,
        "validate": [
            {
                "eq": [
                    "content.msg",
                    "success"
                ]
            },
            {
                "eq": [
                    "content.code",
                    "0000"
                ]
            },
            {
                "eqLength": [
                    "${fetchall($find_unload_port,$unloadingPort,$warehouseId)}",
                    1
                ]
            }
        ]
    }
