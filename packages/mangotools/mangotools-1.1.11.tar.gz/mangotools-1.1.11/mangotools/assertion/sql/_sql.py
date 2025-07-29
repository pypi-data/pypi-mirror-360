# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-11-20 9:47
# @Author : 毛鹏
from deepdiff import DeepDiff

from mangotools.database import MysqlConnect
from mangotools.decorator import sync_method_callback
from mangotools.models import MethodModel


class MysqlAssertion:
    """mysql"""

    def __init__(self, mysql_connect: MysqlConnect | None):
        self.mysql_connect: MysqlConnect = mysql_connect

    @sync_method_callback('sql断言', 'mysql', 1, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望条数', d=True),
    ])
    async def assert_sql_count(self, actual: str, expect: int):
        """SQL查询结果条数"""
        result = self.mysql_connect.condition_execute(actual)
        assert len(result) == int(expect), f'实际条数={len(result)}, 预期条数={expect}'

    @sync_method_callback('sql断言', 'mysql', 2, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='请输入期望的dict', d=True),
    ])
    async def assert_sql_first_row(self, actual: str, expect: dict):
        """数据相等"""
        result = self.mysql_connect.condition_execute(actual)
        assert result, f'实际={result}, 预期={expect}'
        first_row = result[0]
        diff = DeepDiff(first_row, expect, ignore_order=True)
        assert not diff, f'实际={actual}, 预期={expect}'

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望字段及值', d=True,
                    v={'key': '请输入对应查询语句中的key', 'value': '请输入期望结果'}),
    ])
    async def assert_sql_value_in_first_row(self, actual: str, expect: dict):
        """值相等"""
        result = self.mysql_connect.condition_execute(actual)
        assert result, f'实际={result}, 预期={expect}'
        first_row = result[0]
        for k, v in expect.items():
            assert first_row.get(k) == v, f'字段{k}实际值={first_row.get(k)}, 预期值={v}'


if __name__ == '__main__':
    _sql = "SELECT id,`name`,`status` FROM `project`;"
    _expect = [{'id': 2, 'name': '1CDXP', 'status': 1}, {'id': 5, 'name': 'AIGC', 'status': 1},
               {'id': 10, 'name': 'DESK', 'status': 1}, {'id': 11, 'name': 'AIGC-SaaS', 'status': 1}]
