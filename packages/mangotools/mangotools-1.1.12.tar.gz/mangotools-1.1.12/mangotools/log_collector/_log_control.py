# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
import logging
import os
from logging import handlers

import colorlog


class LogHandler:
    """ 日志打印封装"""
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self, file_name: str, level: str):
        log_dir = os.path.dirname(file_name)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        self.logger = logging.getLogger(file_name)
        fmt = "%(levelname)-8s[%(asctime)s][%(filename)s:%(lineno)d] %(message)s"
        format_str = logging.Formatter(fmt)
        self.logger.setLevel(self.level_relations.get(level, logging.DEBUG))

        screen_output = logging.StreamHandler()
        screen_output.setFormatter(self.log_format(level))

        time_rotating = handlers.TimedRotatingFileHandler(
            filename=file_name,
            when="D",
            backupCount=3,
            encoding='utf-8'
        )
        time_rotating.setFormatter(format_str)

        self.logger.addHandler(screen_output)
        self.logger.addHandler(time_rotating)

    @classmethod
    def log_format(cls, level):
        if level in ["debug", "info"]:
            fmt = "%(log_color)s[%(asctime)s] [%(levelname)s]: %(message)s"
        else:
            fmt = "%(log_color)s[%(asctime)s] [%(filename)s-->行:%(lineno)d] [%(levelname)s]: %(message)s"
        format_str = colorlog.ColoredFormatter(
            fmt,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'purple',
            }
        )
        return format_str
