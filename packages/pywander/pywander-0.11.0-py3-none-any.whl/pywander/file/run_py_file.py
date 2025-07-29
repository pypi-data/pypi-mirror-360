"""
本模块采用文件hash比对的方法，因为预先假设文件夹里面的都是一些零碎的小文件，总的文件数目也不是很多。

批量运行某个文件夹下的python脚本

"""
import os
import subprocess

from pywander.cache import get_cachedb
from pywander.file.utils import calculate_file_hash

from pywander.path import gen_all_file


def batch_run_python_script(root='.', out_suffix='.out', err_suffix='.err'):
    need_to_process_file = collect_need_to_process_file(root=root, out_suffix=out_suffix, err_suffix=err_suffix)

    for file_path in need_to_process_file:
        file_out_path = file_path + out_suffix
        file_error_path = file_path + err_suffix

        try:
            # 打开文件以写入标准输出
            with open(file_out_path, 'wt', encoding='utf8') as stdout_file:
                # 打开文件以写入标准错误
                with open(file_error_path, 'wt', encoding='utf8') as stderr_file:
                    # 运行子进程，并将标准输出和标准错误分别重定向到文件
                    result = subprocess.run(f'python {file_path}', stdout=stdout_file, stderr=stderr_file,
                                            text=True, shell=True)

            # 检查返回码
            if result.returncode == 0:
                print(f"脚本 {file_path} 执行成功，标准输出已保存到 {stdout_file.name}")
                sync_file_hash(file_path, root=root)
            else:
                print(f"脚本 {file_path} 执行失败，错误信息已保存到 {stderr_file.name}")

        except FileNotFoundError:
            print("错误: 要运行的脚本文件未找到。")
        except Exception as e:
            print(f"发生未知错误: {e}")

    print(f'all job done.')


def collect_need_to_process_file(root='.', out_suffix='.out', err_suffix='.err'):
    """
    收集需要处理的文件
    """
    file_group = set()
    cachedb = get_cachedb(root=root)

    # 检查没有输出的脚本
    for file_path in gen_all_file(root, 'py$', exclude_folder_name=['__pycache__']):
        file_out_path = file_path + out_suffix

        if not os.path.exists(file_out_path):
            file_group.add(file_path)

    for file_path in gen_all_file(root, 'py$', exclude_folder_name=['__pycache__']):
        # 计算文件的哈希值
        file_hash = calculate_file_hash(file_path)

        # 获取文件的哈希缓存
        file_hash_cache_key = build_file_hash_key(file_path)
        if cachedb.has_key(file_hash_cache_key):
            file_hash_cache = cachedb.get(file_hash_cache_key)
        else:
            file_hash_cache = file_hash
            cachedb.set(file_hash_cache_key, file_hash)

        # 判断文件是否被修改
        if file_hash != file_hash_cache:
            file_group.add(file_path)

    return list(file_group)


def build_file_hash_key(file_path):
    file_hash_cache_key = 'file_hash' + file_path
    return file_hash_cache_key


def sync_file_hash(file_path, root='.'):
    cachedb = get_cachedb(root=root)
    file_hash_cache_key = build_file_hash_key(file_path)
    file_hash = calculate_file_hash(file_path)
    cachedb.set(file_hash_cache_key, file_hash)
