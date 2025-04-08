import csv
import os
import logging
import requests


class StratagemCodes():
    """
    战略配备
    """
    _offical: list  # 官方数据
    _custom: list  # 自定义数据
    codes: list  # 合并后的数据
    logger: logging.Logger
    def __init__(self, updurl: str = None, language_code: str = 'en'):
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            response = requests.get(updurl)
            response.raise_for_status()  # 检查请求是否成功
            csv_content = response.text.splitlines()  # 按行分割CSV内容
            reader = csv.reader(csv_content)
            self._offical = self._dataToStratagemCodes(reader)  # 读取数据并转换为字典
        except Exception as e:
            self.logger.error(f"从URL读取数据时发生错误: {e}")
            self._offical = self.getStratagemCodesFromFile("offical_Stratagem_Codes.csv")  # 使用本地文件作为备份
        self._custom = self.getStratagemCodesFromFile("custom_Stratagem_Codes.csv")  # 读取本地文件
        self.logger.info(f"读取数据成功: {self._offical}")
        self.logger.info(f"读取自定义数据成功: {self._custom}")
        combined_codes = []
        supported_languages = True
        self.logger.info(f"语言代码: {language_code}")
        # 检查是否支持指定语言
        code_info = self._offical[0] if self._offical else {}
        if language_code not in code_info:
            supported_languages = False
            self.logger.info(f"不支持指定语言: {language_code}，使用默认语言")
        for code_info in self._offical:
            if supported_languages:
                description = code_info.get(language_code, code_info.get('en', ''))
            else:
                description = code_info.get('en', '')
            combined_codes.append([code_info['codes'], description])
        for code_info in self._custom:
            code = code_info['codes']
            for i in range(len(combined_codes)):
                if combined_codes[i][0] == code:
                    self._custom.pop(i)  # 删除重复的自定义代码
                    continue
            description = code_info.get("local", "")
            combined_codes.append([code, description])  # 添加自定义代码
        self.codes = combined_codes  # 合并后的数据

    def __str__(self):
        return str(self.codes)

    def _dataToStratagemCodes(self, data: list) -> list:
        """
        将读取的数据转换为战略配备代码列表

        Args:
        - data: 读取的数据列表

        Returns:
        - list[dict]
        """
        result = []
        headers = None  # 初始化 headers
        for i, row in enumerate(data):
            self.logger.debug(f"读取行: {row}")
            if i == 0:  # 跳过第一行标题
                headers = [header.strip() for header in row]
                self.logger.debug(f"标题行: {headers}")
                continue
            if not headers:
                self.logger.error("标题行未找到")
                break
            if len(row) < len(headers):  # 确保数据行长度不小于标题行
                self.logger.debug("跳过不完整的行")
                continue
            entry = {}
            for j, value in enumerate(row):
                entry[headers[j]] = value.strip()  # 动态根据标题生成键值对
            self.logger.debug(f"生成条目: {entry}")
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
                self.logger.debug(f"读取文件: {file_path}")
                self.logger.debug(f"读取数据: {result}")
        except FileNotFoundError:
            self.logger.error(f"文件 {file_path} 未找到")
        except Exception as e:
            self.logger.error(f"读取文件时发生错误: {e}")
        return result

    def saveStratagemCodesToFile(self, filename: str) -> None:
        """
        将战略配备数据保存到指定文件

        Args:
        - data: 要保存的数据
        - filename: 文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as csv_file:
                writer = csv.writer(csv_file)
                for row in self._custom:
                    writer.writerow(row.values())
            self.logger.info(f"数据已保存到 {filename}")
        except Exception as e:
            self.logger.error(f"保存数据时发生错误: {e}")
        return None

    def addCustomCode(self, code: str, description: str) -> None:
        """
        添加自定义战略配备代码

        Args:
        - key: 战略配备代码
        - value: 战略配备描述
        """
        is_official = False
        for code_info in self._offical:
            if code_info['codes'] == code:
                is_official = True
                break
        if is_official:
            self.logger.error(f"自定义代码 {code} 已存在于官方数据中")
            return None
        is_update = False
        for code_info in self._custom:
            if code_info["codes"] == code:
                self.logger.warning(f"自定义代码 {code} 已存在, 进行更新")
                self._custom[code]["local"] = description
                break
        if not is_update:
            self._custom.append({"codes": code, "local": description})
        is_update = False
        for code_info in self.codes:
            if code_info[0] == code:
                self.logger.warning(f"自定义代码 {code} 已存在, 进行更新")
                code_info[1] = description
                is_update = True
                break
        if not is_update:
            self.codes.append([code, description])
        self.logger.info(f"添加自定义代码 {code}: {description}")
        return None

    def removeCustomCode(self, code: str) -> None:
        """
        删除自定义战略配备代码

        Args:
        - key: 战略配备代码
        """
        is_remove = False
        for code_info in self._custom:
            if code_info["codes"] == code:
                self._custom.remove(code_info)
                self.logger.info(f"删除自定义代码 {code}")
                is_remove = True
                break
        for code_info in self.codes:
            if code_info[0] == code:
                self.codes.remove(code_info)
                self.logger.info(f"删除自定义代码 {code}")
                break
        self.saveStratagemCodesToFile("custom_Stratagem_Codes.csv")
        if not is_remove:
            self.logger.error(f"自定义代码 {code} 不存在")
        return None
