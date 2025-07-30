import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 14
project_path = file_path[0:end]
sys.path.append(project_path)
import psutil
import pandas as pd


# 获取所有进程
def get_all_process():
    all_process_df = None
    # 获取所有当前运行的进程
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            process_pid = proc.pid
            process_name = proc.info['name']
            result = {"process_pid": process_pid,
                      "process_name": process_name}
            result_df = pd.DataFrame(result, index=[1])
            if all_process_df is None:
                all_process_df = result_df
            else:
                all_process_df = pd.concat([all_process_df, result_df])
        except psutil.NoSuchProcess:
            pass
    return all_process_df


def is_process_running(process_name):
    # 获取所有当前运行的进程
    for proc in psutil.process_iter(['name']):
        try:
            # 检查进程名称是否匹配
            if proc.info['name'] == process_name:
                return True
        except psutil.NoSuchProcess:
            pass
    return False


# 查找文件路径
def find_file_path(file_name, search_path):
    '''
    :param file_name: 文件名
    :param search_path: 搜索路径 C:\\
    :return:
    '''
    for root, dirs, files in os.walk(search_path):
        if file_name in files:
            return os.path.join(root, file_name)
    return None
    # 示例用法


# 查找文件夹详细路径
def find_folder_path(folder_name, search_path):
    '''
    :param folder_name: 文件夹名
    :param search_path:  搜索路径 C:\\
    :return:
    '''
    for root, dirs, files in os.walk(search_path):
        if folder_name in dirs:
            return os.path.join(root, folder_name)
    return None

# get_all_process()
# # 示例用法
# name = "XtMiniQmt.exe"  # 你要查找的 exe 进程名
# if is_process_running(name):
#     print(f"{name} 进程正在运行")
# else:
#     print(f"{name} 进程未运行")
