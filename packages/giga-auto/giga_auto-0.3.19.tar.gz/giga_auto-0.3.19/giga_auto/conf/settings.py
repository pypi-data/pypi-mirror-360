import os
import importlib

class LazySettings(object):

    def __init__(self):
        self._settings = None

    def _set_business(self, name):
        if name == 'business':
            return self._get_module(name)
        return None

    def _set_assert_class(self, name):
        if name == 'assert_class':
            return self._get_class(name,'giga_auto.assert_utils.AssertUtils')
        return None

    def _set_login_class(self,name):
        if name=='login_class':
            return self._get_class(name,'common.login.Login')
        return None

    def _get_module(self,name,default=None):
        """必须"""
        module_path:str = getattr(self._settings, name.upper(),default)
        if module_path is None:
            raise ValueError('%s is not set in settings' % name.upper())
        return importlib.import_module(module_path)

    def _get_class(self,name,default=None):
        assert_class_path:str = getattr(self._settings, name.upper(), default)
        if assert_class_path is None:
            raise ValueError('%s is not set in settings' % name.upper())
        module, class_obj = assert_class_path.rsplit('.', 1)
        return getattr(importlib.import_module(module), class_obj)

    def _set_main(self, name):
        return (self._set_business(name)
                or self._set_assert_class(name)
                or self._set_login_class(name)
                or getattr(self._settings, name))

    def __getattr__(self, name):
        if self._settings is None:
            module_path = os.environ['GIGA_SETTINGS_MODULE']
            self._settings = importlib.import_module(module_path)
        return self._set_main(name)


settings = LazySettings()
