import logging
import time
import threading
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from util.Util import run_in_thread
key_dict = {
    '<alt>': Key.alt,
    '<alt_l>': Key.alt_l,
    '<alt_r>': Key.alt_r,
    '<alt_gr>': Key.alt_gr,
    '<backspace>': Key.backspace,
    '<caps_lock>': Key.caps_lock,
    '<cmd>': Key.cmd,
    '<cmd_l>': Key.cmd_l,
    '<cmd_r>': Key.cmd_r,
    '<ctrl>': Key.ctrl,
    '<ctrl_l>': Key.ctrl_l,
    '<ctrl_r>': Key.ctrl_r,
    '<delete>': Key.delete,
    '<down>': Key.down,
    '<end>': Key.end,
    '<enter>': Key.enter,
    '<esc>': Key.esc,
    '<f1>': Key.f1,
    '<f2>': Key.f2,
    '<f3>': Key.f3,
    '<f4>': Key.f4,
    '<f5>': Key.f5,
    '<f6>': Key.f6,
    '<f7>': Key.f7,
    '<f8>': Key.f8,
    '<f9>': Key.f9,
    '<f10>': Key.f10,
    '<f11>': Key.f11,
    '<f12>': Key.f12,
    '<f13>': Key.f13,
    '<f14>': Key.f14,
    '<f15>': Key.f15,
    '<f16>': Key.f16,
    '<f17>': Key.f17,
    '<f18>': Key.f18,
    '<f19>': Key.f19,
    '<f20>': Key.f20,
    '<home>': Key.home,
    '<left>': Key.left,
    '<page_down>': Key.page_down,
    '<page_up>': Key.page_up,
    '<right>': Key.right,
    '<shift>': Key.shift,
    '<shift_l>': Key.shift_l,
    '<shift_r>': Key.shift_r,
    '<space>': Key.space,
    '<tab>': Key.tab,
    '<up>': Key.up,
    '<media_play_pause>': Key.media_play_pause,
    '<media_volume_mute>': Key.media_volume_mute,
    '<media_volume_down>': Key.media_volume_down,
    '<media_volume_up>': Key.media_volume_up,
    '<media_previous>': Key.media_previous,
    '<media_next>': Key.media_next,
    '<insert>': Key.insert,
    '<menu>': Key.menu,
    '<num_lock>': Key.num_lock,
    '<pause>': Key.pause,
    '<print_screen>': Key.print_screen,
    '<scroll_lock>': Key.scroll_lock
}
key_dict['<alt>'].vk = 164
key_dict['<alt_l>'].vk = 164
key_dict['<alt_r>'].vk = 165
key_dict['<alt_gr>'].vk = 165
key_dict['<backspace>'].vk = 8
key_dict['<caps_lock>'].vk = 20
key_dict['<cmd>'].vk = 91
key_dict['<cmd_l>'].vk = 91
key_dict['<cmd_r>'].vk = 92
key_dict['<win>'] = key_dict['<cmd>']
key_dict['<win_l>'] = key_dict['<cmd_l>']
key_dict['<win_r>'] = key_dict['<cmd_r>']
key_dict['<ctrl>'].vk = 162
key_dict['<ctrl_l>'].vk = 162
key_dict['<ctrl_r>'].vk = 163
key_dict['<delete>'].vk = 46
key_dict['<down>'].vk = 40
key_dict['<end>'].vk = 35
key_dict['<enter>'].vk = 13
key_dict['<esc>'].vk = 27
key_dict['<f1>'].vk = 112
key_dict['<f2>'].vk = 113
key_dict['<f3>'].vk = 114
key_dict['<f4>'].vk = 115
key_dict['<f5>'].vk = 116
key_dict['<f6>'].vk = 117
key_dict['<f7>'].vk = 118
key_dict['<f8>'].vk = 119
key_dict['<f9>'].vk = 120
key_dict['<f10>'].vk = 121
key_dict['<f11>'].vk = 122
key_dict['<f12>'].vk = 123
key_dict['<f13>'].vk = 124
key_dict['<f14>'].vk = 125
key_dict['<f15>'].vk = 126
key_dict['<f16>'].vk = 127
key_dict['<f17>'].vk = 128
key_dict['<f18>'].vk = 129
key_dict['<f19>'].vk = 130
key_dict['<f20>'].vk = 131
key_dict['<home>'].vk = 36
key_dict['<left>'].vk = 37
key_dict['<page_down>'].vk = 34
key_dict['<page_up>'].vk = 33
key_dict['<right>'].vk = 39
key_dict['<shift>'].vk = 160
key_dict['<shift_l>'].vk = 160
key_dict['<shift_r>'].vk = 161
key_dict['<space>'].vk = 32
key_dict['<tab>'].vk = 9
key_dict['<up>'].vk = 38
key_dict['<media_play_pause>'].vk = 179
key_dict['<media_volume_mute>'].vk = 173
key_dict['<media_volume_down>'].vk = 174
key_dict['<media_volume_up>'].vk = 175
key_dict['<media_previous>'].vk = 177
key_dict['<media_next>'].vk = 176
key_dict['<insert>'].vk = 45
key_dict['<menu>'].vk = 93
key_dict['<num_lock>'].vk = 144
key_dict['<pause>'].vk = 19
key_dict['<print_screen>'].vk = 44
key_dict['<scroll_lock>'].vk = 145


# 遍历A~Z
for i in range(65, 91):
    t = chr(i)
    key_dict[t] = KeyCode.from_vk(i)
    key_dict[f'<{t}>'] = KeyCode.from_vk(i)
    key_dict[t.upper()] = KeyCode.from_vk(i)
    key_dict[f'<{t.upper()}>'] = KeyCode.from_vk(i)
# 0~9
for i in range(48, 58):
    t = str(i - 48)
    key_dict[t] = KeyCode.from_vk(i)
    key_dict[f'<{t}>'] = KeyCode.from_vk(i)
# 小键盘 0~9
for i in range(96, 106):
    t = str(i - 96)
    key_dict[f'numpad_{t}'] = KeyCode.from_vk(i)
    key_dict[f'numpad{t}'] = KeyCode.from_vk(i)
    key_dict[f'<numpad_{t}>'] = KeyCode.from_vk(i)
    key_dict[f'<numpad{t}>'] = KeyCode.from_vk(i)
# 小键盘
key_dict[f'<numpad_*>'] = KeyCode.from_vk(106)
key_dict[f'<numpad_multiply>'] = KeyCode.from_vk(106)
key_dict[f'<numpad_+>'] = KeyCode.from_vk(107)
key_dict[f'<numpad_add>'] = KeyCode.from_vk(107)
key_dict[f'<numpad_enter>'] = KeyCode.from_vk(108)
key_dict[f'<numpad_->'] = KeyCode.from_vk(109)
key_dict[f'<numpad_subtract>'] = KeyCode.from_vk(109)
key_dict[f'<numpad_.>'] = KeyCode.from_vk(110)
key_dict[f'<numpad_decimal>'] = KeyCode.from_vk(110)
key_dict[f'<numpad_/>'] = KeyCode.from_vk(111)
key_dict[f'<numpad_divide>'] = KeyCode.from_vk(111)
# 符号
key_dict['<`>'] = KeyCode.from_vk(192)
key_dict['`'] = KeyCode.from_vk(192)
key_dict['<~>'] = KeyCode.from_vk(192)
key_dict['~'] = KeyCode.from_vk(192)
key_dict['<!>'] = KeyCode.from_vk(49)
key_dict['!'] = KeyCode.from_vk(49)
key_dict['<@>'] = KeyCode.from_vk(50)
key_dict['@'] = KeyCode.from_vk(50)
key_dict['<#>'] = KeyCode.from_vk(51)
key_dict['#'] = KeyCode.from_vk(51)
key_dict['<$>'] = KeyCode.from_vk(52)
key_dict['$'] = KeyCode.from_vk(52)
key_dict['<%>'] = KeyCode.from_vk(53)
key_dict['%'] = KeyCode.from_vk(53)
key_dict['<^>'] = KeyCode.from_vk(54)
key_dict['^'] = KeyCode.from_vk(54)
key_dict['<&>'] = KeyCode.from_vk(55)
key_dict['&'] = KeyCode.from_vk(55)
key_dict['<*>'] = KeyCode.from_vk(56)
key_dict['*'] = KeyCode.from_vk(56)
key_dict['<(>'] = KeyCode.from_vk(57)
key_dict['('] = KeyCode.from_vk(57)
key_dict['<)>'] = KeyCode.from_vk(48)
key_dict[')'] = KeyCode.from_vk(48)
key_dict['<_>'] = KeyCode.from_vk(189)
key_dict['_'] = KeyCode.from_vk(189)
key_dict['<->'] = KeyCode.from_vk(189)
key_dict['-'] = KeyCode.from_vk(189)
key_dict['<=>'] = KeyCode.from_vk(187)
key_dict['='] = KeyCode.from_vk(187)
key_dict['<+>'] = KeyCode.from_vk(187)
key_dict['+'] = KeyCode.from_vk(187)
key_dict['<|>'] = KeyCode.from_vk(220)
key_dict['|'] = KeyCode.from_vk(220)
key_dict['<\\>'] = KeyCode.from_vk(220)
key_dict['\\'] = KeyCode.from_vk(220)
key_dict['<;>'] = KeyCode.from_vk(186)
key_dict[';'] = KeyCode.from_vk(186)
key_dict['<:>'] = KeyCode.from_vk(186)
key_dict[':'] = KeyCode.from_vk(186)
key_dict["<[>"] = KeyCode.from_vk(219)
key_dict["["] = KeyCode.from_vk(219)
key_dict["<{>"] = KeyCode.from_vk(219)
key_dict['{'] = KeyCode.from_vk(219)
key_dict['<]>'] = KeyCode.from_vk(221)
key_dict['<}>'] = KeyCode.from_vk(221)
key_dict[']'] = KeyCode.from_vk(221)
key_dict['}'] = KeyCode.from_vk(221)
key_dict['</>'] = KeyCode.from_vk(191)
key_dict['/'] = KeyCode.from_vk(191)
key_dict['<?>'] = KeyCode.from_vk(191)
key_dict['?'] = KeyCode.from_vk(191)
key_dict['<\'>'] = KeyCode.from_vk(222)
key_dict['\''] = KeyCode.from_vk(222)
key_dict['<">'] = KeyCode.from_vk(222)
key_dict['"'] = KeyCode.from_vk(222)
key_dict['<,>'] = KeyCode.from_vk(188)
key_dict['<<>'] = KeyCode.from_vk(188)
key_dict['<'] = KeyCode.from_vk(188)
key_dict[','] = KeyCode.from_vk(188)
key_dict['<.>'] = KeyCode.from_vk(190)
key_dict['<>>'] = KeyCode.from_vk(190)
key_dict['>'] = KeyCode.from_vk(190)
key_dict['.'] = KeyCode.from_vk(190)

key_vk_dict = {v.vk: k for k, v in key_dict.items() if '+' not in k and '<' in k and '>' in k}

def vk_to_key_str(vk_code : int) -> str:
    return key_vk_dict[vk_code]

def vks_to_key_str(vk_codes : list|set) -> str:
    vk_codes = set(vk_codes)
    result = '+'.join([vk_to_key_str(vk_code) for vk_code in vk_codes])
    return result

class GlobalHotKeyManager:
    """一利用GlobalHotKeys注册全局快捷键,提供注册函数和删除函数"""

    def __init__(self):
        self.hotkeys = {}  # 一个字典，存储已注册的全局快捷键和对应的回调函数
        self.kbl = None

    def register(self, keys: set | list, callback=None):
        """注册函数,将set包含的按键组合注册为全局快捷键,传入回调函数,当按键组合被触发时执行,如果不传入回调函数,使用默认的回调函数"""
        key_codes = [key for key in keys if key]
        self.hotkeys['+'.join([str(i) for i in key_codes])] = callback if not callback is None else lambda: print(
            f'{keys} is pressed')

    is_run_set = set()

    def _run(self, press_key_set):

        # 检查要运行哪些函数
        # 遍历hotkeys
        for key, call_back in self.hotkeys.items():
            # 检查是否所有按键且不在is_run_set中
            key_flag = all([key_dict[i].vk in press_key_set for i in key.split('+') if i in key_dict]) if key else False
            if key_flag and not key in self.is_run_set:
                # 运行
                self.is_run_set.add(key)
                call_back()
            elif not key_flag:
                # 将key从is_run_set中移除
                if key in self.is_run_set:
                    self.is_run_set.discard(key)

    def start(self):
        self.kbl = KeyboardListener(self._run)
        self.kbl.start()

    def stop(self):
        """删除函数,用于删除所有通过注册函数注册的全局快捷键"""
        self.kbl.stop()
        self.kbl = None
        # 清空字典
        self.hotkeys.clear()

    def auto_register(self, config, ocr_func=None, setting_func=None, other_func=None):
        if not ocr_func is None:
            self.ocr_func = ocr_func
        if not setting_func is None:
            self.setting_func = setting_func
        if not other_func is None:
            self.other_func = other_func
        ocr_keys = config.get('OCRKEY','<ctrl_l>+<->|<ctrl_r>+<->').split('|')
        setting_keys = config.get('SETTINGKEY','<ctrl_l>+<=>|<ctrl_r>+<=>').split('|')
        for keys in ocr_keys:
            self.register(keys.split('+'), self.ocr_func)
        for keys in setting_keys:
            self.register(keys.split('+'), self.setting_func)
        for i in range(1, 11):
            for keys in config.get(f'SKEY{i}',f'<ctrl_l>+<{i}>|<ctrl_r>+<{i}>').split('|'):
                self.register(keys.split('+'), lambda x=i: self.other_func(x))
            for keys in config.get(f'SKEYANDOCR{i}',f'<f{i}>').split('|'):
                self.register(keys.split('+'), lambda x=i: self.other_func(x, True))


class KeyboardListener:
    def __init__(self, function = lambda x:None, scanningFrequency=128, on_press_function = lambda x:None, on_release_function = lambda x:None):
        self.function = function  # 要执行的函数
        self.scanningFrequency = scanningFrequency  # 上报频率
        self.press_key_set = set()
        self.stop_event = threading.Event()
        self.listener_thread = None
        self.scanner_thread = None
        self.on_press_function = on_press_function
        self.on_release_function = on_release_function

    @run_in_thread
    def on_press(self, key, _):
        # 记录按下的键
        self.press_key_set.add(key.vk)
        self.on_press_function(t)

    @run_in_thread
    def on_release(self, key, _):
        # 移除松开的键
        t = key.vk
        try:
            self.press_key_set.remove(t)
        except KeyError:
            # 清除set
            logging.warning("发生错误,清空按键")
            self.press_key_set.clear()
        self.on_release_function(t)

    def start_listener(self):
        # 使用with语句创建一个键盘监听器，监听键盘按键按下和释放事件
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            while not self.stop_event.is_set():
                time.sleep(0.01)  # 检查停止事件

    old_press_key_set = set()
    def start_scanner(self):
        while not self.stop_event.is_set():
            time.sleep(1 / float(self.scanningFrequency))
            if self.press_key_set != self.old_press_key_set:
                self.old_press_key_set = self.press_key_set.copy()
                self.function(self.press_key_set)

    def start(self):
        self.listener_thread = threading.Thread(target=self.start_listener)
        self.scanner_thread = threading.Thread(target=self.start_scanner)

        self.listener_thread.start()
        self.scanner_thread.start()

    def stop(self):
        if not self.listener_thread is None and not self.scanner_thread is None:
            # 设置停止事件，通知监听器和扫描器线程停止
            self.stop_event.set()
            # 等待线程实际退出
            self.listener_thread.join()
            self.scanner_thread.join()
