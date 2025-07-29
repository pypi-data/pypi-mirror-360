from pathlib import Path
import os
import shutil

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
def b_makedir(path):
    path = Path(path)

    if is_dir(path):
        os.makedirs(path, exist_ok=True)
    if is_file(path):
        os.makedirs(path.parent, exist_ok=True)


