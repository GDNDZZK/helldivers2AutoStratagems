import csv
import os
import requests

class StratagemCodes():
    """
    战略配备
    """
    _offical = []  # 官方数据
    _custom = []  # 自定义数据
    codes = []  # 合并后的数据
    def __init__(self, updurl: str = None, language_code: str = 'en'):
        try:
            response = requests.get(updurl)
            response.raise_for_status()  # 检查请求是否成功
            csv_content = response.text.splitlines()  # 按行分割CSV内容
            reader = csv.reader(csv_content)
            self._offical = self._dataToStratagemCodes(reader)  # 读取数据并转换为字典
        except requests.RequestException as e:
            print(f"请求 {updurl} 时发生错误: {e}")
            self._offical = self.getStratagemCodesFromFile("custom_Stratagem_Codes.csv")  # 使用本地文件作为备份
        except Exception as e:
            print(f"发生错误: {e}")
            self._offical = []
        self._custom = self.getStratagemCodesFromFile("custom_Stratagem_Codes.csv")  # 读取本地文件
        combined_codes = []
        supported_languages = True
        # 检查是否支持指定语言
        code_info = self._offical[0] if self._offical else {}
        if language_code not in code_info:
            supported_languages = False
            print(f"不支持语言: {language_code}，使用默认语言")
        for code_info in self._offical:
            if supported_languages:
                description = code_info.get(language_code, code_info.get('en', ''))
            else:
                description = code_info.get('en', '')
            combined_codes.append(code_info['code'], description)
        for code_info in self._custom:
            code = code_info['code']
            description = code_info.get(language_code, code_info.get('local', ''))
            combined_codes.append(code, description)
        # 根据战略配备代码的列表去重
        combined_codes = list(set(combined_codes))


    def _dataToStratagemCodes(data: list) -> list:
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

    def getStratagemCodesFromFile(self, filename: str) -> list:
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
                result = self._dataToStratagemCodes(reader)  # 读取数据并转换为字典
        except FileNotFoundError:
            print(f"文件 {file_path} 未找到")
        except Exception as e:
            print(f"读取文件 {file_path} 时发生错误: {e}")
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

    def addCustomCode(self, code: str, description: str) -> None:
        """
        添加自定义战略配备代码

        Args:
        - key: 战略配备代码
        - value: 战略配备描述
        """
        self._custom[code] = description
        self.codes[code] = description
        self.saveStratagemCodesToFile(self._custom, "custom_Stratagem_Codes.csv")

    def removeCustomCode(self, code: str) -> None:
        """
        删除自定义战略配备代码

        Args:
        - key: 战略配备代码
        """
        if code in self._custom:
            del self._custom[code]
            del self.codes[code]
            self.saveStratagemCodesToFile(self._custom, "custom_Stratagem_Codes.csv")
        else:
            print(f"自定义代码 {code} 不存在")
        return None
