import os
import tempfile
from contextlib import contextmanager

import pandas as pd


class FileUtils:

    @staticmethod
    def extract_and_count_files(file_path, extract_to=''):
        import zipfile
        import tarfile

        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
                # 只统计文件，不包括文件夹
                file_count = sum(1 for f in zip_ref.namelist() if not f.endswith('/'))

        elif file_path.endswith('.tar.gz') or file_path.endswith('.tgz'):
            with tarfile.open(file_path, 'r:gz') as tar_ref:
                tar_ref.extractall(path=extract_to)
                # 只统计文件
                file_count = sum(1 for m in tar_ref.getmembers() if m.isfile())
        else:
            raise ValueError("不支持的压缩文件格式，仅支持 .zip 和 .tar.gz/.tgz")
        return file_count

    @staticmethod
    def read_pdf_pypdf(path):
        import PyPDF2
        text = ""
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        return text

    @staticmethod
    def read_file_rows(file_path: str, num_rows: int = 1, sheet_name: str = ""):
        """
        读取 Excel 或 CSV 文件的前 num_rows 行数据
        :param file_path: 文件路径（支持 .xlsx, .xls, .csv）
        :param num_rows: 需要读取的行数（默认 1 行）
        :param sheet_name: 指定读取的 Excel sheet 名称（仅 Excel 文件有效）
        :return: 前 num_rows 行的数据列表
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path, sheet_name=sheet_name or 0, header=None)
        elif ext == ".csv":
            df = pd.read_csv(file_path, header=None)
        else:
            raise ValueError(f"不支持的文件类型: {ext}")

        if df.empty:
            raise ValueError("文件为空")

        num_rows = min(num_rows, len(df))
        return df.iloc[:num_rows].values.tolist()

    @contextmanager
    def download_file(self,response, filename):
        """
        上下文管理器：保存 Excel 响应内容到本地，并在退出时自动清理

        :param response: `requests` 的响应对象，需确保 response.content 是 Excel 文件
        :param filename: 自定义保存的文件名
        :return: 返回本地 Excel 文件路径
        """
        if response.status_code != 200:
            raise RuntimeError(f"下载失败，状态码：{response.status_code}")

        # 获取当前项目的临时目录
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(response.content)

        try:
            yield file_path  # 返回文件路径
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)  # 退出时自动删除文件
