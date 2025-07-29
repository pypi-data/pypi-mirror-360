#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
import logging
from functools import wraps
from datetime import timezone
from dateutil.relativedelta import relativedelta

from diskcache import Cache

from pywander.path import mkdirs
from pywander.unique_key import build_unique_key
from pywander.datetime import timestamp_current, timestamp_to_dt, dt_current
from pywander.path import normalized_path, to_absolute_path

logger = logging.getLogger(__name__)


class CacheDB(object):
    """
    """
    _instance = None

    def __new__(cls, cache_path):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._cache = Cache(cache_path)
        return cls._instance

    @property
    def cache(self):
        return self._cache

    @property
    def directory(self):
        return self._cache.directory

    def set(self, key, value, **kwargs):
        """
        设置缓存值
        """
        self.cache.set(key, value, **kwargs)

    def get(self, key, **kwargs):
        """
        获取缓存值
        """
        return self.cache.get(key, **kwargs)

    def add(self, key, value, **kwargs):
        """
        初始化缓存值
        """
        return self.cache.add(key, value, **kwargs)

    def has_key(self, key):
        """
        检查key是否存在
        """
        return key in self.cache



def get_cachedb(root='.'):
    """
    从某个文件夹下获取缓存数据库 默认是当前文件夹下
    """
    cachedb_path = to_absolute_path(os.path.join(root, 'cachedb'))

    if not os.path.exists(cachedb_path):
        mkdirs(cachedb_path)

    cachedb = CacheDB(cachedb_path)

    return cachedb


def get_default_cachedb_path(app_name='test'):
    """
    获取缓存文件路径
    """
    return normalized_path(os.path.join('~', 'Pywander', app_name, 'cachedb'))


def get_default_cachedb(app_name='test'):
    """ 
    默认的cachedb对象
    """
    cachedb_path = get_default_cachedb_path(app_name=app_name)

    if not os.path.exists(cachedb_path):
        mkdirs(cachedb_path)

    cachedb = CacheDB(cachedb_path)

    return cachedb


def default_use_cache_callback(cachedb, cache_data, func, args, kwargs, use_cache_oldest_dt=None):
    timestamp = cache_data.get('timestamp', timestamp_current())
    data_dt = timestamp_to_dt(timestamp)

    if use_cache_oldest_dt is None:
        target_dt = dt_current() - relativedelta(seconds=86400 * 14)  # default 14 days
    else:
        target_dt = use_cache_oldest_dt

    if data_dt.tzinfo is None:
        data_dt.replace(tzinfo=timezone.utc)
    if target_dt.tzinfo is None:
        target_dt.replace(tzinfo=timezone.utc)

    # too old then we will re-excute the function
    if data_dt < target_dt:
        key = cache_data.get('key')
        data = func(*args, **kwargs)

        if data:
            cache_data['data'] = data
            cache_data['timestamp'] = str(timestamp_current())

            cachedb.set(key, cache_data)
        else:
            raise Exception(f'execute func {func.__name__} got no data return.')


def func_cache(cachedb, use_key='', use_cache_oldest_dt=None,
               use_cache_callback=default_use_cache_callback):
    """
    this decorator will decorator a function and try to return a value based on
    cache.
    """

    def _mydecorator(func):
        @wraps(func)
        def wraper_func(*args, **kwargs):
            if not use_key:
                key = build_unique_key(func.__name__, *args, **kwargs)
            else:
                key = use_key

            cache_data = cachedb.get(key)

            if cache_data:
                logger.info('read data from cache ')
                use_cache_callback(cachedb, cache_data, func, args, kwargs,
                                   use_cache_oldest_dt=use_cache_oldest_dt)
                return cache_data.get('data')
            else:
                logger.info(f'get data from excute func')
                data = func(*args, **kwargs)

                if data:
                    cache_data = {
                        'data': data,
                        'key': key,
                        "timestamp": str(timestamp_current())
                    }

                    cachedb.set(key, cache_data)
                    return data
                else:
                    raise Exception(
                        f'execute func {func.__name__} got no data return.')

        return wraper_func

    return _mydecorator
