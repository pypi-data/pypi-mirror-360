# -*- coding: utf-8 -*-
# @Project: 芒果测试平台# @Description: 随机数据封装
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
import random

import time
from faker import Faker


class RandomNumberData:
    """ 随机的数字类型测试数据 """
    faker = Faker(locale='zh_CN')

    @classmethod
    def randint(cls, **kwargs):
        """随机的范围数，传入：left，right"""
        data = kwargs.get('data')
        if data:
            left = data.get('left', 2000)
        else:
            left = 2000
        if data:
            right = data.get('left', 2500)
        else:
            right = 2500
        return random.randint(left, right)

    @classmethod
    def number_time_5(cls):
        """获取基于当前时间戳的随机五位数"""
        s = int(time.time())
        s = str(s)
        return s[5:len(s)]

    @classmethod
    def number_random_0_9(cls) -> int:
        """0-9的随机数"""
        _data = random.randint(0, 9)
        return _data

    @classmethod
    def number_random_0_5(cls) -> int:
        """0-9的随机数"""
        _data = random.randint(0, 5)
        return _data

    @classmethod
    def number_random_10_99(cls) -> int:
        """10-99的随机数"""
        _data = random.randint(10, 99)
        return _data

    @classmethod
    def number_random_100_999(cls) -> int:
        """100-999的随机数"""
        _data = random.randint(100, 999)
        return _data

    @classmethod
    def number_random_0_5000(cls) -> int:
        """0-5000的随机数"""
        _data = random.randint(0, 5000)
        return _data

    @classmethod
    def number_random_float(cls):
        """小数"""
        return random.random()

    @classmethod
    def number_random_two_float(cls):
        """随机两位小数"""
        return round(random.random(), 2)

    @classmethod
    def number_random_1000_two_float(cls):
        """1000以内的随机两位小数"""
        return cls.number_random_100_999() + round(random.random(), 2)

    @classmethod
    def number_random_negative(cls, left=-1000, right=-1):
        """负数范围的随机整数"""
        return random.randint(left, right)

    @classmethod
    def number_random_digits(cls, digits=6):
        """指定位数的随机整数"""
        if digits < 1:
            digits = 1
        start = 10**(digits-1)
        end = 10**digits - 1
        return random.randint(start, end)

    @classmethod
    def number_random_even(cls, left=0, right=1000):
        """指定范围内的随机偶数"""
        even = random.randrange(left + (left % 2), right, 2)
        return even

    @classmethod
    def number_random_odd(cls, left=0, right=1000):
        """指定范围内的随机奇数"""
        odd = random.randrange(left + (1 - left % 2), right, 2)
        return odd

    @classmethod
    def number_random_positive_float(cls, left=0.0, right=1000.0):
        """指定范围内的随机正浮点数"""
        return random.uniform(left, right)

    @classmethod
    def number_random_negative_float(cls, left=-1000.0, right=-0.01):
        """指定范围内的随机负浮点数"""
        return random.uniform(left, right)

    @classmethod
    def number_random_bigint(cls, digits=16):
        """指定位数的大整数"""
        if digits < 1:
            digits = 1
        start = 10**(digits-1)
        end = 10**digits - 1
        return random.randint(start, end)

    @classmethod
    def number_random_scientific(cls):
        """随机科学计数法数字（字符串）"""
        base = random.uniform(1, 10)
        exp = random.randint(1, 10)
        return f'{base:.2f}e{exp}'

    @classmethod
    def number_random_percent(cls):
        """随机百分数（0-100，带两位小数）"""
        return round(random.uniform(0, 100), 2)

    @classmethod
    def number_random_money(cls, left=0.01, right=10000.00):
        """随机金额（两位小数）"""
        return round(random.uniform(left, right), 2)

    @classmethod
    def number_random_mobile(cls):
        """随机手机号码（数字型，11位）"""
        return int('1' + ''.join([str(random.randint(0, 9)) for _ in range(10)]))

    @classmethod
    def number_random_code4(cls):
        """4位数字验证码"""
        return random.randint(1000, 9999)

    @classmethod
    def number_random_code6(cls):
        """6位数字验证码"""
        return random.randint(100000, 999999)

    @classmethod
    def number_random_prime(cls, left=2, right=100):
        """指定范围内的随机质数"""
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return False
            return True
        primes = [i for i in range(left, right+1) if is_prime(i)]
        return random.choice(primes) if primes else None

    @classmethod
    def number_random_nonnegative(cls, left=0, right=1000):
        """随机非负整数"""
        return random.randint(left, right)

    @classmethod
    def number_random_nonzero(cls, left=-1000, right=1000):
        """随机非零整数"""
        n = 0
        while n == 0:
            n = random.randint(left, right)
        return n

    @classmethod
    def number_random_negative_nonzero(cls, left=-1000, right=-1):
        """随机负数（不含0）"""
        return random.randint(left, right)

    @classmethod
    def number_random_negative_even(cls, left=-1000, right=-2):
        """负数范围内的随机偶数"""
        even = random.randrange(left + (left % 2), right, 2)
        return even

    @classmethod
    def number_random_negative_odd(cls, left=-999, right=-1):
        """负数范围内的随机奇数"""
        odd = random.randrange(left + (1 - left % 2), right, 2)
        return odd

    @classmethod
    def number_random_step(cls, left=0, right=100, step=5):
        """指定步长的随机整数"""
        return random.randrange(left, right, step)

    @classmethod
    def number_random_multiple_of_n(cls, n=7, left=0, right=1000):
        """指定范围内的随机N的倍数"""
        candidates = [i for i in range(left, right+1) if i % n == 0]
        return random.choice(candidates) if candidates else None

    @classmethod
    def number_random_decimal(cls, digits=3):
        """随机小数（指定小数位数）"""
        return round(random.uniform(0, 1), digits)

    @classmethod
    def number_positive_infinity(cls):
        """正无穷（float('inf')）"""
        return float('inf')

    @classmethod
    def number_negative_infinity(cls):
        """负无穷（float('-inf')）"""
        return float('-inf')

    @classmethod
    def number_nan(cls):
        """NaN（float('nan')）"""
        return float('nan')

    @classmethod
    def number_random_exponential(cls):
        """随机指数型浮点数（如1.23e+10）"""
        base = random.uniform(1, 10)
        exp = random.randint(1, 10)
        return float(f'{base:.2f}e{exp}')

    @classmethod
    def number_random_fraction_str(cls):
        """随机分数字符串（如'3/7'）"""
        numerator = random.randint(1, 99)
        denominator = random.randint(1, 99)
        return f'{numerator}/{denominator}'

    @classmethod
    def number_random_roman(cls):
        """随机罗马数字字符串（1-3999）"""
        def int_to_roman(num):
            val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
            syb = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
            roman = ''
            i = 0
            while num > 0:
                for _ in range(num // val[i]):
                    roman += syb[i]
                    num -= val[i]
                i += 1
            return roman
        n = random.randint(1, 3999)
        return int_to_roman(n)

    @classmethod
    def number_random_bin_str(cls, digits=8):
        """随机二进制字符串"""
        return bin(random.randint(0, 2**digits-1))[2:].zfill(digits)

    @classmethod
    def number_random_oct_str(cls, digits=6):
        """随机八进制字符串"""
        return oct(random.randint(0, 8**digits-1))[2:]

    @classmethod
    def number_random_hex_str(cls, digits=6):
        """随机十六进制字符串"""
        return hex(random.randint(0, 16**digits-1))[2:]
