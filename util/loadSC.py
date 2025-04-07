import csv
import os
import requests
import csv
import os
import requests
import csv
import os
import requests

def getStratagemCodesFromFile(filename: str) -> list:
    """
    读取指定战略配备文件并返回一个列表，每个元素是包含战略配备信息的字典

    Returns:
    - list[dict]
    """
    local_path = f'./local/{filename}'
    file_path = local_path if os.path.exists(local_path) else f'./{filename}'
    result = []
    try:
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            result = dataToStratagemCodes(reader)  # 读取数据并转换为字典
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到")
    except Exception as e:
        print(f"读取文件 {file_path} 时发生错误: {e}")
    return result

def getStratagemCodeFromWeb(url: str) -> list:
    """
    从指定URL获取战略配备数据并返回一个列表，每个元素是包含战略配备信息的字典

    Returns:
    - list[dict]
    """
    result = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        csv_content = response.text.splitlines()  # 按行分割CSV内容
        reader = csv.reader(csv_content)
        result = dataToStratagemCodes(reader)  # 读取数据并转换为字典
    except requests.RequestException as e:
        print(f"请求 {url} 时发生错误: {e}")
    except Exception as e:
        print(f"处理数据时发生错误: {e}")
    return result

def dataToStratagemCodes(data: list) -> list:
    """
    将读取的数据转换为战略配备代码字典

    Args:
    - data: 读取的数据列表

    Returns:
    - dict
    """
    result = []
    for i, row in enumerate(data):
        if i == 0:  # 跳过第一行标题
            headers = [header.strip() for header in row]
            continue
        if len(row) < len(headers):  # 确保数据行长度不小于标题行
            print(f"数据行长度不足，跳过: {row}")
            continue
        entry = {}
        for j, value in enumerate(row):
            entry[headers[j]] = value.strip()  # 动态根据标题生成键值对
        result.append(entry)
    return result

def saveStratagemCodesToFile(data: dict, filename: str) -> None:
    """
    将战略配备数据保存到指定文件

    Args:
    - data: 要保存的数据
    - filename: 文件名
    """
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in data.items():
                writer.writerow([key, value])
        print(f"数据已保存到 {filename}")
    except Exception as e:
        print(f"保存数据时发生错误: {e}")
    return None