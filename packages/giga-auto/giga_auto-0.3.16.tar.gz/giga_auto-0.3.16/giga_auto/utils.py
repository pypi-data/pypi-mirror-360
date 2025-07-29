import copy
import datetime
import functools
import hashlib
import logging
import os
import shutil
import string
import subprocess
import time
import random
import traceback
from urllib.parse import unquote
from collections import defaultdict
from contextlib import contextmanager
from typing import List, Dict, Any

import pytz
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5

import re

from giga_auto.yaml_utils import YamlUtils
from giga_auto.conf.settings import settings
from datetime import date


def random_str(length):
    """
    Generate a random string of digits of a given length.
    :param length: Length of the string of digits to generate
    :return: Random string of digits
    """
    # if not 3 <= length <= 6:
    #     raise ValueError("Length must be between 3 and 6.")

    # Generate a random number at the given length
    lower_bound = 10 ** (length - 1)
    upper_bound = 10 ** length - 1
    random_number = random.randint(lower_bound, upper_bound)

    return str(random_number)


def regular_match(pattern, content, isDoTAll=False):
    """
    regular match
    :param rule: regular rule
    """
    if isDoTAll:
        pattern = re.compile(pattern, re.DOTALL)
    else:
        pattern = re.compile(pattern)
    match = pattern.search(content)
    if match:
        return match.group(1)
    else:
        raise Exception("not pattern")


def format_path(dirs: list):
    """
    format path with os.sep
    """
    return os.sep + os.sep.join(dirs) + os.sep


def gen_random_string(str_len):
    """ generate random string with specified length
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(str_len)
    )


def delete_existing_files_or_dirs(paths):
    """
    Deletes files or directories if they exist. Accepts a single path or a list of paths.
    """
    if not isinstance(paths, list):
        paths = [paths]  # Ensure paths is always a list

    for path in paths:
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            else:
                logging.error(f"No action taken: {path} does not exist.")
        except Exception as e:
            logging.error(f"Failed to delete {path}: {e}")


def get_date(days_interval, type=1, str_format='%Y-%m-%d'):
    """
    获取指定日期的字符串格式
    :param days_interval: 间隔天数
    :param type: 1-之前的日期，2-之后的日期
    """
    current_date = datetime.date.today()
    if type == 1:
        # 计算之前的日期
        days = current_date - datetime.timedelta(days=days_interval)
    elif type == 2:
        # 计算之后的日期
        days = current_date + datetime.timedelta(days=days_interval)
    else:
        raise ValueError("Invalid type. Type must be 1 or 2.")
    formatted_date = days.strftime(str_format)
    return formatted_date


def step_msg(msg):
    """
    steps decorator
    :param msg:
    :return:
    """

    def decorator_step(func):
        @functools.wraps(func)
        def wrapper_step(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                func_name = func.__name__
                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                params_repr = ", ".join(args_repr + kwargs_repr)
                error_msg = (
                    f"\nStep Error - {msg}\n"
                    f"Function: {func_name}\n"
                    f"Params: {params_repr}\n"
                    f"Fail Reason: {e}\n"
                    f"Traceback:\n{traceback.format_exc()}"
                )
                raise

        return wrapper_step

    return decorator_step


def retry(reruns=6, reruns_delay=10):
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            last_exception = None
            for attempt in range(1, reruns + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < reruns:
                        time.sleep(reruns_delay)
                        print(f"Retrying {func.__name__} (attempt {attempt + 1}/{reruns_delay})")
                    else:
                        raise last_exception

        return wrapper_retry

    return decorator_retry


def generate_md5():
    """
    获取随机字符串-暂时用于阿里云上传文件
    """
    current_time = int(time.time() * 1000)

    random_number = random.random()
    message = f"{current_time}{random_number}"

    # 计算MD5哈希值
    md5_hash = hashlib.md5(message.encode()).hexdigest()

    return md5_hash


def md5_brute_force(hash_to_crack, known_strings):
    """
    解密md5
    """
    for string in known_strings:
        if hashlib.md5(string.encode('utf-8')).hexdigest() == hash_to_crack:
            return string
    return None


def convert_dollar_to_float(currency_str):
    """
    将货币字符串转换为浮点数。
    支持的货币符号包括：美元 ($)、人民币 (￥)、欧元 (€)、英镑 (£)
    :param currency_str: 货币字符串，例如 "$1,234.56"
     :return: 转换后的浮点数，例如 1234.56
    """
    if not currency_str:
        return 0

    currency_symbols = ['CAN$', '$', '￥', '€', '£']
    symbol = None

    # 查找货币符号
    for sym in currency_symbols:
        if sym in currency_str:
            symbol = sym
            break

    if symbol is None:
        raise ValueError(f"不支持的货币符号:{symbol}")

    # 移除货币符号和逗号
    clean_str = currency_str.replace(symbol, '').replace(',', '')
    return float(clean_str)


def get_pytz_time(timezone='US/Pacific'):
    """
    获取指定时区的时间，支持字符型时区名称和整型时区偏移量。
    :param timezone: 时区，可以是字符型（时区名称）或整型（UTC偏移量）
    :return: 指定时区的时间
    """
    if isinstance(timezone, int):
        # 如果是整型，表示固定的UTC偏移量（分钟数）
        offset = pytz.FixedOffset(timezone)
        current_time_utc = datetime.datetime.now(pytz.utc)
        current_time_with_offset = current_time_utc.astimezone(offset)
    elif isinstance(timezone, str):
        # 如果是字符型，表示时区名称
        local_tz = pytz.timezone(timezone)
        current_time_utc = datetime.datetime.now(pytz.utc)
        current_time_with_offset = current_time_utc.astimezone(local_tz)
    else:
        raise ValueError("timezone 参数必须是整型或字符型")

    formatted_time = current_time_with_offset.isoformat()
    return formatted_time


def format_pem(encoded_str, pem_type="PUBLIC KEY"):
    # 定义头和尾
    pem_header = f"-----BEGIN {pem_type}-----"
    pem_footer = f"-----END {pem_type}-----"

    # 将字符串按64字符分割
    pem_body = '\n'.join([encoded_str[i:i + 64] for i in range(0, len(encoded_str), 64)])

    # 拼接整个PEM内容
    pem_content = f"{pem_header}\n{pem_body}\n{pem_footer}"

    return pem_content


def rsa_encrypt(plain_text, public_key):
    """
    RSA加密
    :param plain_text: 明文
    :param public_key: 公钥
    :return: 密文
    """
    rsa_key = RSA.importKey(public_key)
    cipher = Cipher_pkcs1_v1_5.new(rsa_key)
    plain_text = base64.b64encode(cipher.encrypt(plain_text.encode("utf-8")))
    return plain_text.decode("utf-8")


def round_half_up(value, decimals=2):
    """
    四舍五入 满5进1
    """
    factor = 10 ** decimals
    return round(value * factor + 0.0001) / factor


def unzip_file(zip_file_path, extractall_to_path):
    """
    解压文件
    """
    import zipfile
    # 解压 ZIP 文件
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extractall_to_path)
        print(f'{zip_file_path}解压缩完成到 {extractall_to_path}')


def encrypt_email(email):
    """
    对邮箱进行加密处理，将用户名的部分字符替换为通配符。
    例如：apiflow0001@gmail.com -> api***@gmail.com
    """
    # 定义正则表达式匹配邮箱
    pattern = r'^([^@]{3})[^@]*(?=@)(@.+)$'
    match = re.match(pattern, email)
    if match:
        return f"{match.group(1)}***{match.group(2)}"
    else:
        return "Invalid email format"


def allure_report(report_path, report_html):
    # 执行命令 allure generate
    allure_cmd = "allure generate %s -o %s --clean" % (report_path, report_html)
    # subprocess.call
    try:
        subprocess.call(allure_cmd, shell=True)
        print('测试报告已更新')
    except:
        raise


def gen_auth_headers(token):
    """
    生成认证头
    """
    return {"authorization": f"Bearer {token}"}


def parse_case_data(case_file: str, add_info: bool = False):
    case_data = YamlUtils(case_file).read()
    cases = defaultdict(list)
    other_key = defaultdict(dict)
    for key, case_config in case_data.items():
        for sub_key, value in case_config.items():
            if isinstance(value, list) and sub_key == 'cases':
                for case in value:
                    case_items = [value for _, value in case.items()]
                    cases[key].append(tuple(case_items))
            else:
                other_key[key].update({sub_key: value})
    return cases if not add_info else (cases, other_key)


def parse_data(file, add_info=False):
    """
    :param file: 测试py文件路径或者data文件路径
    :param add_info: 如果为true返回两个值，否则返回一个值
    """
    if file.endswith('.py'):
        file = right_replace(file)
    return parse_case_data(file, add_info)


def right_replace(s):
    """
    取代最右边的字符串,仅用于取代文件路径
    例：s=testcase/wms_us_web/test_unloading_port.py
    return: testcase/wms_us_web/data_unloading_port.yml
    """
    replace_list = [('.py', '.yml'), ('test', 'data')]
    for old, new in replace_list:
        index = s.rfind(old)
        if index == -1:
            return s
        s = s[:index] + new + s[index + len(old):]
    return s


def extract_values(data: List[Dict[str, Any]], keys: List[str] = None) -> List[tuple]:
    """
    从字典列表中提取指定的 key 对应的 value，返回一个包含这些值的元组列表。
    如果 keys 为空，则提取每个字典中的所有值。

    :param data: 字典列表（如用于 pytest 参数化的数据）
    :param keys: 要提取的 key 列表（为空时提取所有 key）
    :return: 提取的值组成的元组列表
    """
    return [tuple(obj[key] for key in (keys or obj.keys())) for obj in data]


def to_date(obj):
    """
    将 str / datetime / date 类型统一转为 date 类型
    """
    if isinstance(obj, date) and not isinstance(obj, datetime.datetime):
        return obj
    elif isinstance(obj, datetime.datetime):
        return obj.date()
    elif isinstance(obj, str):
        # 兼容 "2024-03-17" 和 "2024-03-17 00:00:00"
        try:
            return datetime.datetime.strptime(obj, "%Y-%m-%d").date()
        except ValueError:
            return datetime.datetime.strptime(obj, "%Y-%m-%d %H:%M:%S").date()
    else:
        raise TypeError(f"Unsupported type for date conversion: {type(obj)}")


def deep_sort(data):
    """
    递归地对数据结构进行排序，支持嵌套结构。
    支持类型：dict, list, tuple, set 及其组合。
    """
    if isinstance(data, dict):
        return sorted((k, deep_sort(v)) for k, v in data.items())
    elif isinstance(data, list):
        return sorted(deep_sort(item) for item in data)
    elif isinstance(data, tuple):
        return tuple(deep_sort(item) for item in data)
    elif isinstance(data, set):
        return sorted(deep_sort(item) for item in data)
    else:
        return data


def retry_login(times=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            for i in range(times):
                try:
                    result = func(self, *args, **kwargs)
                except Exception as e:
                    self.kwargs['retry_login'] = False
                    raise e
                if result == settings.UNAUTHORIZED:  # 认证失败重登一次
                    self.kwargs['retry_login'] = True
                else:  # 认证成功直接返回
                    self.kwargs['retry_login'] = False
                    return result
            raise Exception(f"重试登录失败，请检查登录信息")

        return wrapper

    return decorator


def download_file(response, filename):
    """
    上下文管理器：保存 Excel 响应内容到本地，并在退出时自动清理

    :param response: `requests` 的响应对象，需确保 response.content 是 Excel 文件
    :param filename: 自定义保存的文件名
    :return: 返回本地 Excel 文件路径
    """
    if response.status_code != 200:
        raise RuntimeError(f"下载失败，状态码：{response.status_code}")
    # 获取当前项目的临时目录
    temp_dir: str = settings.Constants.TEMP_DIR
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.abspath(os.path.join(temp_dir, unquote(filename)))
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(response.content)
    return file_path
