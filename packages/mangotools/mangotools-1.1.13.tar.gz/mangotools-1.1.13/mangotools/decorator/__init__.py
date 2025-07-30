# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023/4/26 17:41
# @Author : 毛鹏
import sys

from ..decorator.convert_args import convert_args
from ..decorator.inject_to_class import inject_to_class
from ..decorator.method_callback import async_method_callback, sync_method_callback, func_info
from ..decorator.retry import async_retry, sync_retry
from ..decorator.singleton import singleton
python_version = sys.version_info
if f"{python_version.major}.{python_version.minor}" != "3.10":
    raise Exception("必须使用>Python3.10.4")
__all__ = [
    'convert_args',
    'func_info',
    'singleton',
    'async_method_callback',
    'sync_method_callback',
    'inject_to_class',
    'async_retry',
    'sync_retry',
]
