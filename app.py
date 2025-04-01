

import threading
import os
import shutil
import time
from util.globalHotKeyManager import GlobalHotKeyManager
from util.imageProcessing import arrow_str, binarize_image, crop_image, process_images, resize_image, split_image
from util.loadSetting import getConfigDict
from util.SystemTrayIcon import SystemTrayIcon


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


def checkDir(path='./temp'):
    """检查目录是否存在,不存在则创建"""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def run_in_thread(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


hotkey0_is_running = False
hotkey0_lock = threading.Lock()
@run_in_thread
def hotkey0():
    global hotkey0_is_running
    with hotkey0_lock:
        if hotkey0_is_running:
            return
        hotkey0_is_running = True
    try:
        # checkDir()
        print('===开始识别===')
        start_time = time.time()
        # capture_screenshot()
        resize_image()
        crop_image()

        binarize_image()
        split_image()
        process_images()
        arrow_original_s = arrow_str()
        arrow_original_l = arrow_original_s.split('\n')
        with open('./temp/arrow_original.txt', 'w') as f:
            f.write(arrow_original_s)
        with open('./defaultArrow.txt', 'r') as f:
            arrow_default_l = f.read().split('\n')
        arrow_processed_l = []
        # 遍历arrow_s每一行
        for i in range(len(arrow_original_l)):
            line = arrow_original_l[i]
            # 如果是空的,查找arrow_default_l中有没有,有就采用arrow_default_l的值
            if not line:
                if len(arrow_default_l) > i and arrow_default_l[i]:
                    arrow_processed_l.append(arrow_default_l[i])
                else:
                    arrow_processed_l.append('')
            else:
                arrow_processed_l.append(line)
        with open('./temp/arrow.txt', 'w') as f:
            f.write('\n'.join(arrow_processed_l))

        print(f'耗时: {time.time() - start_time} 秒')
        print('===识别结束===')
    except Exception as e:
        print(f'识别失败: {e}')
        raise e
    finally:
        with hotkey0_lock:
            hotkey0_is_running = False


def hotkey_other(num: int):
    num -= 1
    print(f'num: {num}')


def main():
    checkPath()
    config = getConfigDict()
    hotkeyManager = GlobalHotKeyManager()
    hotkeyManager.register([config['ACTIVATION'], '0'], hotkey0)
    for i in range(1, 10):
        hotkeyManager.register(
            [config['ACTIVATION'], str(i)], lambda x=i: hotkey_other(x))
    hotkeyManager.start()
    # 随机选择arrow下的一张图片
    sti = SystemTrayIcon()
    sti.start()
    pass


if __name__ == '__main__':
    main()
