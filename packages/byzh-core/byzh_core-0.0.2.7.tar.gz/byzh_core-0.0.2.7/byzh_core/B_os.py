import shutil
import os
from pathlib import Path
from typing import Literal

def get_parent_dir(path: Literal['__file__']) -> Path:
    '''
    获取 该py文件 所在的文件夹
    :param path: __file__
    '''
    parent_dir = Path(path).parent
    return parent_dir

def get_cwd() -> Path:
    '''
    获取 当前工作目录current working directory
    '''
    return Path.cwd()


def makedirs(path):
    def is_dir(path):
        path = Path(path)

        # 存在
        if os.path.isdir(path):
            return True

        # 不存在
        name = path.name
        if '.' in name:
            return False
        return True

    def is_file(path):
        path = Path(path)

        # 存在
        if os.path.isfile(path):
            return True

        # 不存在
        name = path.name
        if '.' in name:
            return True
        return False

    path = Path(path)

    if is_dir(path):
        os.makedirs(path, exist_ok=True)
    if is_file(path):
        os.makedirs(path.parent, exist_ok=True)

def rm(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    if os.path.isfile(path):
        os.remove(path)


def get_dirpaths_in_dir(root_dir_path, exclude_dir=['__pycache__', '.git']):
    result = []
    for root, dirs, files in os.walk(root_dir_path):
        for i, dir in enumerate(dirs):
            if str(dir) in exclude_dir:
                dirs.pop(i)
        path = Path(root)
        result.append(path)

    result = result[1:]

    return result

def get_filepaths_in_dir(root_dir_path, exclude_name=[], exclude_suffix=['.pyc'], exclude_dir=['.git']):
    file_paths = []
    for root, dirs, files in os.walk(root_dir_path):
        for i, dir in enumerate(dirs):
            if str(dir) in exclude_dir:
                dirs.pop(i)
        for file in files:
            file_path = os.path.join(root, file)
            file_path = Path(file_path)
            if file_path.name in exclude_name or file_path.suffix in exclude_suffix:
                continue
            file_paths.append(file_path)
    return file_paths

if __name__ == '__main__':
    # print(get_dirpaths_in_dir(r'E:\byzh_workingplace\byzh-rc-to-pypi'))
    a = get_filepaths_in_dir(r'E:\byzh_workingplace\byzh-rc-to-pypi')
    print(a)