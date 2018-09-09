# -*- coding: utf-8 -*-
"""
Created at: 2018/7/10 17:41

@Author: Qian
"""

from .helper import BaseDataApi


class Sina(BaseDataApi):
    def __init__(self):
        super(Sina, self).__init__()

    def __str__(self):
        return "Sina"
