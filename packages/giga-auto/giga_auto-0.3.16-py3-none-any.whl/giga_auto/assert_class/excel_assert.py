from giga_auto.file_attr.excel_attr import ExcelAttr


class AssertExcel:

    @staticmethod
    def assert_excel_headers(filepath, expected: list, msg=None):
        """断言excel表头，如模版文件断言表头是否正确"""
        assert ExcelAttr(
            filepath).headers == expected, f'{msg or "检查文件表头"} \nExcel{filepath} Headers Failed{expected}'

    @staticmethod
    def assert_excel_rows_num(filepath, rows_num, sub_length: int = 1, msg=None):
        """断言文件数据行数"""
        assert ExcelAttr(filepath).data_row_num(
            sub_length) == rows_num, f'{msg or "检查文件行的长度"}\n Excel{filepath} rows_num Failed {rows_num}'

    @staticmethod
    def assert_excel_rows_data(filepath, expected: list, start=1, end=None, msg=None):
        """断言数据，默认从第一行取到最后一行,end=None会自动取到最后一行"""
        assert ExcelAttr(filepath).row_data(
            start,end) == expected, f'{msg or "检查文件行的数据"}\n Excel{filepath} rows_data Failed {expected}'
