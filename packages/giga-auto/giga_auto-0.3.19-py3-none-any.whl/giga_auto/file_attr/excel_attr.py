import os
from typing import List

import pandas as pd


class ExcelAttr:

    def __init__(self, excel_path: str, sheet_name: str = None):
        self.excel_path = excel_path
        self.sheet_name = sheet_name
        self._df = None

    @property
    def df(self):
        if self._df is None:
            file_path = self.excel_path
            sheet_name = self.sheet_name
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件未找到：{file_path}")
            if file_path.endswith(".csv"):
                # 读取 CSV 文件
                df = pd.read_csv(file_path, header=None)
            else:
                # 如果 sheet_name 为空，则读取第一个 sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name or 0, header=None)
                if df.empty:
                    raise ValueError("Excel 文件为空")
            self._df = df
        return self._df

    @property
    def row_num(self) -> int:
        """返回excel的函数"""
        return self.df.shape[0]

    @property
    def column_num(self) -> int:
        """返回excel列数"""
        return self.df.shape[1]

    @property
    def headers(self) -> list:
        """返回header值，格式参考：['仓库Code', 'Item Code', '托盘码数量']"""
        if self.row_num == 0:
            return []
        return self.df.iloc[0].values.tolist()

    @property
    def data(self) -> List[list]:
        """返回除第一行data值，格式参考：[['CA2', 'M022310765147', '3'], ['CA2', 'M022310765146', 1]]"""
        if self.row_num <=1:
            return []
        return self.df.iloc[1:].values.tolist()

    def data_row_num(self,sub_length: int=1) -> int:
        """返回excel除表头的行数,默认表头只有一行"""
        return self.df.shape[0] - sub_length

    def row_data(self, start=0, end=None) -> List[list]:
        """
        默认返回所有数据，包裹请求头，格式如下：
            [['仓库Code', 'Item Code', '托盘码数量'], ['CA2', 'M022310765147', '3'], ['CA2', 'M022310765146', 1]]
        """
        if self.row_num <= start:
            return []
        return self.df.iloc[start:end or self.row_num].values.tolist()
