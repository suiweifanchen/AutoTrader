# -*- coding: utf-8 -*-
"""
Created at: 2018/7/9 14:30

@Author: Qian
"""

import sys
import json
from PyQt5 import QtWidgets

from my_modules.trader.Engine import MainEngine, EventEngine
from my_modules.trader.UI import MainWindow

app = QtWidgets.QApplication(sys.argv)
ee = EventEngine()


me = MainEngine(ee)
mw = MainWindow(me, ee)
mw.show()
sys.exit(app.exec_())
