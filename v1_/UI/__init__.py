# -*- coding: utf-8 -*-
"""
Created at: 18-5-16 上午8:19

@Author: Qian
"""

from collections import OrderedDict
from PyQt5 import QtWidgets, QtCore, QtGui

import sys
sys.path.append('..')
from event_engine import Event, EVENT_TIMER


DIRECTION_NET = u'net'
DIRECTION_LONG = u'long'
DIRECTION_SHORT = u'short'
COLOR_RED = QtGui.QColor('red')
COLOR_GREEN = QtGui.QColor('green')


class uiMainWindow(QtWidgets.QWidget):
    def __init__(self, eventEngine):
        super(uiMainWindow, self).__init__()
        self.eventEngine = eventEngine
        self.initUI()

    def initUI(self):
        grid = QtWidgets.QGridLayout()
        self.setLayout(grid)
        self.setGeometry(300, 200, 650, 400)
        self.setWindowTitle('MyTrader')

        widgetMarketM = MarketMonitor(self.eventEngine)
        # docker = QtWidgets.QDockWidget(u'Market Data')
        # docker.setWidget(widgetMarketM)
        # docker.setObjectName(u'Market Data')
        # docker.setFeatures(docker.DockWidgetFloatable | docker.DockWidgetMovable)

        button_start = QtWidgets.QPushButton('开始')
        button_start.clicked.connect(self.start)
        button_restart = QtWidgets.QPushButton('恢复')
        button_restart.clicked.connect(self.restart)
        button_stop = QtWidgets.QPushButton('结束')
        button_stop.clicked.connect(self.stop)

        grid.addWidget(widgetMarketM, 0, 0, 8, 5)
        grid.setSpacing(10)
        grid.addWidget(button_start, 9, 2)
        grid.addWidget(button_restart, 9, 3)
        grid.addWidget(button_stop, 9, 4)

    def start(self):
        self.eventEngine.start()

    def restart(self):
        self.eventEngine.restart()

    def stop(self):
        self.eventEngine.stop()


class BasicCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, engine=None):
        super(BasicCell, self).__init__()
        self.data = None
        if text:
            self.setContent(text)

    def setContent(self, text):
        """设置内容"""
        if text == '0' or text == '0.0':
            self.setText('')
        else:
            self.setText(text)


class NumCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, engine=None):
        super(NumCell, self).__init__()
        self.data = None
        if text:
            self.setContent(text)

    def setContent(self, text):
        try:
            num = int(text)
            self.setData(QtCore.Qt.DisplayRole, num)
        except ValueError:
            self.setText(text)


class DirectionCell(QtWidgets.QTableWidgetItem):
    """用来显示买卖方向的单元格"""

    def __init__(self, text=None, engine=None):
        super(DirectionCell, self).__init__()
        self.data = None
        if text:
            self.setContent(text)

    def setContent(self, text):
        """设置内容"""
        if text == DIRECTION_LONG or text == DIRECTION_NET:
            self.setForeground(QtGui.QColor('red'))
        elif text == DIRECTION_SHORT:
            self.setForeground(QtGui.QColor('green'))
        self.setText(text)


class BidCell(QtWidgets.QTableWidgetItem):
    """买价单元格"""

    def __init__(self, text=None, engine=None):
        super(BidCell, self).__init__()
        self.data = None

        self.setForeground(QtGui.QColor('black'))
        self.setBackground(QtGui.QColor(255, 174, 201))

        if text:
            self.setContent(text)

    def setContent(self, text):
        """设置内容"""
        try:
            self.setData(QtCore.Qt.DisplayRole, text)
        except ValueError:
            self.setText(text)


class AskCell(QtWidgets.QTableWidgetItem):
    """卖价单元格"""

    def __init__(self, text=None, engine=None):
        super(AskCell, self).__init__()
        self.data = None

        self.setForeground(QtGui.QColor('black'))
        self.setBackground(QtGui.QColor(160, 255, 160))

        if text:
            self.setContent(text)

    def setContent(self, text):
        """设置内容"""
        try:
            self.setData(QtCore.Qt.DisplayRole, text)
        except ValueError:
            self.setText(text)


class PnlCell(QtWidgets.QTableWidgetItem):
    """显示盈亏的单元格"""

    def __init__(self, text=None, engine=None):
        super(PnlCell, self).__init__()
        self.data = None
        self.color = ''
        if text:
            self.setContent(text)

    def setContent(self, text):
        """设置内容"""
        self.setText(text)

        try:
            value = float(text)
            if value >= 0 and self.color != 'red':
                self.color = 'red'
                self.setForeground(COLOR_RED)
            elif value < 0 and self.color != 'green':
                self.color = 'green'
                self.setForeground(COLOR_GREEN)
        except ValueError:
            pass


class MarketMonitor(QtWidgets.QTableWidget):
    signal = QtCore.pyqtSignal(type(Event()))
    def __init__(self, eventEngine=None):
        super(MarketMonitor, self).__init__()
        self.eventEngine = eventEngine
        self.eventType = EVENT_TIMER
        self.dataDict = {}
        self.dataKey = 'code'
        self.sorting = True
        self.setHeaderDict()
        self.initUI()

    def initUI(self):
        # 设置表格的列数
        col = len(self.headerDict)
        self.setColumnCount(col)
        # 设置列表头
        labels = [d['chinese'] for d in self.headerDict.values()]
        self.setHorizontalHeaderLabels(labels)
        # 关闭左边的垂直表头
        self.verticalHeader().setVisible(False)
        # 设为不可编辑
        self.setEditTriggers(self.NoEditTriggers)
        # 设为行交替颜色
        self.setAlternatingRowColors(True)
        # 设置允许排序
        self.setSortingEnabled(self.sorting)
        # 注册事件监听
        self.registerEvent()

    def setHeaderDict(self):
        """设置表头有序字典"""
        d = OrderedDict()
        d['time'] = {'chinese': u'时间', 'cellType': BasicCell}
        d['name'] = {'chinese': u'名称', 'cellType': BasicCell}
        d['code'] = {'chinese': u'代码', 'cellType': BasicCell}
        d['now'] = {'chinese': u'现价', 'cellType': NumCell}
        d['bid1'] = {'chinese': u'买一', 'cellType': BidCell}
        d['ask1'] = {'chinese': u'卖一', 'cellType': AskCell}
        self.headerDict = d
        self.headerList = d.keys()

    def registerEvent(self):
        self.signal.connect(self.updateEvent)
        self.eventEngine.register(self.eventType, self.signal.emit)

    def updateEvent(self, event):
        data = event.dict_['data']
        self.updateDate(data)

    def updateDate(self, data):
        # 如果允许了排序功能，则插入数据前必须关闭，否则插入新的数据会变乱
        if self.sorting:
            self.setSortingEnabled(False)

        if self.dataKey:
            for i in data:
                if i not in self.dataDict:
                    self.insertRow(0)
                    d = {}
                    for n, header in enumerate(self.headerList):
                        content = data[i][header]
                        cellType = self.headerDict[header]['cellType']
                        cell = cellType(content, self.eventEngine)

                        cell.data = data[i]
                        self.setItem(0, n, cell)
                        d[header] = cell
                    self.dataDict[i] = d
                else:
                    d = self.dataDict[i]
                    for header in self.headerList:
                        content = data[i][header]
                        cell = d[header]
                        cell.setContent(content)

                        cell.data = data[i]
        else:
            for i in data:
                self.insertRow(0)
                for n, header in enumerate(self.headerList):
                    content = data[i][header]
                    cellType = self.headerDict[header]['cellType']
                    cell = cellType(content, self.eventEngine)

                    cell.data = data[i]
                    self.setItem(0, n, cell)

        # 调整列宽
        if not self.columnResized:
            self.resizeColumns()
            self.columnResized = True

        # 重新打开排序
        if self.sorting:
            self.setSortingEnabled(True)
