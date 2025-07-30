# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023-04-16 8:18
# @Author : 毛鹏
import sys

from ..database._mysql_connect import MysqlConnect
from ..database._sqlite_connect import SQLiteConnect

python_version = sys.version_info
if f"{python_version.major}.{python_version.minor}" != "3.10":
    raise Exception("必须使用>Python3.10.4")
__all__ = [
    'MysqlConnect',
    'SQLiteConnect'
]
