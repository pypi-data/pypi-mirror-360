from typing import Any

from giga_auto.parse.parse_base import ParseBase


class ParseCase(ParseBase):
    def __init__(self, case_data, case_variables, business, wms_db):
        self.variables = case_variables
        self.case_data = case_data
        self.business = business
        self.business.db = wms_db

    def parse_prepare(self):
        self._parse_variables()
        self._parse_setup()

    def _parse_variables(self):
        """
        先处理整个yml文件的variables，再处理case_variables,variables已在参数化全部copy了，
        意味着每个用例之间的variables都是独立的，最后把所有参数合在一块
        """
        variables = self.variables
        self.variables = variables.pop("feature_variables")
        case_variables = variables.pop("case_variables")
        self.traversal_assignments(self.variables)
        self.traversal_assignments(case_variables)
        # 以case_variables变量为高优先级
        self.variables.update(case_variables)
        variables.update(self.variables) # 处理完case的variables,供后续parse_step使用

    def _parse_setup(self):
        """处理setup方法"""
        setup = self.case_data.get("setup", [])
        self.traversal_assignments(setup)
        self.case_data["setup"] = setup

    def parse_teardown(self):
        """处理teardown方法"""
        teardown = self.case_data.get("teardown", {})
        self.traversal_assignments(teardown)
        self.case_data["teardown"] = teardown

    def get_func(self, value: str) -> Any:
        method = getattr(self.business, value)
        if method:
            return method
        else:
            raise AttributeError(f"business未获取到属性{value}")

    def get_var(self, value: str) -> Any:
        return self.variables[value]


if __name__ == "__main__":
    # from common.db_utils import DBInitUtils
    # from apis_request.wms_us import business
    # from common.decorate import Response
    # db = DBInitUtils().init_db('WMS_US')
    variables = {
        "find_unload_port": "select id,warehouse_id,unloading_port,status from tbl_warehouse_unloading_port  "
        "where unloading_port=%s and warehouseId=%s",
        "delete_unload_port": "delete from tbl_warehouse_unloading_port where unloading_port= %s and warehouseId=%s",
        "unloadingPort": "autotest123456",
        "warehouseId": 666,
        "anotherWarehouseId": 777,
    }
    test_add_unloading_port = {
        "setup": "${execute($delete_unload_port,$unloadingPort)}",
        "params": {"unloadingPort": "$unloadingPort", "warehouseId": "$warehouseId"},
        "desc": "正常新增卸货口",
        "teardown": None,
        "validate": [
            {"eq": ["content.msg", "success"]},
            {"eq": ["content.code", "0000"]},
            {"eqLength": ["${fetchall($find_unload_port,$unloadingPort,$warehouseId)}", 1]},
        ],
    }
    print(variables["find_unload_port"])
