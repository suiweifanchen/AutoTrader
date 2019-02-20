# -*- coding: utf-8 -*-
"""
@author: Fanchen
@Created At: 2018/12/17 14:41
"""

import datetime

from .eventType import *
from .eventEngine import *
from trader.API import BaseGateway, Sina, XQ


class LogEngine(EventEngine):
    def __init__(self):
        super(LogEngine, self).__init__()


class TradeEngine(EventEngine):
    def __init__(self):
        super(TradeEngine, self).__init__()


# 主引擎
class MainEngine:
    # 持仓信息每10秒更新一次，程序启动时更新一次
    __position_flag = 9
    __position_trigger = 10

    # -------------------------------------------------
    def __init__(self):
        self.gateway = XQ()
        self.gateway_list = [XQ, ]  # 存放可用的gateway类
        self.quotation = Sina()  # 默认使用新浪行情
        self.quotation_list = [Sina, ]  # 存放可用的quotation类

        # 初始化事件引擎，并注册handler
        self.event_engine = EventEngine()
        self.event_engine.register(EVENT_TIMER, self.get_market_data)  # 定时获取行情信息
        self.event_engine.register(EVENT_TIMER, self.get_position_data)  # 定时获取持仓信息

        # 初始化交易引擎
        self.trade_engine = TradeEngine()
        # 初始化日志引擎
        self.log_engine = LogEngine()

    # -------------------------------------------------
    def get_market_data(self, event):
        market_data = self.quotation.get_market_data()
        event.dict_['Market'] = market_data

    # -------------------------------------------------
    def get_position_data(self, event):
        # 根据一定事件间隔更新一次持仓信息
        self.__position_flag += 1
        if self.__position_trigger == self.__position_flag:
            self.gateway.update_portfolio()

        position = self.gateway.get_position()
        event.dict_['Position'] = position
        self.__position_flag = 0

    # -------------------------------------------------
    def send_order(self, order={}):
        pass

    # -------------------------------------------------
    def close_position(self):
        pass

    # -------------------------------------------------
    def start(self):
        self.event_engine.start()
        self.log_engine.start(timer=False)  # 日志引擎不开启计时器

    # -------------------------------------------------
    def stop(self):
        pass

    # -------------------------------------------------
    def cancel_order(self, order_id=''):
        pass

    # -------------------------------------------------
    def get_api_status(self):
        return {
            "gateway_name": "BaseGateway",
            "gateway_status": "connected",
            "quotation_name": "BaseQuotation",
            "quotation_status": "connected",
        }

    # -------------------------------------------------
    def write_log(self, content):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event = Event(EVENT_LOG)
        log = {}
        log['logTime'] = now
        log['logContent'] = content
        event.dict_['Log'] = {now: log}
        self.log_engine.put(event)

    # -------------------------------------------------
    def exit(self):
        pass
