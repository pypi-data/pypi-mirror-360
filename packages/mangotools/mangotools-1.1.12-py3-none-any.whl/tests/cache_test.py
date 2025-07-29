# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-01-21 11:42
# @Author : 毛鹏
from mangotools.data_processor import DataProcessor


def test_001():
    """设置缓存和使用华城"""
    value = '设置到缓存中'
    processor = DataProcessor()
    processor.set_cache('value', value)  # 首先我们把value设置一个值
    assert processor.get_cache('value') == value
    return processor.get_cache('value')


def test_002():
    """替换${{}}中间的内容"""
    key = '芒果测试平台'
    value = '替换：${{key}}'
    processor = DataProcessor()
    processor.set_cache('key', key)  # 首先我们把value设置一个值
    assert processor.replace(value) == '替换：芒果测试平台'
    return processor.replace(value)  # 调用replace进行替换


def test_003():
    """获取公共方法中的数据"""
    processor = DataProcessor()
    assert processor.replace('${{md5_32_small(123456)}}') is not None
    return processor.replace('${{md5_32_small(123456)}}')


def test_004():
    """直接将获取到的内容存到缓存中"""
    str_ = "我是基于时间戳的5位随机数：${{number_time_5()|flow名称}}"
    processor = DataProcessor()
    value = processor.replace(str_)
    assert value == f"我是基于时间戳的5位随机数：{processor.get_cache('flow名称')}"
    return f"我是基于时间戳的5位随机数：{processor.get_cache('flow名称')}"


if __name__ == '__main__':
    print(f"方法：{test_001.__name__}：{test_001()}")
    print(f"方法：{test_002.__name__}：{test_002()}")
    print(f"方法：{test_003.__name__}：{test_003()}")
    print(f"方法：{test_004.__name__}：{test_004()}")
    from mangotools.mangos.pyarmor_runtime_windows.mango import Mango
    Mango.v(1)
