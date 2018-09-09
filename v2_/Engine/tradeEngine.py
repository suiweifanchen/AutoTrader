# -*- coding: utf-8 -*-
"""
Created at: 2018/6/21 16:04

@Author: Qian
"""

from collections import OrderedDict

from .eventType import *
from .eventEngine import Event, EventEngine


class TradeEngine(EventEngine):

    # -------------------------------------------------
    def __init__(self, account_info):
        super(TradeEngine, self).__init__()

        self.initGateway(account_info)
        self.register(EVENT_TRADE, self.trade)

    # -------------------------------------------------
    def initGateway(self, account_info):
        self.gsCount = 0
        self.gsTrigger = 10
        self.register(EVENT_TIMER, self.updateStatus)
        self.register(EVENT_GATEWAY, self.setGateway)


        self.gatewayDict = OrderedDict()
        # XQ
        from my_modules.trader.API.gateways import XQ
        self.gatewayDict['XQ'] = XQ

        self.gateway = XQ(**account_info)
        self.connectGateway()

    # -------------------------------------------------
    def setGateway(self, event):
        if not isinstance(self.gateway, event.dict_['gateway_class']):
            self.gateway = event.dict_['gateway_class']()

        event.dict_['status'] = self.connectGateway()

    # -------------------------------------------------
    def connectGateway(self):
        status = self.gateway.connect()
        if status is True or status == "Connected":
            self.gatewayStatus = "Connected"
        else:
            self.gatewayStatus = "UnConnected"

        return status

    # -------------------------------------------------
    def updateStatus(self, event):
        self.gsCount += 1

        if self.gsCount == self.gsTrigger:
            self.gsCount = 0
            self.connectGateway()

    # -------------------------------------------------
    def initAccount(self):
        pass

    # -------------------------------------------------
    def trade(self, event):
        if event.dict_['direction'] == "Long":
            event.dict_['data'] = self.gateway.buy(event.dict_['code'], event.dict_['quantity'])
        elif event.dict_['direction'] == "Short":
            event.dict_['data'] = self.gateway.sell(event.dict_['code'], event.dict_['quantity'])
        else:
            pass
