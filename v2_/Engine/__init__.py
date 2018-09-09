# -*- coding: utf-8 -*-
"""
Created at: 2018/6/21 15:21

@Author: Qian
"""

import datetime
from collections import OrderedDict

from .eventEngine import Event, EventEngine
from .tradeEngine import TradeEngine
from .eventType import *


################################################
# 主引擎
class MainEngine:

    # -------------------------------------------------
    def __init__(self, eventEngine, account_info):
        self.todayDate = datetime.datetime.now().strftime("%Y%m%d")

        self.eventEngine = eventEngine
        self.eventEngine.start(timer=False)
        self.dbEngine = None
        self.logEngine = None
        self.requestEngine = None
        self.strategyEngine = None
        self.tradeEngine = TradeEngine(account_info)
        self.tradeEngine.start(timer=True)

        self.dataApi = None
        self.dataApiStatus = "UnConnected"
        self.dataApiDict = OrderedDict()
        self.initDataApi()

    # -------------------------------------------------
    def initDataApi(self):
        self.eventEngine.register(EVENT_DATAAPI, self.connectDataApi)

        # Sina
        from my_modules.trader.API.quotation import Sina
        self.dataApiDict['Sina'] = Sina

        event = Event(EVENT_DATAAPI)
        event.dict_['dataApi_name'] = "Sina"
        event.dict_['dataApi_class'] = Sina
        self.eventEngine.put(event)

    # -------------------------------------------------
    def connectDataApi(self, event):
        if not isinstance(self.dataApi, event.dict_['dataApi_class']):
            self.dataApi = event.dict_['dataApi_class']()

        status = self.dataApi.connect()
        event.dict_['status'] = status
        if status is True or status == "Connected":
            self.dataApiStatus = "Connected"
        else:
            self.dataApiStatus = "UnConnected"

        return status

    # -------------------------------------------------
    def sendOrder(self, orderDict):
        event = Event(type_=EVENT_TRADE)
        event.dict_ = orderDict
        self.tradeEngine.put(event)

    # -------------------------------------------------
    def writeLog(self, content):
        pass

    # -------------------------------------------------
    def exit(self):
        self.eventEngine.stop()
        self.tradeEngine.stop()
