# -*- encoding: utf-8 -*-
import os

default_config = r'''; encoding: utf-8
; 按键设置
; 可选按键
; '<alt>', '<alt_l>', '<alt_r>', '<alt_gr>', '<backspace>', '<caps_lock>', '<cmd>', '<cmd_l>',
; '<cmd_r>', '<ctrl>', '<ctrl_l>', '<ctrl_r>', '<delete>', '<down>', '<end>', '<enter>', '<esc>',
; '<f1>', '<f2>', '<f3>', '<f4>', '<f5>', '<f6>', '<f7>', '<f8>', '<f9>', '<f10>', '<f11>',
; '<f12>', '<f13>', '<f14>', '<f15>', '<f16>', '<f17>', '<f18>', '<f19>', '<f20>', '<home>',
; '<left>', '<page_down>', '<page_up>', '<right>', '<shift>', '<shift_l>', '<shift_r>', '<space>', '<tab>', '<up>',
; '<media_play_pause>', '<media_volume_mute>', '<media_volume_down>',
; '<media_volume_up>', '<media_previous>', '<media_next>', '<insert>',
; '<menu>', '<num_lock>', '<pause>', '<print_screen>', '<scroll_lock>',
; '<win>', '<win_l>', '<win_r>', '<A>', '<B>', '<C>', '<D>', '<E>', '<F>',
; '<G>', '<H>', '<I>', '<J>', '<K>', '<L>', '<M>', '<N>', '<O>', '<P>', '<Q>',
; '<R>', '<S>', '<T>', '<U>', '<V>', '<W>', '<X>', '<Y>', '<Z>',
; '<0>', '<1>', '<2>', '<3>', '<4>', '<5>', '<6>', '<7>', '<8>', '<9>',
; '<numpad_0>', '<numpad0>', '<numpad_1>', '<numpad1>', '<numpad_2>',
; '<numpad2>', '<numpad_3>', '<numpad3>', '<numpad_4>', '<numpad4>',
; '<numpad_5>', '<numpad5>', '<numpad_6>', '<numpad6>', '<numpad_7>',
; '<numpad7>', '<numpad_8>', '<numpad8>', '<numpad_9>', '<numpad9>',
; '<numpad_*>', '<numpad_multiply>', '<numpad_add>', '<numpad_enter>',
; '<numpad_->', '<numpad_subtract>', '<numpad_.>', '<numpad_decimal>', '<numpad_/>',
; '<numpad_divide>', '<`>', '<~>', '<!>', '<@>', '<#>', '<$>', '<%>', '<^>', '<&>', '<*>',
; '<(>', '<)>', '<_>', '<->', '<=>', '<\>', '<;>', '<:>', '<[>', '<{>', '<]>', '<}>',
; '</>', '<?>', "<'>", '<">', '<,>', '<<>', '<', '<.>', '<>>'
; 使用+连接同组多个按键,表示同时按下
; 使用|连接多组按键,表示按下任意一组
; 识别按键
OCRKEY=<ctrl_l>+<->|<ctrl_r>+<->
; 打开设置面板
SETTINGKEY=<ctrl_l>+<=>|<ctrl_r>+<=>
; 战备1
SKEY1=<ctrl_l>+<1>|<ctrl_r>+<1>
; 战备2
SKEY2=<ctrl_l>+<2>|<ctrl_r>+<2>
; 战备3
SKEY3=<ctrl_l>+<3>|<ctrl_r>+<3>
; 战备4
SKEY4=<ctrl_l>+<4>|<ctrl_r>+<4>
; 战备5
SKEY5=<ctrl_l>+<5>|<ctrl_r>+<5>
; 战备6
SKEY6=<ctrl_l>+<6>|<ctrl_r>+<6>
; 战备7
SKEY7=<ctrl_l>+<7>|<ctrl_r>+<7>
; 战备8
SKEY8=<ctrl_l>+<8>|<ctrl_r>+<8>
; 战备9
SKEY9=<ctrl_l>+<9>|<ctrl_r>+<9>
; 战备10
SKEY10=<ctrl_l>+<0>|<ctrl_r>+<0>

; 干扰器优化模式战备按键,每次使用战备都会重新识别,不会输出中间文件,不会实时更新设置.由于每次使用战备都会重新识别,所以还是会比识别完成后使用慢,但会比先识别后使用快.
SKEYANDOCR1=<f1>
SKEYANDOCR2=<f2>
SKEYANDOCR3=<f3>
SKEYANDOCR4=<f4>
SKEYANDOCR5=<f5>
SKEYANDOCR6=<f6>
SKEYANDOCR7=<f7>
SKEYANDOCR8=<f8>
SKEYANDOCR9=<f9>
SKEYANDOCR10=<f10>

; 设置战备按键
W=<up>
A=<left>
S=<down>
D=<right>

; 战备面板识别区域
LEFT=30
TOP=20
RIGHT=220
BOTTOM=400

; 二值化相关设置
THRESHOLD=30
COLORS=#DAC177,#DF7567,#50AFC8,#74A15F,#BEBEBE,#BAB9A1,#E4D0AA

; 按键触发速度设置
DELAY_MIN=0.03
DELAY_MAX=0.08

; GUI相关设置
; GUI是否应该随着程序启动，接受值: 1, 0
START_GUI_WITH_PROGRAM=1
'''

def getDefaultConfigDict() -> dict:
    """
    获取默认配置文件并返回一个字典

    Returns:
    - dict
    """
    result = {}
    # 遍历default_config每一行
    for line in default_config.splitlines():
        # 如果行不为空，且不以;开头
        if line and not line.startswith(";"):
            # 用等号分割键和值
            key, value = line.split("=", 1)
            # 将键值对添加到字典中
            result[key] = value
    return result

def getConfigDict(filename: str = 'config.ini') -> dict:
    """
    读取指定配置文件并返回一个字典

    Returns:
    - dict
    """
    local_path = f'./local/{filename}'
    file_path = local_path if os.path.exists(local_path) else f'./{filename}'
    # 如果文件不存在,则创建一个默认的配置文件
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(default_config)
    # 创建一个空字典
    result = {}
    # 打开文件
    with open(file_path, "r", encoding='utf-8') as f:
        # 遍历文件的每一行
        for line in f:
            # 去掉行尾的换行符
            line = line.strip()
            # 如果行不为空，且不以;开头
            if line and not line.startswith(";"):
                # 用等号分割键和值
                key, value = line.split("=", 1)
                # 将键值对添加到字典中
                result[key] = value
    # 返回字典
    return result

def saveConfigDict(config: dict, filename: str = 'config.ini') -> None:
    """
    将字典保存到指定配置文件中

    Args:
    -config: dict
    -filename: str
    """
    local_path = f'./local/{filename}'
    file_path = local_path if os.path.exists(local_path) else f'./{filename}'
    result = ''
    old_config_str = ''
    # 载入旧设置
    with open(file_path, "r", encoding='utf-8') as f:
        old_config_str = f.read()
    # 生成新设置
    # 记录已替换的设置
    replaced_keys = set()
    # 遍历old_config_str每一行
    for line in old_config_str.splitlines():
        # 如果行不为空，且不以;开头
        if line and not line.startswith(";"):
            # 用等号分割键和值
            key, value = line.split("=", 1)
            # 如果key在config中,则将value替换为config中的值
            value = config.get(key, value)
            new_line = f'{key}={value}\n'
            result += new_line
            replaced_keys.add(key)
        else:
            result += line + '\n'
    # 如果有未替换的设置，则添加到result中
    # 先判断是否有未替换的设置,如果有添加注释
    if len([i for i in config.keys() if i not in replaced_keys]) > 0:
        result += '\n;自动生成设置\n;Auto generated settings\n'
    for key, value in config.items():
        if key not in replaced_keys:
            result += f'{key}={value}\n'
    # 将result写入文件
    with open(file_path, "w", encoding='utf-8') as f:
        f.write(result)
