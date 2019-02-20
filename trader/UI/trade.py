# -*- coding: utf-8 -*-
"""
@author: Fanchen
@Created At: 2019/1/8 16:29
"""

from PyQt5 import QtCore, QtGui, QtWidgets

from trader.Engine import Event


class TraderWidget(QtWidgets.QWidget):
    signal = QtCore.pyqtSignal(Event)  # 用于定时更新API状态的信号

    # -------------------------------------------------
    def __init__(self, main_engine=None, parent=None):
        super(TraderWidget, self).__init__(parent)

        self.main_engine = main_engine
        self.signal_count = 9  # signal信号的计数器
        self.signal_trigger = 10  # signal信号的触发条件，即每10秒触发一次
        self.signal.connect(self.update_status)  # 将signal信号绑定到对应的槽函数
        self.init_ui()

    # -------------------------------------------------
    def init_ui(self):
        self.setWindowTitle(u"Trade Widget")  # 设置组件标题

        # UI items
        label_code = QtWidgets.QLabel('Code')
        self.text_code = QtWidgets.QLineEdit('', self)
        label_price = QtWidgets.QLabel('Price')
        self.text_price = QtWidgets.QLineEdit('', self)
        label_quantity = QtWidgets.QLabel('Quantity')
        self.text_quantity = QtWidgets.QLineEdit('', self)

        button_buy = QtWidgets.QPushButton('Buy', self)
        button_buy.clicked.connect(self.buy)
        button_sell = QtWidgets.QPushButton('Sell', self)
        button_sell.clicked.connect(self.sell)
        button_close_position = QtWidgets.QPushButton('Close Position', self)
        button_close_position.clicked.connect(self.close_position)
        button_stop = QtWidgets.QPushButton('Stop', self)
        button_stop.clicked.connect(self.stop)

        self.label_gateway = QtWidgets.QLabel('Gateway: ')  # 用于显示所用的Gateway，绿色表示连接畅通，红色则反
        self.label_quotation = QtWidgets.QLabel('Quotation: ')  # 用于显示所用的行情API，绿色表示连接畅通，红色则反

        # UI Layout
        grid = QtWidgets.QGridLayout()
        grid.addWidget(label_code, 1, 1, 1, 2)
        grid.addWidget(self.text_code, 1, 4, 1, 2)
        grid.addWidget(label_price, 2, 1, 1, 2)
        grid.addWidget(self.text_price, 2, 4, 1, 2)
        grid.addWidget(label_quantity, 3, 1, 1, 2)
        grid.addWidget(self.text_quantity, 3, 4, 1, 2)
        h_box = QtWidgets.QHBoxLayout()
        h_box.addStretch(2)
        h_box.addWidget(button_buy)
        h_box.addStretch(1)
        h_box.addWidget(button_sell)
        h_box.addStretch(2)
        vBox = QtWidgets.QVBoxLayout()
        vBox.addStretch(1)
        vBox.addLayout(grid)
        vBox.addStretch(1)
        vBox.addLayout(h_box)
        vBox.addStretch(1)
        vBox.addWidget(button_stop)
        vBox.addWidget(button_close_position)
        vBox.addStretch(5)
        vBox.addWidget(self.label_gateway)
        vBox.addWidget(self.label_quotation)
        vBox.addStretch(3)
        self.setLayout(vBox)

    # -------------------------------------------------
    def buy(self):
        try:
            order = {}
            order['code'] = self.text_code.text()
            order['price'] = float(self.text_price.text())
            order['direction'] = 'Long'
            order['quantity'] = int(self.text_quantity.text())
            self.main_engine.send_order(order)
        except:
            self.main_engine.write_log(e)
            QtWidgets.QMessageBox.critical(self, "Send Order", "Failed !")
        else:
            QtWidgets.QMessageBox.information(self, "Send Order", "Success !")

    # -------------------------------------------------
    def sell(self):
        try:
            order = {}
            order['code'] = self.text_code.text()
            order['price'] = float(self.text_price.text())
            order['direction'] = 'Short'
            order['quantity'] = int(self.text_quantity.text())
            self.main_engine.send_order(order)
        except Exception as e:
            self.main_engine.write_log(e)
            QtWidgets.QMessageBox.critical(self, "Send Order", "Failed !")
        else:
            QtWidgets.QMessageBox.information(self, "Send Order", "Success !")

    # -------------------------------------------------
    def stop(self):
        self.main_engine.stop()

    # -------------------------------------------------
    def close_position(self):
        self.main_engine.close_position()

    # -------------------------------------------------
    # update the status of gateway and quotation API
    def update_status(self, event):
        self.signal_count += 1

        if self.signal_count == self.signal_trigger:
            self.signal_count = 0
            api_status = self.main_engine.get_api_status()
            self.set_api_label(api_status)

    # -------------------------------------------------
    def set_api_label(self, api_status):
        for obj, i, j in [(self.label_gateway, 'gateway_name', 'gateway_status'), (self.label_quotation, 'quotation_name', 'quotation_status')]:
            if api_status.get(i):
                obj.setText("Gateway: " + api_status.get(i))
                if api_status.get(j).lower() in ['connected', 'connect']:
                    palette = QtGui.QPalette()
                    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor('green'))
                    obj.setPalette(palette)
                else:
                    palette = QtGui.QPalette()
                    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor('red'))
                    obj.setPalette(palette)

    # -------------------------------------------------
    def register_to_engine(self, event_type, engine):
        engine.register(event_type, self.signal.emit)
