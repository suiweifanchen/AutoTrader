# -*- coding: utf-8 -*-
"""
Created at: 2018/6/21 17:59

@Author: Qian
"""

import csv
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from collections import OrderedDict

from my_modules.trader.Engine import Event
from my_modules.trader.Engine.eventType import *


################################################
# QTableWidgetItem

class BasicCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, mainEngine=None):
        super(BasicCell, self).__init__()
        self.data = None
        if text:
            self.setContent(text)

    def setContent(self, text):
        if text == '0' or text == '0.0':
            self.setText('')
        else:
            self.setText(text)


class AskCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, mainEngine=None):
        super(AskCell, self).__init__()
        self.data = None
        self.setForeground(QtGui.QColor("black"))
        self.setBackground(QtGui.QColor(160,255,160))

        if text:
            self.setContent(text)

    def setContent(self, text):
        self.setText(text)


class BidCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, mainEngine=None):
        super(BidCell, self).__init__()
        self.data = None
        self.setForeground(QtGui.QColor("black"))
        self.setBackground(QtGui.QColor(255,174,201))

        if text:
            self.setContent(text)

    def setContent(self, text):
        self.setText(text)


class DirectionCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, mainEngine=None):
        super(DirectionCell, self).__init__()
        self.data = None
        if text:
            self.setContent(text)

    def setContent(self, text):
        if text == "Long":
            self.setForeground(QtGui.QColor("red"))
        elif text == "Net":
            self.setForeground(QtGui.QColor("black"))
        elif text == "Short":
            self.setForeground(QtGui.QColor("green"))
        self.setText(text)


# it is used to show the int number
class NumCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, mainEngine=None):
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


# it is used to show `Profit and Loss`
class PnlCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, mainEngine=None):
        super(PnlCell, self).__init__()
        self.data = None
        self.color = ''
        if text:
            pass

    def setContent(self, text):
        self.setText(text)

        try:
            value = float(text)
            if value > 0 and self.color != 'red':
                self.color = 'red'
                self.setForeground(QtGui.QColor('red'))
            elif value <= 0 and self.color != 'green':
                self.color = 'green'
                self.setForeground(QtGui.QColor('green'))
        except ValueError:
            pass


################################################
# Monitor Window

class BasicMonitor(QtWidgets.QTableWidget):
    signal = QtCore.pyqtSignal(type(Event()))

    # -------------------------------------------------
    def __init__(self, mainEngine=None, eventEngine=None, parent=None):
        super(BasicMonitor, self).__init__(parent)

        self.mainEngine = mainEngine
        self.eventEngine = eventEngine

        # 保存表头标签用
        self.headerDict = OrderedDict()  # 有序字典，key是英文名，value是对应的配置字典，如{'chinese': u'中文名', 'english': u'EnglishName', 'cellType': BasicCell}
        self.headerList = []  # 对应self.headerDict.keys()
        self.dataDict = {}
        self.dataKey = ''
        self.eventType = ''
        self.columnResized = False
        self.font = None
        self.saveData = False
        self.sorting = False  # 默认不允许根据表头进行排序，需要的组件可以开启

        self.initMenu()

    # -------------------------------------------------
    def set_headerDict(self, headerDict):
        self.headerDict = headerDict
        self.headerList = headerDict.keys()

    # -------------------------------------------------
    def set_dataKey(self, dataKey):
        self.dataKey = dataKey

    # -------------------------------------------------
    def set_eventType(self, eventType):
        self.eventType = eventType

    # -------------------------------------------------
    def set_font(self, font):
        self.font = font

    # -------------------------------------------------
    def set_saveData(self, saveData):
        self.saveData = saveData

    # -------------------------------------------------
    def set_sorting(self, sorting):
        self.sorting = sorting

    # -------------------------------------------------
    # the menu of right click
    def initMenu(self):
        self.menu = QtWidgets.QMenu(self)

        resizeAction = QtWidgets.QAction(u'Resize Columns', self)
        resizeAction.triggered.connect(self.resizeColumns)
        saveAction = QtWidgets.QAction(u'Save Data', self)
        saveAction.triggered.connect(self.saveToCsv)

        self.menu.addAction(resizeAction)
        self.menu.addAction(saveAction)

    # -------------------------------------------------
    def contextMenuEvent(self, event):
        self.menu.popup(QtGui.QCursor.pos())

    # -------------------------------------------------
    def resizeColumns(self):
        self.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeToContents)

    # -------------------------------------------------
    def saveToCsv(self):
        self.menu.close()  # 先隐藏右键菜单

        path = QtWidgets.QFileDialog.getSaveFileName(self, u'Save Data', '', 'CSV(*.csv)')
        try:
            if path:
                with open(path, 'wb') as f:
                    writer = csv.writer(f)

                    headers = [header.encode('gbk') for header in self.headerList]
                    writer.writerow(headers)

                    for row in range(self.rowCount()):
                        row_data = []
                        for column in range(self.columnCount()):
                            item = self.item(row, column)
                            if item is not None:
                                row_data.append(item.text().encode('gbk'))
                            else:
                                row_data.append('')
                        writer.writerow(row_data)
        except IOError:
            pass

    # -------------------------------------------------
    def initTable(self):
        # 设置表格的列数
        col = len(self.headerDict)
        self.setColumnCount(col)
        #设置表头
        labels = [d['english'] for d in self.headerDict.values()]
        self.setHorizontalHeaderLabels(labels)
        # 关闭左边垂直表头，即表格右边的序号
        self.verticalHeader().setVisible(False)
        # 设置为不可编辑
        self.setEditTriggers(self.NoEditTriggers)
        # 设置行交替颜色
        self.setAlternatingRowColors(True)
        # 设置允许排序
        self.setSortingEnabled(self.sorting)

    # -------------------------------------------------
    # register function into handlers
    def registerEvent(self):
        self.signal.connect(self.updateEvent)  # 将signal信号绑定到updateEvent方法，当触发该信号会调用该方法
        self.eventEngine.register(self.eventType, self.signal.emit)

    # -------------------------------------------------
    def updateEvent(self, event):
        data = event.dict_['data']
        self.updateData(data)

    # -------------------------------------------------
    # update data into table
    def updateData(self, data):
        # 如果允许了排序功能，则插入数据前必须关闭，否则插入新的数据会变乱
        if self.sorting:
            self.setSortingEnabled(False)

        # 如果设置了dataKey，则采用存量更新模式
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
        # 否则采用增量更新模式
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


class LogMonitor(BasicMonitor):
    def __init__(self, mainEngine, eventEngine, parent=None):
        super(LogMonitor, self).__init__(mainEngine, eventEngine, parent)

        d = OrderedDict()
        d['logTime'] = {'chinese': u"时间", 'english': u"Time", 'cellType': BasicCell}
        d['logContent'] = {'chinese': u"日志内容", 'english': u"Content", 'cellType': BasicCell}
        d['gateway'] = {'chinese': u"渠道", 'english': u"Trader", 'cellType': BasicCell}
        self.set_headerDict(d)

        self.set_eventType(EVENT_LOG)
        self.setFont(QtGui.QFont(u'微软雅黑', 12))
        self.initTable()
        self.registerEvent()


class OrderMonitor(BasicMonitor):

    # -------------------------------------------------
    def __init__(self, mainEngine, eventEngine, parent=None):
        super(OrderMonitor, self).__init__(mainEngine, eventEngine, parent)

        d = OrderedDict()
        d['orderID'] = {'chinese': u"订单ID", 'english': u"Order ID", 'cellType': BasicCell}
        d['code'] = {'chinese': u"代码", 'english': u"Code", 'cellType': BasicCell}
        d['name'] = {'chinese': u"名称", 'english': u"Name", 'cellType': BasicCell}
        d['direction'] = {'chinese': u"方向", 'english': u"Direction", 'cellType': DirectionCell}
        d['orderQuantity'] = {'chinese': u"订单数量", 'english': u"Order Quantity", 'cellType': NumCell}
        d['orderPrice'] = {'chinese': u"订单价格", 'english': u"Order Price", 'cellType': NumCell}
        d['status'] = {'chinese': u"状态", 'english': u"Status", 'cellType': BasicCell}
        d['gateway'] = {'chinese': u"渠道", 'english': u"Trader", 'cellType': BasicCell}
        d['orderTime'] = {'chinese': u"下单时间", 'english': u"Order Time", 'cellType': BasicCell}
        d['tradeTime'] = {'chinese': u"成交时间", 'english': u"Trade Time", 'cellType': BasicCell}
        d['cancelTime'] = {'chinese': u"撤销时间", 'english': u"Cancel Time", 'cellType': BasicCell}
        self.set_headerDict(d)

        self.set_dataKey(u"TradeMonitor")
        self.set_eventType(EVENT_TRADE)
        self.setFont(QtGui.QFont(u'微软雅黑', 12))
        self.set_saveData(True)
        self.set_sorting(True)

        self.initTable()
        self.registerEvent()
        self.connectSignal()

    # -------------------------------------------------
    def registerEvent(self):
        self.signal.connect(self.updateEvent)  # 将signal信号绑定到updateEvent方法，当触发该信号会调用该方法
        self.mainEngine.tradeEngine.register(self.eventType, self.signal.emit)

    # -------------------------------------------------
    # cancel the order when be double clicked
    def connectSignal(self):
        self.itemDoubleClicked.connect(self.cancelOrder)

    # -------------------------------------------------
    def cancelOrder(self, cell):
        pass


class PositionMonitor(BasicMonitor):
    def __init__(self, mainEngine, eventEngine, parent=None):
        super(PositionMonitor, self).__init__(mainEngine, eventEngine, parent)

        d = OrderedDict()
        d['code'] = {'chinese': u"代码", 'english': u"Code", 'cellType': BasicCell}
        d['name'] = {'chinese': u"名称", 'english': u"Name", 'cellType': BasicCell}
        d['direction'] = {'chinese': u"方向", 'english': u"Direction", 'cellType': DirectionCell}
        d['price'] = {'chinese': u"价格", 'english': u"Price", 'cellType': NumCell}
        d['position'] = {'chinese': u"订单数量", 'english': u"Order Quantity", 'cellType': NumCell}
        d['gateway'] = {'chinese': u"渠道", 'english': u"Trader", 'cellType': BasicCell}
        self.set_headerDict(d)

        self.set_dataKey("PositionMonitor")
        self.set_eventType(EVENT_POSITION)
        self.setFont(QtGui.QFont(u'微软雅黑', 12))
        self.set_saveData(True)

        self.initTable()
        self.registerEvent()
