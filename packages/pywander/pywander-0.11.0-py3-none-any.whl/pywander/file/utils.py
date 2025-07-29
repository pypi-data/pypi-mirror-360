#!/usr/bin/env python
# -*-coding:utf-8-*-

import hashlib


def calculate_file_hash(file_path):
    """
    计算目标文件hash值
    """
    hash_object = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_object.update(chunk)
    return hash_object.hexdigest()


def bigfile_read(filename, process_line=None, line_start=1, line_count=-1, mode="r", encoding="utf8"):
    """
    选择大型文件部分行执行某些操作

    filename 要处理的文件名
    process_line -- 每一行的处理函数 默认打印动作 默认传入第一个参数 当前行数 第二个参数 具体行内容
    line_start 从哪一行开始处理 默认1
    line_count 总计要处理多少行 默认-1 含义为无穷大
    mode 文件打开模式 默认 'r'
    encoding 文件打开编码 默认 'utf8'

    :return:
    """

    def _default_process_line(line_num, line_content):
        print(f"{line_num}: {line_content}", end='')
        return line_content

    if process_line is None:
        process_line = _default_process_line

    with open(filename, mode=mode, encoding=encoding) as f:
        in_block = False
        count = 0

        for index, line in enumerate(f):
            line_num = index + 1

            if line_num == line_start:
                in_block = True
                print('\n', end='')

            if in_block:
                new_line = process_line(line_num, line)

                count += 1

            if 0 < line_count <= count:
                break


def gen_bigfile_read(filename, process_line=None, line_start=1, line_count=-1, mode="r", encoding="utf8"):
    """
    选择大型文件的某些行执行某些操作，并生成出来。

    filename 要处理的文件名
    process_line -- 每一行的处理函数 默认不执行动作 默认传入第一个参数 当前行数 第二个参数 具体行内容
    line_start 从哪一行开始处理 默认1
    line_count 总计要处理多少行 默认-1 含义为无穷大
    mode 文件打开模式 默认 'r'
    encoding 文件打开编码 默认 'utf8'

    :return:

    """

    def _default_process_line(line_num, line_content):
        return line_content

    if process_line is None:
        process_line = _default_process_line

    with open(filename, mode=mode, encoding=encoding) as f:
        in_block = False
        count = 0

        for index, line in enumerate(f):
            line_num = index + 1

            if line_num == line_start:
                in_block = True

            if in_block:
                new_line = process_line(line_num, line)
                yield new_line

                count += 1

            if 0 < line_count <= count:
                break
