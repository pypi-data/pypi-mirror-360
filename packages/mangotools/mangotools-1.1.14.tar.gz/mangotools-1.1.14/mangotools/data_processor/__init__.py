# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-03-07 8:24
# @Author : 毛鹏
import json
import re

import sys

from ..data_processor._cache_tool import CacheTool
from ..data_processor._coding_tool import CodingTool
from ..data_processor._encryption_tool import EncryptionTool
from ..data_processor._json_tool import JsonTool
from ..data_processor._random_character_info_data import RandomCharacterInfoData
from ..data_processor._random_number_data import RandomNumberData
from ..data_processor._random_string_data import RandomStringData
from ..data_processor._random_time_data import RandomTimeData
from ..data_processor._sql_cache import SqlCache
from ..exceptions import MangoToolsError
from ..exceptions.error_msg import ERROR_MSG_0047, ERROR_MSG_0002

"""
ObtainRandomData类的函数注释必须是： “”“中间写值”“”
"""

python_version = sys.version_info
if f"{python_version.major}.{python_version.minor}" != "3.10":
    raise Exception("必须使用>Python3.10.4")


class ObtainRandomData(RandomNumberData, RandomCharacterInfoData, RandomTimeData, RandomStringData):
    """ 获取随机数据 """

    def regular(self, func: str):
        """
        反射并执行函数
        :param func: 函数
        :return:
        """
        match = re.search(r'\((.*?)\)', func)
        if match:
            try:
                content = json.loads(match.group(1))
                if not isinstance(content, dict):
                    content = {'data': match.group(1)}
            except json.decoder.JSONDecodeError:
                content = {'data': match.group(1)}

            func = re.sub(r'\(' + match.group(1) + r'\)', '', func)
            try:
                if content['data'] != '':
                    return getattr(self, func)(**content)
                return getattr(self, func)()
            except AttributeError:
                raise MangoToolsError(*ERROR_MSG_0047)


class DataClean(JsonTool, CacheTool, EncryptionTool, CodingTool):
    """存储或处理随机数据"""
    pass


class DataProcessor(ObtainRandomData, DataClean):

    def __init__(self):
        ObtainRandomData.__init__(self)
        DataClean.__init__(self)

    def replace(self, data: list | dict | str | None) -> list | dict | str | None:
        if not data:
            return data
        if isinstance(data, list):
            return [self.replace(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.replace(value) for key, value in data.items()}
        else:
            return self.replace_str(data)

    def replace_str(self, data: str) -> str:
        replace_list = re.findall(r"\${{.*?}}", str(data))
        for replace_value in replace_list:
            key_text = self.remove_parentheses(replace_value)
            args = key_text.split("|")
            key_text, key = (args[0], args[1]) if len(args) == 2 else (args[0], None)
            if key and (key_value := self.get_cache(key)):
                return key_value

            value = self.regular(key_text) if self.identify_parentheses(key_text) else self.get_cache(key_text)
            if value is None:
                raise MangoToolsError(*ERROR_MSG_0002, value=(key_text,))

            if key:
                self.set_cache(key, value)
            data = data.replace(replace_value, str(value))
        return data

    @classmethod
    def remove_parentheses(cls, data: str) -> str:
        return data.replace("${{", "").replace("}}", "").strip()

    @classmethod
    def identify_parentheses(cls, value: str):
        return re.search(r'\((.*?)\)', str(value))

    @classmethod
    def is_extract(cls, string: str) -> bool:
        return bool(re.search(r'\$\{\{.*\}\}', string))


__all__ = [
    'CacheTool',
    'CodingTool',
    'EncryptionTool',
    'JsonTool',
    'RandomCharacterInfoData',
    'RandomNumberData',
    'RandomStringData',
    'RandomTimeData',
    'ObtainRandomData',
    'DataClean',
    'DataProcessor',
    'SqlCache'
]
