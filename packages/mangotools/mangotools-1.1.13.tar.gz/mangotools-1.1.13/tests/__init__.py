# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-07 23:25
# @Author : 毛鹏
import json

from mangotools.assertion import *
from mangotools.decorator import func_info

if __name__ == '__main__':
    print(json.dumps(func_info, ensure_ascii=False))