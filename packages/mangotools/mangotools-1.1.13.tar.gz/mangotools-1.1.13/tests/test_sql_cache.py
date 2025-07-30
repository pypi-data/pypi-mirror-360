# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-30 17:12
# @Author : 毛鹏
import json
import tempfile

from mangotools.data_processor import SqlCache
from mangotools.enums import CacheValueTypeEnum

temp_db = tempfile.NamedTemporaryFile(delete=False)
temp_db.close()
db_path = temp_db.name

cache = SqlCache(db_path)

cache.set_sql_cache("test_str", "hello world", CacheValueTypeEnum.STR)
print(type(cache.get_sql_cache("test_str")), cache.get_sql_cache("test_str"))
assert cache.get_sql_cache("test_str") == "hello world"

cache.set_sql_cache("test_int", 42, CacheValueTypeEnum.INT)
print(type(cache.get_sql_cache("test_int")), cache.get_sql_cache("test_int"))
assert cache.get_sql_cache("test_int") == 42

cache.set_sql_cache("test_float", 3.14, CacheValueTypeEnum.FLOAT)
print(type(cache.get_sql_cache("test_float")), cache.get_sql_cache("test_float"))
assert cache.get_sql_cache("test_float") == 3.14

cache.set_sql_cache("test_bool", True, CacheValueTypeEnum.BOOL)
print(type(cache.get_sql_cache("test_bool")), cache.get_sql_cache("test_bool"))
assert cache.get_sql_cache("test_bool") is True

cache.set_sql_cache("test_none", None, CacheValueTypeEnum.NONE)
print(type(cache.get_sql_cache("test_none")), cache.get_sql_cache("test_none"))
assert cache.get_sql_cache("test_none") is None

test_list = [1, 2, 3, "four"]
cache.set_sql_cache("test_list", test_list, CacheValueTypeEnum.LIST)
print(type(cache.get_sql_cache("test_list")), cache.get_sql_cache("test_list"))
assert cache.get_sql_cache("test_list") == test_list

test_dict = {"a": 1, "b": 2, "c": "three"}
cache.set_sql_cache("test_dict", test_dict, CacheValueTypeEnum.DICT)
print(type(cache.get_sql_cache("test_dict")), cache.get_sql_cache("test_dict"))
assert cache.get_sql_cache("test_dict") == test_dict

test_tuple = (1, 2, 3, "four")
cache.set_sql_cache("test_tuple", test_tuple, CacheValueTypeEnum.TUPLE)
print(type(cache.get_sql_cache("test_tuple")), cache.get_sql_cache("test_tuple"))
assert cache.get_sql_cache("test_tuple") == test_tuple

test_json = {"name": "John", "age": 30, "city": "New York"}
cache.set_sql_cache("test_json", test_json, CacheValueTypeEnum.JSON)
print(type(cache.get_sql_cache("test_json")), cache.get_sql_cache("test_json"))
assert cache.get_sql_cache("test_json") == test_json

print(json.dumps(cache.get_sql_all()))
print("测试包含。..")
assert cache.contains_sql_cache("test_str") is True
assert cache.contains_sql_cache("nonexistent") is False

print("测试删除。..")
cache.delete_sql_cache("test_str")
assert cache.get_sql_cache("test_str") is None
assert cache.contains_sql_cache("test_str") is False

print("测试清除。..")
cache.clear_sql_cache()
assert cache.get_sql_cache("test_int") is None
assert cache.contains_sql_cache("test_int") is False

print("所有测试均已通过！")
