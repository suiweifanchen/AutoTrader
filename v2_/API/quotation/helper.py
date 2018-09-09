# -*- coding: utf-8 -*-
"""
Created at: 2018/7/13 9:39

@Author: Qian
"""


class BaseDataApi:
    def __init__(self):
        pass

    def connect(self):
        return False

    def __str__(self):
        return "BaseDataApi"
