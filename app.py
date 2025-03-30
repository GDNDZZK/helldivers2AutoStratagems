

import os
import shutil


def checkPath():
    """确保工作路径正确"""
    # 获取当前工作路径
    current_work_dir = os.getcwd()
    print(f"当前工作路径：{current_work_dir}")

    # 获取当前文件所在路径
    current_file_dir = os.path.dirname(__file__)
    print(f"文件所在路径：{current_file_dir}")
    # 如果文件所在路径末尾是(_internal),跳转到上一级
    if '_internal' == current_file_dir[-9:]:
        current_file_dir = current_file_dir[:-9]
        print('internal')
        print(f"文件所在路径：{current_file_dir}")

    # 如果工作路径不是文件所在路径，切换到文件所在路径
    if current_work_dir != current_file_dir:
        os.chdir(current_file_dir)
        print("已切换到文件所在路径。")


def checkDir(path = './temp'):
    """检查目录是否存在,不存在则创建"""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def main():
    checkPath()
    # checkDir()
    pass

if __name__ == '__main__':
    main()