import copy
import os
import shutil
import tempfile
from contextlib import contextmanager


@contextmanager
def folder_context(folder_path=''):
    """
    上下文管理器：进入时操作 文件，退出时自动删除整个文件夹。
    """
    try:
        if not folder_path:
            folder_path = tempfile.gettempdir() + os.sep + "api_test_folder"

        os.makedirs(folder_path, exist_ok=True)  # 如果文件夹不存在则创建
        yield folder_path  # 暴露文件夹路径给 with 块
    finally:
        # 退出时删除文件夹及其内容
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

@contextmanager
def header_manager(headers, update_headers=None, remove_headers=None):
    """
    Context manager for managing headers.

    :param headers: The original headers dictionary.
    :param update_headers: A dictionary of headers to update or add.
    :param remove_headers: A list of header keys to remove.
    """

    # Make a copy of the original headers
    original_headers = copy.copy(headers)

    # Update headers with new values
    if update_headers:
        for key, value in update_headers.items():
            headers[key] = value

    # Remove specified headers
    if remove_headers:
        for key in remove_headers:
            if key in headers:
                del headers[key]
    try:
        yield
    finally:
        # Restore the original headers
        headers.clear()
        headers.update(original_headers)




