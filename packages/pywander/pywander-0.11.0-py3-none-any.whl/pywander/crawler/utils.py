#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import os
from enum import Enum
from urllib.parse import urlsplit, urljoin, urldefrag

import requests
from my_fake_useragent import UserAgent
from pywander.path import mkdirs, to_absolute_path

logger = logging.getLogger(__name__)

ua = UserAgent(family=['chrome', 'firefox'])


class URLType(Enum):
    """
    refUrl: 除了Absolute URL，其他URL都需要根据本URL所在的文章的refUrl才能得到绝对URL
    """
    Absolute = 1
    # 'https://www.cis.rit.edu/htbooks/nmr/chap-10/chap-10.htm'
    MissScheme = 2
    # ’//www.cis.rit.edu/htbooks/nmr/chap-10/chap-10.htm‘ refUrl
    RelativeSite = 3
    # ’/htbooks/nmr/chap-10/chap-10.htm‘ refUrl
    RelativeFolder = 4
    # ’chap-10.html‘ refUrl
    RelativeArticle = 5
    # ’#sec1‘
    InValid = 6


def to_absolute_url(url, ref_url):
    """
    给定好refUrl，利用urljoin就能得到绝对url
    refUrl: 除了绝对URL，其他URL都需要根据本URL所在的文章的Url也就是refUrl
            才能得到绝对URL

    如果是爬虫，一开始就将遇到的URL转成绝对URL可能是一个好的选择，但其他文档处理情况则
    不能这样简单处理，需要小心地根据URL的各种类型来采取不同的处理策略。
    """
    return urljoin(ref_url, url)


def is_url_in_site(url, ref_url):
    """
    is the url in site.
    the judgement is based on the refUrl's netloc.

>>> is_url_in_site('https://code.visualstudio.com/docs', \
    'https://code.visualstudio.com/docs/python/linting')
True
    """
    p = urlsplit(url)
    if p.netloc == urlsplit(ref_url).netloc:
        return True
    else:
        return False


def is_url_in_article(url):
    """

    """
    p = urlsplit(url)
    if p.fragment:
        return True
    else:
        return False


def is_url_belong(url, baseurl):
    """
    is the url belong to the baseurl.
    the check logic is strict string match.
    """
    if url.startswith(baseurl):
        return True
    else:
        return False


def check_url_type(url):
    """
    这里只是对URL类型进行判断，从网络下或的HTML文件需要分辨各种URL类型并采取相应的策略
    """
    p = urlsplit(url)
    if p.scheme and p.netloc and p.path:
        return URLType.Absolute

    if not p.scheme and p.netloc and p.path:
        return URLType.MissScheme

    if not p.scheme and not p.netloc and p.path:
        if p.path.startswith('/'):
            return URLType.RelativeSite
        else:
            return URLType.RelativeFolder
    if not p.scheme and not p.netloc and not p.path:
        if p.fragment:
            return URLType.RelativeArticle
        else:
            return URLType.InValid


def get_url_netloc(url):
    """
    获取url的netloc属性
    """
    p = urlsplit(url)
    return p.netloc


def get_url_fragment(url):
    """
    please notice the fragment not include the symbol #
    """
    p = urlsplit(url)
    return p.fragment


def get_url_path(url):
    """
    获取url的path属性
    """
    p = urlsplit(url)
    return p.path


def remove_url_fragment(url):
    """
    remove url fragment like `#sec1` and the parameters on url will
    keeped still.
    """
    defragmented, frag = urldefrag(url)
    return defragmented


def get_download_filename(url):
    """
    从下载url中获得文件名, 不一定是有意义的.
    """
    path = get_url_path(url)
    filename = os.path.basename(path)
    return filename


def download(url, filename, download_timeout=30, override=False, **kwargs):
    """
    将目标url先下载到临时文件,然后再保存到命名文件.

    :param url: the url
    :param filename: 指定文件名
    """
    headers = {
        'user-agent': ua.random()
    }

    logger.info(f'start downloading file {url} to {filename}')
    start = time.time()

    filename = to_absolute_path(filename)

    # make sure folder exists
    mkdirs(os.path.dirname(filename))

    if os.path.exists(filename):
        if override:
            logger.info(f'{filename} exist. but i will override it.')
        else:
            logger.info(f'{filename} exist.')
            return

    content = requests.get(url, stream=True, headers=headers, **kwargs)

    with open(filename, 'wb') as f:
        for chunk in content.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
            if time.time() - start > download_timeout:
                content.close()
                os.unlink(filename)
                logger.warning('{0} download failed'.format(filename))
                return False

    return filename
