import re
from typing import Union
import requests
from giga_auto.logger import log
DEFAULT_TIMEOUT = 60


class RequestBase(object):

    def __init__(self, base_url: str = '', expect_code=200):
        """
        :param base_url: The base URL of the API
        """
        self.base_url = base_url.rstrip('/')
        self._session = requests.Session()
        self._session.timeout = DEFAULT_TIMEOUT
        self.expect_code = expect_code
    @log
    def _request(self, method, url, **kwargs):
        """
        处理请求方法和URL中的占位符
        """
        placeholders = re.findall(r'<:(\w+)>', url)
        for placeholder in placeholders:
            if placeholder in kwargs:
                url = url.replace(f'<:{placeholder}>', str(kwargs.pop(placeholder)))
            else:
                url = url.replace(f'/<:{placeholder}>', '')
        if not url.startswith('http'):
            url = f'{self.base_url}{url}' if 'route' in self.base_url else f'{self.base_url}/{url.lstrip("/")}'
        return self._session.request(method.upper(), url, **kwargs)

    def request(self, method, url, **kwargs) -> Union[dict, list, str]:
        return_json = kwargs.pop('return_json',True)
        response = self._request(method, url, **kwargs)
        if 'code' in response.json():
            if response.json()['code'] != self.expect_code:
                raise Exception(f"Response error: {response}")
        if return_json:
            return response.json()
        return response

    def get(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('PUT', url, **kwargs)

    def delete(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('DELETE', url, **kwargs)

    def patch(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('PATCH', url, **kwargs)
