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