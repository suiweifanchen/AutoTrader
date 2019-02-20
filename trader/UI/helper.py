# -*- coding: utf-8 -*-
"""
@author: Fanchen
@Created At: 2018/12/19 13:57
"""

import csv
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from datetime import datetime
from collections import OrderedDict

from trader.Engine import Event
from trader.Engine.eventType import *


################################################
# QTableWidgetItem

class BasicCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, main_engine=None):
        super(BasicCell, self).__init__()
        self.data = None
        if text:
            self.set_content(text)

    def set_content(self, text):
        self.setText(str(text))


class AskCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, main_engine=None):
        super(AskCell, self).__init__()
        self.data = None
        self.setForeground(QtGui.QColor("black"))
        self.setBackground(QtGui.QColor(160, 255, 160))

        if text:
            self.set_content(text)

    def set_content(self, text):
        self.setText(str(text))


class BidCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, main_engine=None):
        super(BidCell, self).__init__()
        self.data = None
        self.setForeground(QtGui.QColor("black"))
        self.setBackground(QtGui.QColor(255, 174, 201))

        if text:
            self.set_content(text)

    def set_content(self, text):
        self.setText(str(text))


class DirectionCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, main_engine=None):
        super(DirectionCell, self).__init__()
        self.data = None
        if text:
            self.set_content(text)

    def set_content(self, text):
        if text == "Long":
            self.setForeground(QtGui.QColor("red"))
        elif text == "Net":
            self.setForeground(QtGui.QColor("black"))
        elif text == "Short":
            self.setForeground(QtGui.QColor("green"))
        self.setText(text)


# it is used to show the int number
class NumCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, main_engine=None):
        super(NumCell, self).__init__()
        self.data = None
        if text:
            self.set_content(text)

    def set_content(self, text):
        try:
            num = int(text)
            self.setData(QtCore.Qt.DisplayRole, num)
        except ValueError:
            self.setText(str(text))


# it is used to show `Profit and Loss`
class PnlCell(QtWidgets.QTableWidgetItem):
    def __init__(self, text=None, main_engine=None):
        super(PnlCell, self).__init__()
        self.data = None
        self.color = ''
        if text:
            self.set_content(text)

    def set_content(self, text):
        self.setText(str(text))

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
# Monitor Table

class BasicMonitor(QtWidgets.QTableWidget):
    signal = QtCore.pyqtSignal(Event)  # 用于触发 槽update_event() 的信号

    # -------------------------------------------------
    def __init__(self, main_engine=None, parent=None):
        super(BasicMonitor, self).__init__(parent)

        self.main_engine = main_engine

        self.name = 'Basic'  # 用于保存类型名称
        # 保存表头标签用
        # self.header_dict 为有序字典，key是英文名，value是对应的配置字典
        # 例如 {'EnglishName': {'chinese': u'中文名', 'english': u'EnglishName', 'cellType': BasicCell}}
        # self.header_list 对应 self.headerDict.keys()
        self.header_dict = OrderedDict()
        self.header_list = []

        self.data_dict = {}  # 用于保存表中每个单元（cell）,形如{"000001":{"code": cell_1, "name": cell_2, ...}, ...}
        self.data_key = ''  # 若设置了data_key，则根据data_key进行存量更新，否则采用增量更新模式

        self.column_resized = False  # 用于调整列宽,仅第一次更新数据时使用
        self.sorting = False  # 排序功能，默认不允许根据表头进行排序
        self.font = None  # 设置表格字体类型

        self.init_menu()  # 初始化右键菜单
        self.signal.connect(self.update_event)  # 将信号连接到槽函数

    # -------------------------------------------------
    def init_table(self, lagrange='english'):
        # 设置表格列数
        col = len(self.header_dict)
        self.setColumnCount(col)
        # 设置表头
        labels = [d[lagrange] for d in self.header_dict.values()]
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
    # the menu of right click
    def init_menu(self):
        self.menu = QtWidgets.QMenu(self)

        resize_action = QtWidgets.QAction('Resize Columns', self)
        resize_action.triggered.connect(self.resize_columns)
        save_action = QtWidgets.QAction('Save to CSV', self)
        save_action.triggered.connect(self.save_to_csv)

        self.menu.addAction(resize_action)
        self.menu.addAction(save_action)

    # -------------------------------------------------
    def contextMenuEvent(self, event):
        self.menu.popup(QtGui.QCursor.pos())

    # -------------------------------------------------
    # set the table headers
    def set_header_dict(self, dict_):
        self.header_dict = dict_
        self.header_list = self.header_dict.keys()

    # -------------------------------------------------
    def set_font(self, font):
        self.font = font

    # -------------------------------------------------
    def set_sorting(self, sorting):
        self.sorting = sorting

    # -------------------------------------------------
    def set_data_key(self, data_key):
        self.data_key = data_key

    # -------------------------------------------------
    # register the `update_event` into the handlers
    def register_to_engine(self, event_type, engine):
        engine.register(event_type, self.signal.emit)

    # -------------------------------------------------
    # update the data in table according to the data in `event.dict_`
    def update_event(self, event):
        data = event.dict_.get(self.name)
        if data:
            self.update_data(data)

    # -------------------------------------------------
    def update_data(self, data):
        """
        Update the table according the parameter `data`
        :param data: A dict, like {"000001":{"code": "000001", "name": "平安银行", ...}, ...}
        :return: None
        """
        # 如果开启了排序功能，先关闭排序功能
        if self.sorting:
            self.setSortingEnabled(False)

        # 如果设置了data_key，则采用存量更新模式，否则采用增量更新模式。
        if self.data_key:
            for key in data:
                # 取出data_dict中对应key的数据进行更新。若是新加入的key，则插入新的一行并加进data_dict中。
                if key in self.data_dict:
                    d = self.data_dict[key]
                else:
                    self.insertRow(0)
                    d = {}
                    for n, header in enumerate(self.header_list):
                        cell_type = self.header_dict[header]["cell_type"]
                        cell = cell_type()
                        self.setItem(0, n, cell)
                        d[header] = cell
                    self.data_dict[key] = d

                for header in self.header_list:
                    cell = d[header]
                    content = data[key][header]
                    cell.set_content(content)
                    cell.data = data[key]

        else:
            for key in data:
                self.insertRow(0)
                for n, header in enumerate(self.header_list):
                    content = data[key][header]
                    cell_type = self.header_dict[header]["cell_type"]
                    cell = cell_type(content)
                    self.setItem(0, n, cell)

        # 若是第一次更新数据，则在完成更新后调整列宽
        if not self.column_resized:
            self.resize_columns()
            self.column_resized = True

        # 重新打开拍寻
        if self.sorting:
            self.setSortingEnabled(True)

    # -------------------------------------------------
    def resize_columns(self):
        self.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeToContents)

    # -------------------------------------------------
    def save_to_csv(self):
        self.menu.close()  # 先关闭菜单栏

        # 获取文件路径
        path = QtWidgets.QFileDialog.getSaveFileName(
            self, '%s-%s' % (self.name, datetime.now().strftime("%Y%m%d_%H%M%S")), '', 'CSV(*.csv)'
        )

        try:
            # 打开文件，准备写入数据
            if path:
                with open(path, 'wb') as f:
                    writer = csv.writer(f)

                    # 写入表头
                    headers = [header.encode('gbk') for header in self.headerList]
                    writer.writerow(headers)
                    # 写入每行数据
                    for row in range(self.rowCount()):
                        row_data = []
                        for column in range(self.columnCount()):
                            item = self.item(row, column)
                            if item is not None:
                                row_data.append(item.text().encode('gbk'))
                            else:
                                row_data.append(''.encode('gbk'))
                        writer.writerow(row_data)
        except IOError as e:
            print(e)


class MarketMonitor(BasicMonitor):
    def __init__(self, main_engine=None, parent=None):
        super(MarketMonitor, self).__init__(main_engine, parent)
        self.name = "Market"

        d = OrderedDict()
        d['time'] = {'chinese': u'时间', 'english': u'Time', 'cell_type': BasicCell}
        d['name'] = {'chinese': u'名称', 'english': u'Name', 'cell_type': BasicCell}
        d['code'] = {'chinese': u'代码', 'english': u'Code', 'cell_type': BasicCell}
        d['now'] = {'chinese': u'现价', 'english': u'Now', 'cell_type': BasicCell}
        d['ask3_volume'] = {'chinese': u'卖三 - 量', 'english': u'Ask3_v', 'cell_type': NumCell}
        d['ask3'] = {'chinese': u'卖三', 'english': u'Ask3', 'cell_type': AskCell}
        d['ask2_volume'] = {'chinese': u'卖二 - 量', 'english': u'Ask2_v', 'cell_type': NumCell}
        d['ask2'] = {'chinese': u'卖二', 'english': u'Ask2', 'cell_type': AskCell}
        d['ask1_volume'] = {'chinese': u'卖一 - 量', 'english': u'Ask1_v', 'cell_type': NumCell}
        d['ask1'] = {'chinese': u'卖一', 'english': u'Ask1', 'cell_type': AskCell}
        d['bid1'] = {'chinese': u'买一', 'english': u'Bid1', 'cell_type': BidCell}
        d['bid1_volume'] = {'chinese': u'买一 - 量', 'english': u'Bid1_v', 'cell_type': NumCell}
        d['bid2'] = {'chinese': u'买二', 'english': u'Bid2', 'cell_type': BidCell}
        d['bid2_volume'] = {'chinese': u'买二 - 量', 'english': u'Bid2_v', 'cell_type': NumCell}
        d['bid3'] = {'chinese': u'买三', 'english': u'Bid3', 'cell_type': BidCell}
        d['bid3_volume'] = {'chinese': u'买三 - 量', 'english': u'Bid3_v', 'cell_type': NumCell}
        self.set_header_dict(d)
        self.init_table()

        self.set_data_key(u"code")  # 设置data_key，表格采用存量更新模式
        self.set_font(QtGui.QFont(u'微软雅黑', 12))
        self.set_sorting(True)

        # 需要在对应引擎中注册，但不在此处
        # self.register_to_engine(EVENT_TIMER, EventEngine)  # 注册到计时器事件中，每秒刷新一次


class LogMonitor(BasicMonitor):
    def __init__(self, main_engine=None, parent=None):
        super(LogMonitor, self).__init__(main_engine, parent)
        self.name = "Log"

        d = OrderedDict()
        d['logTime'] = {'chinese': u"时间", 'english': u"Time", 'cell_type': BasicCell}
        d['logContent'] = {'chinese': u"日志内容", 'english': u"Content", 'cell_type': BasicCell}
        self.set_header_dict(d)
        self.init_table()

        self.set_font(QtGui.QFont(u'微软雅黑', 12))

        # 需要在对应引擎中注册，但不在此处
        # self.register_to_engine(EVENT_LOG, LogEngine)


class OrderMonitor(BasicMonitor):
    def __init__(self, main_engine, parent=None):
        super(OrderMonitor, self).__init__(main_engine, parent)
        self.name = "Order"

        d = OrderedDict()
        d['orderID'] = {'chinese': u"订单ID", 'english': u"Order ID", 'cell_type': BasicCell}
        d['code'] = {'chinese': u"代码", 'english': u"Code", 'cell_type': BasicCell}
        d['name'] = {'chinese': u"名称", 'english': u"Name", 'cell_type': BasicCell}
        d['direction'] = {'chinese': u"方向", 'english': u"Direction", 'cell_type': DirectionCell}
        d['orderQuantity'] = {'chinese': u"订单数量", 'english': u"Order Quantity", 'cell_type': NumCell}
        d['orderPrice'] = {'chinese': u"订单价格", 'english': u"Order Price", 'cell_type': NumCell}
        d['status'] = {'chinese': u"状态", 'english': u"Status", 'cell_type': BasicCell}
        d['gateway'] = {'chinese': u"渠道", 'english': u"Trader", 'cell_type': BasicCell}
        d['orderTime'] = {'chinese': u"下单时间", 'english': u"Order Time", 'cell_type': BasicCell}
        d['tradeTime'] = {'chinese': u"成交时间", 'english': u"Trade Time", 'cell_type': BasicCell}
        d['cancelTime'] = {'chinese': u"撤销时间", 'english': u"Cancel Time", 'cell_type': BasicCell}
        self.set_header_dict(d)
        self.init_table()

        self.set_data_key(u"orderID")  # 设置data_key，表格采用存量更新模式
        self.set_font(QtGui.QFont(u'微软雅黑', 12))
        self.set_sorting(True)
        self.connect_signal()

        # 需要在对应引擎中注册，但不在此处
        # self.register_to_engine(EVENT_TIMER, EventEngine)  # 注册到计时器事件中，每10秒刷新一次
        # self.register_to_engine(EVENT_TRADE, TradeEngine)  # 注册到交易事件中，每次交易时刷新

    # -------------------------------------------------
    # cancel the order when be double clicked
    def connect_signal(self):
        self.itemDoubleClicked.connect(self.cancel_order)

    # -------------------------------------------------
    def cancel_order(self, cell):
        order = cell.data
        self.main_engine.cancel_order(order['orderID'])


class PositionMonitor(BasicMonitor):
    def __init__(self, main_engine=None, parent=None):
        super(PositionMonitor, self).__init__(main_engine, parent)
        self.name = "Position"

        d = OrderedDict()
        d['code'] = {'chinese': u"代码", 'english': u"Code", 'cell_type': BasicCell}
        d['name'] = {'chinese': u"名称", 'english': u"Name", 'cell_type': BasicCell}
        d['direction'] = {'chinese': u"方向", 'english': u"Direction", 'cell_type': DirectionCell}
        d['cost'] = {'chinese': u"成本", 'english': u"Cost", 'cell_type': NumCell}
        d['volume'] = {'chinese': u"持仓量", 'english': u"volume", 'cell_type': NumCell}
        d['gateway'] = {'chinese': u"渠道", 'english': u"Trader", 'cell_type': BasicCell}
        self.set_header_dict(d)
        self.init_table()

        self.set_data_key(u"code")  # 设置data_key，表格采用存量更新模式
        self.set_font(QtGui.QFont(u'微软雅黑', 12))
        self.set_sorting(True)

        # 需要在对应引擎中注册，但不在此处
        # self.register_to_engine(EVENT_TIMER, EventEngine)  # 注册到计时器事件中，每10秒刷新一次
        # self.register_to_engine(EVENT_TRADE, TradeEngine)  # 注册到交易事件中，每次交易时刷新
