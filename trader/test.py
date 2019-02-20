# -*- coding: utf-8 -*-
"""
@author: Fanchen
@Created At: 2019/1/13 16:07
"""

import sys
from PyQt5 import QtWidgets

from trader.UI import MainWindow
from trader.Engine import MainEngine

app = QtWidgets.QApplication(sys.argv)
me = MainEngine()
# me.start()
mw = MainWindow(me)
mw.show()
sys.exit(app.exec_())

