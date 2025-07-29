import importlib
import sys
import os
import logging

from pywander.path import normalized_path
from pywander.json import get_json_data

"""
明了胜过隐晦，除了极个别的私密配置，其他所有配置请在程序文件开头明明白白地声明出来，如果觉得太多了可以放在另外一个 `config.py`文件下，这个
`config.py` 文件下面简称为配置文件。

私密配置请参考 `.env` 环境变量的那一套做法。

所有配置的key为大写字母形式，不得以下划线开头。

配置加载之后的实际效果和在代码开头声明的效果应该是等同的。

一个典型的用法如下所示：

from pywander.config import load_config, get_default_config_path
APP_NAME = 'test'
config_path = get_config_path(APP_NAME)
globals().update(load_config(config_path))

"""
logger = logging.getLogger(__name__)


def import_from_path(module_name, file_path, saved_module_name=None):
    spec = importlib.util.spec_from_file_location(module_name, file_path)

    if saved_module_name is None:
        saved_module_name = module_name
    if spec is None:
        raise ImportError("构建模块失败")

    module = importlib.util.module_from_spec(spec)
    sys.modules[saved_module_name] = module
    spec.loader.exec_module(module)
    return module


def lazy_import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    spec.loader = importlib.util.LazyLoader(spec.loader)

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


DEFUALT_CONFIG = {
    "INKSCAPE_COMMAND_PATH": "C:\\Program Files\\Inkscape\\bin",
    "PANDOC_COMMAND_PATH": "C:\\Program Files\\Pandoc",
}


def load_home_config(app_name='test', module_name='config'):
    """
    加载配置文件

    所有配置的key为大写字母形式，不得以下划线开头。
    """
    config_path = get_config_path(app_name=app_name)

    saved_module_name = f'pywander_{app_name}_{module_name}'
    try:
        config = import_from_path(module_name, config_path, saved_module_name=saved_module_name)
    except ImportError as e:
        logger.warning(f"构建模块{module_name}失败: {config_path}")
        return {}
    except FileNotFoundError:
        logger.warning(f'can not found config.py in: {config_path} ')
        return {}

    new_config = {}
    for k in dir(config):
        if k:
            if k[0] == '_':
                continue

            if k.isupper():
                v = getattr(config, k)
                new_config[k] = v

    return new_config


def get_config_path(app_name='test'):
    """
    获取配置文件路径
    """
    return normalized_path(os.path.join('~', 'Pywander', app_name, 'config.py'))


def load_current_config(config_name='pywander.json'):
    if not os.path.exists(config_name):
        return {}

    config = get_json_data(config_name)

    new_config = {}
    for k in config:
        if k:
            if k[0] == '_':
                continue

            if k.isupper():
                v = config.get(k)
                new_config[k] = v

    return new_config


def load_all_config():
    """
    现在加载默认配置
    先加载home文件夹下的配置文件
    再加载当前文件夹下的配置文件
    """
    config = DEFUALT_CONFIG
    config.update(load_home_config())
    config.update(load_current_config())
    return config
