# -*- coding: utf-8 -*-
"""
Created at: 2018/6/21 17:56

@Author: Qian
"""

from my_modules.trader.UI.helper import *


class MarketWindow(QtWidgets.QWidget):
    signal_dataApi = QtCore.pyqtSignal(type(Event()))

    def __init__(self, mainEngine, eventEngine, parent=None):
        super(MarketWindow, self).__init__()
        self.mainEngine = mainEngine
        self.eventEngine = eventEngine
        self.initUI()

    def initUI(self):
        self.resize(650, 400)
        self.setWindowTitle(u'Market')

        widgetMarketM = MarketMonitor(self.mainEngine, self.eventEngine)
        self.label_dataApi = QtWidgets.QLabel("Data Api: " + self.mainEngine.dataApi.__str__())
        button_start = QtWidgets.QPushButton('start')
        button_start.clicked.connect(self.start)
        button_restart = QtWidgets.QPushButton('restart')
        button_restart.clicked.connect(self.restart)
        button_stop = QtWidgets.QPushButton('stop')
        button_stop.clicked.connect(self.stop)

        grid = QtWidgets.QGridLayout()
        grid.addWidget(widgetMarketM, 0, 0, 8, 5)
        grid.setSpacing(10)
        grid.addWidget(self.label_dataApi, 9, 0)
        grid.addWidget(button_start, 9, 2)
        grid.addWidget(button_restart, 9, 3)
        grid.addWidget(button_stop, 9, 4)

        self.setLayout(grid)
        self.signal_dataApi.connect(self.updateDataApiStatus)
        self.eventEngine.register(EVENT_DATAAPI, self.signal_dataApi.emit)

    def start(self):
        pass

    def restart(self):
        pass

    def stop(self):
        pass

    def updateDataApiStatus(self, event):
        self.label_dataApi.setText("Data Api: " + event.dict_['dataApi_name'])
        if event.dict_['status'] is True:
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor('green'))
            self.label_dataApi.setPalette(palette)
        else:
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor('red'))
            self.label_dataApi.setPalette(palette)


class MarketMonitor(BasicMonitor):
    def __init__(self, mainEngine, eventEngine, parent=None):
        super(MarketMonitor, self).__init__(mainEngine, eventEngine, parent)

        d = OrderedDict()
        d['time'] = {'chinese': u'时间', 'english': u'Time', 'cellType': BasicCell}
        d['name'] = {'chinese': u'名称', 'english': u'Name', 'cellType': BasicCell}
        d['code'] = {'chinese': u'代码', 'english': u'Code', 'cellType': BasicCell}
        d['now'] = {'chinese': u'现价', 'english': u'Now', 'cellType': NumCell}
        d['bid1'] = {'chinese': u'买一', 'english': u'Bid1', 'cellType': BidCell}
        d['ask1'] = {'chinese': u'卖一', 'english': u'Ask1', 'cellType': AskCell}

        self.set_headerDict(d)
        self.set_dataKey('MarketMonitor')
        self.set_eventType(EVENT_TIMER)
        self.setFont(QtGui.QFont(u'微软雅黑', 12))
        self.set_sorting(False)
        self.initTable()
        self.registerEvent()


if __name__ == '__main__':
    pass
