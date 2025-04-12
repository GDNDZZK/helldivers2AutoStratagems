from pynput import keyboard

class GlobalHotKeyManager:
    """一利用GlobalHotKeys注册全局快捷键,提供注册函数和删除函数"""

    def __init__(self):
        self.hotkeys = {}  # 一个字典，存储已注册的全局快捷键和对应的回调函数

    def register(self, keys, callback=None):
        """注册函数,将set包含的按键组合注册为全局快捷键,传入回调函数,当按键组合被触发时执行,如果不传入回调函数,使用默认的回调函数"""
        keys_list = [i.replace('_l','').replace('_gr','').replace('_r', '') for i in keys]
        if '' in keys_list:
            keys_list.remove('')
        keys_str = '+'.join(keys_list)
        # 尝试将按键组合和回调函数添加到字典中
        try:
            self.hotkeys[keys_str] = callback if not callback is None else lambda: print(f'{keys_str} is pressed')
            if '<alt>' in keys_list:
                # 替换成<alt_gr>再来一次
                keys_list[keys_list.index('<alt>')] = '<alt_gr>'
                keys_str = '+'.join(keys_list)
                self.hotkeys[keys_str] = callback if not callback is None else lambda: print(f'{keys_str} is pressed')
        except ValueError as e:
            # 如果出现ValueError异常，说明这个快捷键已经被占用，发出一个警告信息，并记录异常信息
            print(str(e))
            return

    def start(self):
        # 尝试创建一个新的GlobalHotKeys对象，传入字典
        try:
            self.globalHotKeys = keyboard.GlobalHotKeys(self.hotkeys)
        except ValueError as e:
            # 如果出现ValueError异常，说明有些快捷键已经被占用，发出一个警告信息，并记录异常信息
            print(str(e))
            return
        # 启动GlobalHotKeys对象，开始监听键盘事件
        self.globalHotKeys.start()

    def stop(self):
        """删除函数,用于删除所有通过注册函数注册的全局快捷键"""
        # 如果有GlobalHotKeys对象，停止它
        if self.globalHotKeys:
            self.globalHotKeys.stop()
        # 清空字典
        self.hotkeys.clear()
        self.globalHotKeys.stop()
        # 将GlobalHotKeys对象设为None
        self.globalHotKeys = None

    def auto_register(self,config, ocr_func = None, setting_func = None, other_func = None):
        if not ocr_func is None:
            self.ocr_func = ocr_func
        if not setting_func is None:
            self.setting_func = setting_func
        if not other_func is None:
            self.other_func = other_func
        self.register([config['ACTIVATION'], '-'], self.ocr_func)
        self.register([config['ACTIVATION'], '='], self.setting_func)
        for i in range(1, 10):
            self.register(
                [config['ACTIVATION'], str(i)], lambda x=i: self.other_func(x))
        self.register([config['ACTIVATION'], '0'], lambda: self.other_func(10))