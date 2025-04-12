# -*- encoding: utf-8 -*-
import os

def getConfigDict(filename: str = 'config.ini') -> dict:
    """
    读取指定配置文件并返回一个字典

    Returns:
    - dict
    """
    local_path = f'./local/{filename}'
    file_path = local_path if os.path.exists(local_path) else f'./{filename}'
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
                result[key] = value.lower()
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