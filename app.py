

import random
import threading
import os
import shutil
import time
from util.globalHotKeyManager import GlobalHotKeyManager
from util.imageProcessing import arrow_str, binarize_image, capture_screenshot, crop_image, process_images, resize_image, split_image
from util.loadSetting import getConfigDict
from util.SystemTrayIcon import SystemTrayIcon
from pynput.keyboard import Controller, Key
try:
    from winsound import Beep
except ModuleNotFoundError:
    print('WARN: winsound not found, beep will not work')

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

@run_in_thread
def di(m = 0):
    try:
        match m:
            case 0:
                # 开始提示音
                Beep(800, 100)
            case 1:
                # 结束提示音
                Beep(500, 50)
                time.sleep(0.01)
                Beep(500, 50)
            case 2:
                # 警告提示音
                Beep(400, 80)
            case 3:
                # 错误提示音
                Beep(200, 1000)
    except Exception as e:
        print(f'beep error: {e}')

file_lock = threading.Lock()

hotkey0_is_running = False
hotkey0_lock = threading.Lock()
@run_in_thread
def hotkey0():
    global hotkey0_is_running
    with hotkey0_lock:
        if hotkey0_is_running:
            di(2)
            return
        hotkey0_is_running = True
    try:
        checkDir()
        print('===开始识别===')
        start_time = time.time()
        capture_screenshot()
        di()
        resize_image()
        crop_image()

        binarize_image()
        split_image()
        process_images()
        arrow_original_s = arrow_str()
        arrow_original_l = arrow_original_s.split('\n')
        with file_lock:
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
        with file_lock:
            with open('./temp/arrow.txt', 'w') as f:
                f.write('\n'.join(arrow_processed_l))

        print(f'耗时: {time.time() - start_time} 秒')
        print('===识别结束===')
        di(1)
    except Exception as e:
        print(f'识别失败: {e}')
        di(3)
    finally:
        with hotkey0_lock:
            hotkey0_is_running = False

# 随机延迟(60/300秒到60/100秒)
def random_sleep():
    time.sleep(random.uniform(1/15, 1/25))

keyboard = Controller()
def press_and_release(key):
    global keyboard
    keyboard.press(key)
    random_sleep()
    keyboard.release(key)
    random_sleep()

def c(line_s : str):
    for s in line_s:
        if not s:
            continue
        match s:
            case 'W':
                press_and_release(Key.up)
            case 'S':
                press_and_release(Key.down)
            case 'A':
                press_and_release(Key.left)
            case 'D':
                press_and_release(Key.right)


hotkeyother_is_running = False
hotkeyother_lock = threading.Lock()
@run_in_thread
def hotkey_other(num: int):
    global hotkeyother_is_running
    with hotkeyother_lock:
        if hotkeyother_is_running:
            return
        hotkeyother_is_running = True
    try:
        with file_lock:
            # 如果temp/arrow.txt存在,则读取并执行
            if os.path.exists('./temp/arrow.txt'):
                with open('./temp/arrow.txt', 'r') as f:
                    arrow = f.read().split('\n')
            # 如果不存在,则读取defaultArrow.txt
            else:
                with open('./defaultArrow.txt', 'r') as f:
                    arrow = f.read().split('\n')
        code = arrow[num - 1]
        print(f'执行: {code}')
        c(code)
    except Exception as e:
        print(f'操作失败: {e}')
        di(2)
    finally:
        with hotkeyother_lock:
            hotkeyother_is_running = False


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
