# -*- coding: utf-8 -*-
"""
Created at: 18-4-8 上午11:07

@Author: Qian
"""

import sys
import time
import datetime
from PyQt5 import QtWidgets

from api.quotation.sina import SinaQuotation
from UI import uiMainWindow, MarketMonitor
from event_engine import EventEngine, EVENT_TIMER

your_stocks = []
sina_quotation = SinaQuotation()
if your_stocks:
    sina_quotation.stock_list = sina_quotation.gen_stock_list(your_stocks)


def test(event):
    t = datetime.datetime.now().strftime("%H:%M:%S")
    stock_data = sina_quotation.market_snapshot()
    event.dict_['data'] = stock_data


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    ee = EventEngine()
    ee.register(EVENT_TIMER, test)

    mw = uiMainWindow(ee)
    mw.show()

    # ee.start()

    sys.exit(app.exec_())
