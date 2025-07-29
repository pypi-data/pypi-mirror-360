import re
import sys
from typing import Union, Any


class ParseBase:
    pattern_func = re.compile(r'(\$\{(.+?)\((.*?)\)\})')
    pattern_func_var = re.compile('(\$\{([a-zA-Z0-9_\.]+?)\})')
    pattern_var = re.compile(r'(\$([a-zA-Z0-9_\.]+))')

    def _parse_func(self, value: str):
        """
        解析 ${func($var1,${var2})}
        """
        items = self.pattern_func.findall(value)
        for item in items:
            replace_str, func, var = item
            args, kwargs = self._parse_var(var)
            if replace_str == value:
                value = self.get_func(func)(*args, **kwargs)
            else:
                value = value.replace(replace_str, str(self.get_func(func)(*args, **kwargs)))
        return value

    def _parse_var(self, values: str) -> Union[list, str, tuple]:
        """
        解析获取变量，
        """
        frame = sys._getframe(1)  # 1表示上一级调用栈
        co_name = frame.f_code.co_name  # 获取上一级调用栈函数名
        if '_parse_func' == co_name:  # 函数变量以逗号分割，需分开解析
            value = values.split(',')
            args = []
            kwargs = {}
            for var in value:
                if '=' in var:
                    k, v = var.split('=')
                    kwargs[k] = self._parse_single_var(v)
                else:
                    var = self._parse_single_var(var)
                    args.append(var)
            return args, kwargs
        else:
            return self._parse_single_var(values)

    def _parse_single_var(self, value: str) -> str:
        """解析单个字符串变量，格式如${var1},$var2"""
        if not isinstance(value, str):
            return value
        value = value.strip()
        v = self.pattern_var.findall(value) + self.pattern_func_var.findall(value)
        for k in v:
            replace_str, new_k = k
            if replace_str == value:
                return self.get_var(new_k)
            value = value.replace(replace_str, str(self.get_var(new_k)))
        return value

    def traversal_assignments(self, data):
        if isinstance(data, list):
            for idx, value in enumerate(data):
                if isinstance(value, (list, dict)):
                    self.traversal_assignments(value)
                elif isinstance(value, str):
                    value = self.traversal_assignments(value)
                    data[idx] = value
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    self.traversal_assignments(value)
                elif isinstance(value, str):
                    value = self.traversal_assignments(value)
                    data[key] = value
        elif isinstance(data, str):
            data = self._parse_func(data)
            data = self._parse_var(data)
        return data

    def get_func(self, value: str) -> Any:
        raise NotImplementedError('get_func is not implemented')

    def get_var(self, value: str) -> Any:
        """
        根据字符串从variables拿到变量
        :param value:
        :return:
        """
        raise NotImplementedError('get_var is not implemented')


if __name__ == '__main__':
    p = ParseBase()
    s = '12324334${query_sql_count(${sql.find_area1}  456,123) }5678${query_sql_count(123$sql.find_area ,123) }'
    s = '$sql.find_area'
    print(p._parse_single_var(s))
    # p.parse_var('${sql.find_area},$.abc')
