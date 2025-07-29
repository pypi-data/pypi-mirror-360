import os
import zipfile

def b_archive_zip(
    source_path,
    output_path,
    exclude_dirs:list[str]=None,
    exclude_files:list[str]=None,
    exclude_exts:list[str]=None,
    while_list:list[str]=None,
    contain_empty_folder:bool=True,
):
    '''
    压缩文件夹，排除 指定文件夹and指定后缀文件
    :param source_path:
    :param output_path:
    :param exclude_dirs: ['__pycache__', '.git', '.idea']
    :param exclude_files: ['.gitignore', 'README.md']
    :param exclude_exts: ['.csv', '.npy', '.pt', '.pth']
    :return:
    '''
    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_files is None:
        exclude_files = []
    if exclude_exts is None:
        exclude_exts = []
    if while_list is None:
        while_list = []

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 压缩文件:
        if os.path.isfile(source_path):
            arcname = os.path.basename(source_path)
            zipf.write(source_path, arcname)
            return

        # 压缩文件夹:
        if os.path.isdir(source_path):
            for root, dirs, files in os.walk(source_path):
                # 排除指定文件夹dirs
                dirs[:] = [d for d in dirs if d in while_list or d not in exclude_dirs]
                # 排除指定文件files
                files = [f for f in files if f in while_list or f not in exclude_files]
                # 排除指定后缀文件files
                files = [f for f in files if f in while_list or not any(f.endswith(ext) for ext in exclude_exts)]


                # 压缩文件:
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_path) # 相对于source_path的相对路径
                    zipf.write(file_path, arcname)

                # 若是空文件夹，则压缩文件夹:
                if contain_empty_folder and (len(dirs) == 0 and len(files) == 0):
                    arcname = os.path.relpath(root, source_path)
                    folder_path = root
                    zipf.write(folder_path, arcname)

if __name__ == '__main__':
    b_archive_zip(
        source_path=r'E:\byzh_workingplace\byzh-rc-to-pypi\awa',
        output_path=r'E:\byzh_workingplace\byzh-rc-to-pypi\awaqwq.zip',
        exclude_dirs=['__pycache__', 'com'],
        exclude_exts=['.ppt']
    )