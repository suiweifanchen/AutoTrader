# -*- coding: utf-8 -*-
"""
Created at: 2018/7/13 9:33

@Author: Qian
"""

import datetime
import random
from collections import defaultdict


class BaseGateway:

    # -------------------------------------------------
    def __init__(self):
        pass

    # -------------------------------------------------
    def connect(self):
        return random.choice([True, False])

    # -------------------------------------------------
    def buy(self, code, quantity):
        orderID = str(random.randint(1000,9999))
        order = defaultdict(str)
        order['orderID'] = orderID
        order['code'] = code
        order['direction'] = "Long"
        order['orderQuantity'] = quantity
        order['status'] = "Pending"
        order['gateway'] = "Base"
        order['orderTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {orderID: order}

    # -------------------------------------------------
    def sell(self, code, quantity):
        orderID = str(random.randint(1000,9999))
        order = defaultdict(str)
        order['orderID'] = orderID
        order['code'] = code
        order['direction'] = "Short"
        order['orderQuantity'] = quantity
        order['status'] = "Pending"
        order['gateway'] = "Base"
        order['orderTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {orderID: order}

    # -------------------------------------------------
    def __str__(self):
        return "BaseGateway"
