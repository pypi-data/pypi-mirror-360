# -*- coding: utf-8 -*-
"""
@author: 彭盛兵
@file: __init__.py.py
@time: 2025/2/20  18:50
"""


from .core import logger, LoggerInitializer, ObServe, ObserveConfig, async_logging_decorator, logging_decorator


__all__ = ["logger",  # 包了一层的logger
           "LoggerInitializer",  # 可以自定义，返回logger
           "ObServe",  # 日志平台服务
           "ObserveConfig",  # 日志平台服务的配置
           "async_logging_decorator",  # 异步装饰器+logging：1. 执行时间
           "logging_decorator"  # 同步装饰器
           ]
