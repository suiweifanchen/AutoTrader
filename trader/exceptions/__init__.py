# -*- coding: utf-8 -*-
"""
@author: Fanchen
@Created At: 2018/12/17 14:42
"""


class InitialException(Exception):
    """对象初始化异常"""


class ParamException(Exception):
    """参数异常，提供的参数不符合要求"""


class RequestException(Exception):
    """请求异常"""
