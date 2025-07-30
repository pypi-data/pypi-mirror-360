import functools
import json
import logging
import os
from logging import config

logging.getLogger("requests").setLevel(logging.WARNING)
import yaml


def response_log(func=None, logger=None):
    if logger is None:
        logger = logging.getLogger(__name__)

    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"API Function: {func.__name__}")
            result = func(*args, **kwargs)
            logger.info(f"Response: {result}\n")
            return result

        return wrapper

    return decorator if func is None else decorator(func)


def log(func=None, *, verbosity=1, my_logger=None):
    if my_logger is None:
        my_logger = logging.getLogger(__name__)

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if verbosity > 0:
                    base_url = getattr(args[0], 'base_url', '')
                    method = args[1] if len(args) > 1 else ''
                    endpoint = args[2] if len(args) > 2 else ''
                    url = f"{base_url}{endpoint}"

                    my_logger.info(f"URL: {url}")
                    print(f"URL: {url}")
                    my_logger.info(f"Method: {method}")
                    print(f"Method: {method}")
                    for key in ['params', 'data', 'json', 'files']:
                        if key in kwargs and kwargs[key] is not None:
                            value = kwargs[key]
                            if key in ['data', 'json']:
                                value = json.dumps(value, indent=4, ensure_ascii=False)
                            my_logger.info(f"{key}: {value}")
                            print(f"{key}: {value}")
            except Exception as e:
                print(f"API Response Error: {e}")
                my_logger.error(f"API Response Error: {e}")
                raise
            return result

        return wrapper

    return decorator if func is None else decorator(func)


class NoUrllib3Filter(logging.Filter):
    def filter(self, record):
        # 检查记录的消息中是否包含指定的文本
        if record.name == 'urllib3.connectionpool' or record.levelname == 'DEBUG' or record.module == 'connectionpool' or record.msg == 'Starting new HTTPS connection (%d): %s:%s':
            return False
        if record.levelname == 'DEBUG' and 'Starting new HTTPS connection' in record.getMessage():
            return False
        return True


def setup_logging(log_dir, log_config_path, default_level=logging.INFO):
    try:
        filename = 'api_auto_test.log'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if os.path.exists(os.path.join(log_dir, filename)):
            os.remove(os.path.join(log_dir, filename))
        if os.path.exists(log_config_path):
            with open(log_config_path, 'rt') as f:
                config = yaml.safe_load(f.read())
            # config['handlers']['file_handler']['filename'] = os.path.join(log_dir, "{}.log".format(Config.CURRENT_DATE))
            config['handlers']['file_handler']['filename'] = os.path.join(log_dir, filename)

            # 添加自定义过滤器到日志配置中
            config['filters'] = {
                'no_urllib3': {
                    '()': NoUrllib3Filter,
                }
            }

            # 将过滤器添加到处理器
            config['handlers']['file_handler']['filters'] = ['no_urllib3']
            if 'console' in config['handlers']:
                config['handlers']['console']['filters'] = ['no_urllib3']

            logging.config.dictConfig(config)

        else:
            logging.basicConfig(level=default_level)
        return logging.getLogger(__name__)
    except Exception as e:
        print(e)
        return logging.getLogger(__name__)


def db_log(func, logger=None):
    if logger is None:
        logger = logging.getLogger(__name__)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            print(f"数据库操作失败: {e}")
            for i, arg in enumerate(args[1:]):
                logger.error(f"数据库参数{i}: {arg}")
                print(f"数据库参数{i}: {arg}")
            raise

    return wrapper

# logger = setup_logging()
