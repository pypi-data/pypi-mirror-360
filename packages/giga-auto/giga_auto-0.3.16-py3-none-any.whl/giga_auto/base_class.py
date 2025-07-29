"""基础类，最好不要调用其它模块"""
import os
import json
import logging
import inspect
import importlib
from typing import Dict
import allure
import curlify
from giga_auto.yaml_utils import YamlUtils
from giga_auto.conf.settings import settings
from giga_auto.request import RequestBase
from giga_auto.utils import retry_login
from giga_auto.utils import download_file


class SingletonMeta(type):
    """
    单例元类：根据初始化参数区分不同实例
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        args_key = (cls, args, frozenset(kwargs.items()))
        if args_key not in SingletonMeta._instances:
            SingletonMeta._instances[args_key] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[args_key]


class ApiBase(RequestBase):
    def __init__(self, **env):
        self.host = env.get('host', '')
        super().__init__(self.host, env.get('expect_code', 200))
        self.headers = env.get('headers', {})

    def set_headers(self, headers):
        self.headers = headers


class ApiYamlBase(RequestBase,metaclass=SingletonMeta):

    def __init__(self, service=None, account_key="admin", extra_headers: dict = None, **kwargs):
        self.service = service
        self.account_key = account_key
        self.config = settings.admin_config[self.service]
        self.logger = logging.getLogger("giga")
        self.extra_headers = extra_headers or {}
        self.kwargs = kwargs
        super().__init__(base_url=self.config["HOST"], expect_code=kwargs.get('expect_code','0000'))

    @property
    def headers(self) -> Dict[str, str]:
        """登录获取请求头"""
        _headers = settings.login_class().login(
            self.service,
            self.account_key,
            self.kwargs.get("reload_login", False) or self.kwargs.get("retry_login", False),
        )
        return _headers

    @retry_login(times=2)
    def _request(self, method, url, **kwargs):
        headers=self._apply_header(kwargs) # 处理请求头
        kwargs.update({"headers": headers, "method": method, "url": url})
        self._apply_prepare(kwargs) # 处理请求信息的allure数据
        response=super()._request(**kwargs)
        if response.status_code == settings.UNAUTHORIZED and self.kwargs.get('need_login',True):
            # token过期或未认证，默认需要重新登陆，特殊场景不需要，在用例层传入need_login=False，不走登录就不处理重新登陆
            return settings.UNAUTHORIZED  # 返回未认证交于retry_login处理
        self._apply_response(response,kwargs) #处理response相关
        return response

    def _apply_header(self,kwargs):
        """处理下header相关信息"""
        headers = self.extra_headers.copy()
        if self.kwargs.get("need_login",True): # 默认需要登录，获取登录请求头
            headers.update(self.headers)
        self.logger.info(f'获取请求头：{headers}，方法传入请求头:{kwargs.get("headers","{}")}')
        headers.update(kwargs.get("headers") or {})  # 以api方法传入的headers为最高优先级
        return  headers

    @staticmethod
    def _apply_prepare(kwargs):
        """处理请求信息的allure报告"""
        allure_data = kwargs.copy()
        if "files" in kwargs:
            # 处理文件上传allure数据
            files = allure_data["files"]
            file_metadata = []
            for k, value in files:
                file_metadata.append((k, value[0]))
            allure_data["files"] = file_metadata
        allure.attach(body=json.dumps(allure_data), name="接口请求信息", attachment_type=allure.attachment_type.JSON)

    def _apply_response(self, response,kwargs):
        """获取到response后，赋值给request_info请求信息，处理文件、处理allure相关报告"""
        response.request_info = kwargs
        if "files" not in kwargs:
            allure.attach(body=curlify.to_curl(response.request), name="curl命令")
        body = response.text
        attachment_type = allure.attachment_type.TEXT
        if response.headers["Content-Type"] == "application/json":
            attachment_type = allure.attachment_type.JSON
        elif response.headers["Content-Type"] == "application/octet-stream":
            filename = response.headers["Content-Disposition"].split("=")[1]
            filepath = download_file(response, filename)
            response.filepath = filepath  # 下载文件在response存储文件路径，用于后续处理
            body = f"已下载{filename}"
        self.logger.info(body)
        allure.attach(body=body, name="接口返回信息", attachment_type=attachment_type)


class ConfigMeta(type):

    def __init__(cls, name, bases, attrs):
        cls.config={att:attrs[att] for att in attrs['__annotations__']}


class Response:
    """针对新型写法需要针对response或者数据查询数据包一层"""

    def __init__(self, response):
        self.response = response

    def __getitem__(self, item):
        return self.response[item]

    def __repr__(self):
        if hasattr(self.response, 'text'):
            return self.response.text
        else:
            return self.response

    def __getattr__(self, attr):
        attr = attr.split('.')
        mid_value = self.response
        index = 0
        is_has_x = False
        while index < len(attr):
            att = attr[index]
            if att == 'content' and index==0:
                if isinstance(mid_value, dict):
                    mid_value = self.response
                else:
                    mid_value = self.response.json()
            elif is_has_x:
                mid_value = [k[att] for k in mid_value]
            elif att=='$': #返回全部
                mid_value=self.response
            elif isinstance(mid_value, dict):
                mid_value = mid_value[att]
            elif isinstance(mid_value, list):
                if att == '*':
                    is_has_x = True
                    mid_value = mid_value
                else:
                    mid_value = mid_value[int(att)]
            else:
                mid_value = getattr(mid_value, att)
            index += 1
        return mid_value


class OperationApi(metaclass=SingletonMeta):
    """针对新型api层写法统一放在这聚合分发类以及统计api数"""

    def __init__(self):
        self.api_path=settings.Constants.API_ROOT_DIR
        self.project_path=settings.Constants.BASE_DIR
        self._api_map=None

    def statistic_api(self):
        number_map={}
        for service in os.listdir(self.api_path):
            if service not in settings.ServiceKey.config.values():
                continue
            api_root_path=os.path.join(self.api_path, service)
            total=0
            module=self.dynamic_import_api(api_root_path)
            for m in module:
                class_objects=self.get_module_classes(m)
                total+=sum([len(self.get_api_method_name(class_object)) for class_object in class_objects])
            number_map[service]=total
        yaml_path = os.path.join(self.project_path,'cal_api_number.yml')
        YamlUtils(yaml_file=yaml_path,check_exists=False).write(number_map)
        return number_map

    def dynamic_import_api(self,root_path:str):
        module_list=[]
        for root, dirs, files in os.walk(root_path):
            for filename in files:
                if filename.startswith('api') and filename.endswith('.py'):
                    m = os.path.relpath(os.path.join(root, filename), self.project_path).replace(os.sep, '.')[:-3]
                    m = importlib.import_module(m)
                    module_list.append(m)
        return module_list

    @staticmethod
    def get_module_classes(module):
        """获取模块中定义的所有类"""
        return [
            obj for name, obj in inspect.getmembers(module)
            if inspect.isclass(obj) and obj.__module__ == module.__name__
        ]

    @staticmethod
    def get_api_method_name(class_object):
        """获取类有多少个api函数"""
        return [name for name,obj in inspect.getmembers(class_object) if hasattr(obj,'api_url')]

    def check_repeat(self,class_list):
        """检查该service是否存在同名api方法"""
        name_list=[]
        for class_obj in class_list:
            name_list.extend(self.get_api_method_name(class_obj))
        repeat_set = set(filter(lambda x: name_list.count(x) > 1, name_list))
        if len(repeat_set) > 0:
            raise Exception(f"出现重复api方法名，请检查方法：{repeat_set}")

    @property
    def aggregate_api(self):
        """根据api_request目录聚合类，按照目录进行分发,已获取后就不会再获取，直接取self._api_map"""
        if self._api_map is None:
            self._api_map={}
            for filename in os.listdir(self.api_path):
                file_path=os.path.join(self.api_path, filename)
                api_obj_list=[]
                if os.path.isdir(file_path) and filename != '__pycache__':
                    modules=self.dynamic_import_api(file_path)
                    for module in modules:
                        api_obj_list.extend(self.get_module_classes(module))
                    self.check_repeat(api_obj_list)
                    api_request = type('ApiRequest', tuple(api_obj_list), {})
                    self._api_map[filename]=api_request
        return self._api_map


class ApiResponse:

    def __init__(self, response):
        self.response = response
        self._json = None

    def __getitem__(self, item):
        if self._json is None:
            self._json = self.response.json()
        return self._json[item]

    def __getattr__(self, item):
        return getattr(self.response, item)

    def __repr__(self):
        if hasattr(self.response, 'text'):
            return self.response.text
        return str(self.response)

    def get(self, key, default=None):
        return self.response.json().get(key, default)
