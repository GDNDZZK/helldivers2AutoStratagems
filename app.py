#!/usr/bin/python3
import random
import sys
import threading
import os
import shutil
import time
import logging
from util.Util import run_in_thread
from util.globalHotKeyManager import GlobalHotKeyManager,key_dict
from util.imageProcessing import arrow_str, binarize_image, capture_screenshot, crop_image, fast_arrow, process_images, resize_image, split_image
from util.settingGUI import settingsGUI
from util.loadSetting import getConfigDict
from util.SystemTrayIcon import SystemTrayIcon
from pynput.keyboard import Controller, Key
try:
    from winsound import Beep
except ModuleNotFoundError:
    logging.warning('winsound not found, beep will not work')

version = 'dev'

def checkPath():
    """确保工作路径正确"""
    # 获取当前工作路径
    current_work_dir = os.getcwd()
    logging.debug(f"当前工作路径：{current_work_dir}")

    # 获取当前文件所在路径
    current_file_dir = os.path.dirname(__file__)
    logging.debug(f"文件所在路径：{current_file_dir}")
    # 如果文件所在路径末尾是(_internal),跳转到上一级
    if '_internal' == current_file_dir[-9:]:
        current_file_dir = current_file_dir[:-9]
        logging.debug('internal')
        logging.debug(f"文件所在路径：{current_file_dir}")

    # 如果工作路径不是文件所在路径，切换到文件所在路径
    if current_work_dir != current_file_dir:
        os.chdir(current_file_dir)
        logging.debug("已切换到文件所在路径。")


def checkDir(path='./temp'):
    """检查目录是否存在,不存在则创建"""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


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
        logging.debug(f'beep error: {e}')

def arrow_merge(arrow_original_s,arrow_default_s):
    arrow_default_l = arrow_default_s.split('\n')
    if not arrow_original_s:
        return arrow_default_l
    arrow_original_l = arrow_original_s.split('\n')
    arrow_processed_l = []
    for i in range(len(arrow_original_l)):
        line = arrow_original_l[i]
        # 如果是空的,查找arrow_default_l中有没有,有就采用arrow_default_l的值
        if not line or len(line) <= 2:
            if len(arrow_default_l) > i and arrow_default_l[i]:
                arrow_processed_l.append(arrow_default_l[i])
            else:
                arrow_processed_l.append(line)
        else:
            arrow_processed_l.append(line)
    # 如果arrow_original_l比arrow_default_l少,则用arrow_default_l的值补齐
    if len(arrow_original_l) < len(arrow_default_l):
        arrow_processed_l += arrow_default_l[len(arrow_original_l):]
    return arrow_processed_l


file_lock = threading.Lock()

hotkeyOCR_is_running = False
hotkeyOCR_lock = threading.Lock()
@run_in_thread
def hotkeyOCR():
    global hotkeyOCR_is_running
    with hotkeyOCR_lock:
        if hotkeyOCR_is_running:
            di(2)
            return
        hotkeyOCR_is_running = True
    try:
        checkDir()
        logging.debug('===开始识别===')
        start_time = time.time()
        capture_screenshot()
        di()
        resize_image()
        crop_image()

        binarize_image()
        split_image()
        process_images()
        arrow_original_s = arrow_str()
        if len(arrow_original_s) < 8:
            raise Exception(arrow_original_s)
        with file_lock:
            with open('./temp/arrow_original.txt', 'w') as f:
                f.write(arrow_original_s)
            with open('./defaultArrow.txt', 'r') as f:
                arrow_default_s = f.read()
        arrow_processed_l = arrow_merge(arrow_original_s,arrow_default_s)
        with file_lock:
            with open('./temp/arrow.txt', 'w') as f:
                f.write('\n'.join(arrow_processed_l))

        logging.debug(f'耗时: {time.time() - start_time} 秒')
        logging.debug('===识别结束===')
        di(1)
    except Exception as e:
        logging.debug(f'识别失败: {e}')
        di(3)
    finally:
        with hotkeyOCR_lock:
            hotkeyOCR_is_running = False


# 随机延迟
def random_sleep(min: float = 0.05, max: float = 0.1) -> None:
    time.sleep(random.uniform(min, max))

keyboard = Controller()
def press_and_release(key) -> None:
    """按下并释放一个键"""
    global keyboard, config
    delay_min, delay_max = float(config.get('DELAY_MIN',0.05)), float(config.get('DELAY_MAX',0.1))
    keyboard.press(key)
    random_sleep(delay_min, delay_max)
    keyboard.release(key)
    random_sleep(delay_min, delay_max)

def c(line_s : str, fast_mode: bool = False):
    # 更新config
    global config
    if not fast_mode:
        config = getConfigDict()
    for s in line_s:
        if not s:
            continue
        match s:
            case 'W':
                press_and_release(key_dict[config.get("W",'<up>')])
            case 'S':
                press_and_release(key_dict[config.get("S",'<down>')])
            case 'A':
                press_and_release(key_dict[config.get("A",'<left>')])
            case 'D':
                press_and_release(key_dict[config.get("D",'<right>')])


hotkeyother_is_running = False
hotkeyother_lock = threading.Lock()
@run_in_thread
def hotkey_other(num: int, fast_mode = False):
    global hotkeyother_is_running, config
    with hotkeyother_lock:
        if hotkeyother_is_running:
            return
        hotkeyother_is_running = True
    try:
        if not fast_mode:
            with file_lock:
                # 如果temp/arrow.txt存在,则读取并执行
                if os.path.exists('./temp/arrow.txt'):
                    with open('./temp/arrow.txt', 'r') as f:
                        arrow = f.read().split('\n')
                # 如果不存在,则读取defaultArrow.txt
                else:
                    with open('./defaultArrow.txt', 'r') as f:
                        arrow = f.read().split('\n')
        else:
            try:
                arrow = fast_arrow(config)
                if not arrow:
                    raise Exception('未识别到箭头')
            except Exception as e:
                logging.debug(f'未识别到箭头: {e}')
                # di(2)
                with file_lock:
                    # 如果temp/arrow.txt存在,则读取并执行
                    if os.path.exists('./temp/arrow.txt'):
                        with open('./temp/arrow.txt', 'r') as f:
                            arrow = f.read().split('\n')
                    else:
                        arrow = ''
            with file_lock:
                with open('./defaultArrow.txt', 'r') as f:
                    default_arrow = f.read()
            arrow = arrow_merge(arrow, default_arrow)

        code = arrow[num - 1]
        logging.debug(f'执行: {code}')
        c(code, fast_mode)
        if fast_mode:
            # 写出temp/arrow.txt
            with file_lock:
                with open('./temp/arrow.txt', 'w') as f:
                    f.write('\n'.join(arrow))
    except Exception as e:
        logging.debug(f'操作失败: {num} {e}')
        di(2)
    finally:
        with hotkeyother_lock:
            hotkeyother_is_running = False


def main():
    checkPath()
    global config
    config = getConfigDict()
    hotkeyManager = GlobalHotKeyManager()
    GUI = settingsGUI(config, hotkeyManager)
    hotkeyManager.auto_register(config, hotkeyOCR, GUI.open_settings_gui, hotkey_other)
    hotkeyManager.start()
    sti = SystemTrayIcon(GUI)
    sti_thread = sti.start()
    # 会阻塞线程
    GUI.startWithProgram()
    # 等待sti线程结束后退出
    sti_thread.join()
    hotkeyManager.stop()

def onlySettingGuiMain():
    checkPath()
    global config
    config = getConfigDict()
    hotkeyManager = GlobalHotKeyManager()
    GUI = settingsGUI(config, hotkeyManager)
    hotkeyManager.auto_register(config, hotkeyOCR, GUI.open_settings_gui, hotkey_other)
    GUI.open_settings_gui()

if __name__ == '__main__':
    print(f'''helldivers2AutoStratagems {version} Copyright (C) 2025 GDNDZZK
This program comes with ABSOLUTELY NO WARRANTY; for details see LICENSE.
This is free software, and you are welcome to redistribute it under certain conditions.
''')

    logging.basicConfig(
    level=logging.DEBUG,  # 设置全局日志级别为 DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 控制台输出
        logging.FileHandler('log.txt', mode='w', encoding='utf-8')  # 保存到文件
    ])

    # 设置文件日志的级别为 INFO
    file_handler = logging.FileHandler('log.txt', mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # 设置控制台日志的级别为 DEBUG
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # 获取根日志器并添加处理器
    logger = logging.getLogger()
    logger.handlers = []  # 清空默认处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logging.debug('===开始===')
    # 如果参数包含"--only-setting-gui",则只打开设置界面
    if '--only-setting-gui' in sys.argv:
        onlySettingGuiMain()
    else:
        main()
