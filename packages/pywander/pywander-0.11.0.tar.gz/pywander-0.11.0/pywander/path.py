#!/usr/bin/env python
# -*-coding:utf-8-*-

"""
路径支持

约定对外返回的路径均为字符串类型, Path对象有时把问题弄复杂了, 只供内部使用.

"""

import re
import errno
import os
import sys
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def is_pyinstaller_exe_running():
    """
    当前是否是pyinstaller的exe执行模式
    """
    if getattr(sys, 'frozen', False):
        return True
    else:
        return False


def get_pyinstaller_one_exe_data_folder():
    """
    pyinstaller制作的exe执行时获取数据文件夹所在.

    pyinstaller制作单exe脚本这样配置

    datas=[ ('file.txt', '.'),],

    额外的文件，实际上这个文件会放在某个临时目录下。
    """

    if getattr(sys, 'frozen', False):
        # exe执行模式 指向临时文件
        data_folder_path = sys._MEIPASS
    else:
        # 本地脚本测试模式 指向本脚本所在文件夹
        data_folder_path = os.path.dirname(
            os.path.abspath(sys.modules['__main__'].__file__)
        )
    return data_folder_path


def get_pyinstaller_exe_folder():
    """
    获取pyinstaller制作的exe的当前执行所在文件夹
    """
    if getattr(sys, 'frozen', False):
        # exe执行模式 指向本exe所在文件夹
        script_path = os.path.dirname(sys.executable)
    else:
        # 本地脚本测试模式 指向本脚本所在文件夹
        script_path = os.path.dirname(
            os.path.abspath(sys.modules['__main__'].__file__)
        )
    return script_path


def normalized_path(path: str | Path) -> str:
    """
    将路径规范化 支持 ~ 符号

    返回的是字符串
    """
    if isinstance(path, Path):
        return str(path.expanduser())
    elif isinstance(path, str):
        if path.startswith('~'):
            path = os.path.expanduser(path)
        return path
    else:
        raise TypeError


def to_absolute_path(path):
    """
    返回标准化的绝对路径
    在normalized_path的基础上还引入当前路径添加等
    """
    return os.path.abspath(normalized_path(path))


def _normalized_path(path) -> Path:
    """
    默认支持 ~ 符号
    """
    if isinstance(path, Path):
        return path.expanduser()
    elif isinstance(path, str):
        if path.startswith('~'):
            path = os.path.expanduser(path)
        return Path(path)
    else:
        raise TypeError


def rm(path, recursive=False):
    """
    the function can remove file or empty directory(default).

    use `shutil.rmtree` to remove the non-empty directory,you need add `recursive=True`

    """
    path = _normalized_path(path)
    if recursive:
        shutil.rmtree(path)
    else:
        if path.is_file():
            path.unlink()
        else:
            path.rmdir()


def mkdirs(path, mode=0o777):
    """
    Recursive directory creation function base on os.makedirs
    with a little error handling.
    """
    try:
        os.makedirs(path, mode=mode)
    except OSError as e:
        if e.errno != errno.EEXIST:  # File exists
            logger.error('file exists: {0}'.format(e))


def _ls(path=".", glob=False):
    """
    like ls common

    if `glob` set to True, then you can use the glob language for ls.
    """
    if glob:
        import glob
        return [_normalized_path(p) for p in glob.glob(path)]
    else:
        return [p for p in _normalized_path(path).iterdir()]


def ls(path=".", glob=False):
    """
    like ls common

    if `glob` set to True, then you can use the glob language for ls.
    """
    return [str(p) for p in _ls(path=path, glob=glob)]


def ls_file(path=".", glob=False):
    """
    based on ls function but only return file.
    """
    return [str(p) for p in _ls(path, glob=glob) if p.is_file()]


def ls_dir(path=".", glob=False):
    """
    based on ls function, but only return directory.
    """
    return [str(p) for p in _ls(path, glob=glob) if p.is_dir()]


def pwd():
    """
    get current directory
    """
    return os.getcwd()


def get_file_ext(path):
    """
    >>> get_file_ext(r'D:\\README.md') # doctest: +SKIP
    '.md'
    """
    if os.path.isfile(path):
        _, ext = os.path.splitext(path)
        return ext
    else:
        raise ValueError


def get_filename(path):
    """
    >>> get_filename(r'D:\\README.md') # doctest: +SKIP
    'README.md'
    """
    if os.path.isfile(path):
        return os.path.basename(path)
    else:
        raise ValueError


def gen_all_file(start_path='.', filetype="", exclude_folder_name=None):
    """
    利用os.walk 遍历某个目录，收集其内的文件，返回一系列的文件*绝对*路径。
    ```
    list(gen_all_file('pywander', filetype='py$'))
    ['D:\\github\\pywander\\pywander\\cache.py',
    'D:\\github\\pywander\\pywander\\common.py',
     ...
    ```
    第一个可选参数 start_path  默认值 '.'
    第二个可选参数  filetype  正则表达式模板 默认值是"" 其作用是只选择某些文件
    如果是空值，则所有的文件都将被选中。比如 "html$|pdf$" 将只选中 html和pdf文件。
    第三个可选参数 exclude_folder_name 列出一些想要排除文件夹的名字

    """
    for root, dirs, files in os.walk(start_path):
        if exclude_folder_name is not None:
            for exclude_folder in exclude_folder_name:
                if exclude_folder in dirs:
                    # 将不会再访问
                    dirs.remove(exclude_folder)

        folder_path = to_absolute_path(os.path.join(root))

        for file in files:
            file_path = os.path.join(folder_path, file)

            file_name, file_ext = os.path.splitext(file)
            if filetype:
                if re.search(filetype, file_ext):
                    yield file_path
            else:
                yield file_path


def gen_all_file2(start_path='.', filetype="", exclude_folder_name=None):
    """
    利用os.walk 遍历某个目录，收集其内的文件，返回一系列的文件的*相对*路径。
    ```
    list(gen_all_file2('pywander', filetype='py$'))
    ['pywander\\cache.py',
    'pywander\\common.py',
    ```
    第一个可选参数 start_path  默认值 '.'
    第二个可选参数  filetype  正则表达式模板 默认值是"" 其作用是只选择某些文件
    如果是空值，则所有的文件都将被选中。比如 "html$|pdf$" 将只选中 html和pdf文件。
    第三个可选参数 exclude_folder_name 列出一些想要排除文件夹的名字

    """
    for file_path in gen_all_file(start_path=start_path, filetype=filetype,
                                  exclude_folder_name=exclude_folder_name):
        yield os.path.relpath(file_path)


def gen_all_file3(start_path='.', filetype="", exclude_folder_name=None):
    """
    利用os.walk 遍历某个目录，收集其内的文件，返回 (文件路径列表, 本路径下的文件列表)
    ```
    list(gen_all_file3('pywander', filetype='py$'))
    [(['pywander'], 'cache.py'),
     (['pywander'], 'common.py'),
    ```
    第一个可选参数 start_path  默认值 '.'
    第二个可选参数  filetype  正则表达式模板 默认值是"" 其作用是只选择某些文件
    如果是空值，则所有的文件都将被选中。比如 "html$|pdf$" 将只选中 html和pdf文件。
    第三个可选参数 exclude_folder_name 列出一些想要排除文件夹的名字
    """
    for file_path in gen_all_file2(start_path=start_path, filetype=filetype,
                                  exclude_folder_name=exclude_folder_name):
        root, file_name = os.path.split(file_path)
        dirlist = root.split(os.path.sep)
        item = (dirlist, file_name)
        yield item


def remove_first_directory(path):
    """
    移除文件路径的第一个目录

    >>> remove_first_directory('pywander\\cache.py') # doctest: +SKIP
    'cache.py'
    """
    path_split = path.split(os.path.sep)
    if len(path_split) > 1:
        return os.path.join(*path_split[1:])
    else:
        raise ValueError(f'输入有误，给定的文件路径没有目录')



def remove_window_illegal_symbol(s):
    """
    移除windows下的非法字符

    >>> remove_window_illegal_symbol('ad >> ? / e  dddd ?')
    'ad    e  dddd '
    """
    new_s = re.sub(r'[/\\:*?"<>|]', '', s)
    return new_s
