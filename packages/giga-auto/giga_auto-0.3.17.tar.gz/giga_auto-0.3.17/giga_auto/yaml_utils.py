import os
import yaml
from typing import Any, Dict, List


class YamlUtils:
    def __init__(self, yaml_file: str,check_exists: bool = True):
        """
        初始化 YamlUtils 类
        :param yaml_file: YAML 文件路径
        """
        if check_exists:
            if not os.path.exists(yaml_file):
                raise FileNotFoundError(f"{yaml_file} : 文件不存在")
        self.yaml_file = yaml_file
    def read(self) -> Dict[str, Any]:
        """
        读取 YAML 文件并返回数据
        :return: YAML 文件内容（字典格式）
        """
        with open(self.yaml_file, "rb") as f:
            return yaml.safe_load(f) or {}

    def read_all(self) -> List[Dict[str, Any]]:
        """
        读取 YAML 文件中的所有文档（适用于多文档 YAML）
        :return: 包含多个 YAML 文档的列表
        """

        with open(self.yaml_file, "rb") as f:
            return  list(yaml.safe_load_all(f))

    def write(self, data: Dict[str, Any]) -> None:
        """
        覆盖写入 YAML 文件
        :param data: 要写入的字典数据
        """
        with open(self.yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def update(self, key: str, new_value: Any) -> None:
        """
        更新 YAML 文件中的某个键值对
        :param key: 需要更新的键
        :param new_value: 新值
        """
        data = self.read()
        if key in data:
            data[key] = new_value
            self.write(data)
        else:
            raise KeyError(f"Key '{key}' not found in the YAML file.")


    def append(self, new_data: Dict[str, Any]) -> None:
        """
        追加数据到 YAML 文件（适用于列表结构）
        :param new_data: 要追加的字典数据
        """
        data = self.read()
        if isinstance(data, list):
            data.append(new_data)
        else:
            raise TypeError("YAML 文件的根结构必须是列表才能进行追加操作")
        self.write(data)

    def delete(self, key: str) -> None:
        """
        删除 YAML 文件中的某个键
        :param key: 需要删除的键
        """
        data = self.read()
        if key in data:
            del data[key]
            self.write(data)
        else:
            raise KeyError(f"Key '{key}' not found in the YAML file.")
