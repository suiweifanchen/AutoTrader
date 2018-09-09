# -*- coding: utf-8 -*-
"""
Created at: 2018/6/21 17:57

@Author: Qian
"""

from PyQt5 import QtCore, QtGui, QtWidgets

from my_modules.trader.Engine import Event
from my_modules.trader.Engine.eventType import *


class TradeWindow(QtWidgets.QWidget):
    signal_Gateway = QtCore.pyqtSignal(type(Event()))

    # -------------------------------------------------
    def __init__(self, mainEngine, eventEngine):
        super(TradeWindow, self).__init__()

        self.mainEngine = mainEngine
        self.eventEngine = eventEngine

        self.initUI()

    # -------------------------------------------------
    def initUI(self):
        self.setWindowTitle(u'Trade')
        # self.resize(200, 350)
        # self.setMaximumWidth(200)
        # self.setMinimumHeight(350)

        # UI items
        button_Buy = QtWidgets.QPushButton(u'Buy', self)
        button_Buy.clicked.connect(self.buy)
        button_Sell = QtWidgets.QPushButton(u'Sell', self)
        button_Sell.clicked.connect(self.sell)
        button_ClPo = QtWidgets.QPushButton(u'Close Position',self)
        button_ClPo.clicked.connect(self.close_position)
        button_Stop = QtWidgets.QPushButton(u'Stop', self)
        button_Stop.clicked.connect(self.stop)
        label_Code = QtWidgets.QLabel('Code')
        label_Quantity = QtWidgets.QLabel('Quantity')
        self.text_Code = QtWidgets.QLineEdit('', self)
        self.text_Quantity = QtWidgets.QLineEdit('', self)
        self.label_Gateway = QtWidgets.QLabel('GateWay: ')
        self.label_Status = QtWidgets.QLabel('Status: ')

        # UI layout
        grid = QtWidgets.QGridLayout()
        grid.addWidget(label_Code, 1, 1, 1, 2)
        grid.addWidget(self.text_Code, 1, 4, 1, 2)
        grid.addWidget(label_Quantity, 2, 1, 1, 2)
        grid.addWidget(self.text_Quantity, 2, 4, 1, 2)
        hBox = QtWidgets.QHBoxLayout()
        hBox.addStretch(2)
        hBox.addWidget(button_Buy)
        hBox.addStretch(1)
        hBox.addWidget(button_Sell)
        hBox.addStretch(2)
        vBox = QtWidgets.QVBoxLayout()
        vBox.addStretch(1)
        vBox.addLayout(grid)
        vBox.addStretch(1)
        vBox.addLayout(hBox)
        vBox.addStretch(3)
        vBox.addWidget(self.label_Gateway)
        vBox.addWidget(self.label_Status)
        vBox.addStretch(5)
        vBox.addWidget(button_Stop)
        vBox.addWidget(button_ClPo)
        self.setLayout(vBox)

        self.initGatewayStatus()

    # -------------------------------------------------
    def buy(self):
        try:
            orderDict = {}
            orderDict['direction'] = "Long"
            orderDict['code'] = self.text_Code.text()
            orderDict['quantity'] = self.text_Quantity.text()
            self.mainEngine.sendOrder(orderDict)
        except:
            QtWidgets.QMessageBox.critical(self, "Send Order", "Failed")
        else:
            QtWidgets.QMessageBox.about(self, "Send Order", "Success")

    # -------------------------------------------------
    def sell(self):
        try:
            orderDict = {}
            orderDict['direction'] = "Short"
            orderDict['code'] = self.text_Code.text()
            orderDict['quantity'] = self.text_Quantity.text()
            self.mainEngine.sendOrder(orderDict)
        except:
            QtWidgets.QMessageBox.critical(self, "Send Order", "Failed")
        else:
            QtWidgets.QMessageBox.about(self, "Send Order", "Success")

    # -------------------------------------------------
    def close_position(self):
        pass

    # -------------------------------------------------
    def stop(self):
        pass

    # -------------------------------------------------
    def initGatewayStatus(self):
        self.updateGatewayStatus()

        self.signal_Gateway.connect(self.updateGatewayStatus)
        self.mainEngine.tradeEngine.register(EVENT_TIMER, self.signal_Gateway.emit)

    # -------------------------------------------------
    def updateGatewayStatus(self):
        self.label_Gateway.setText('GateWay: ' + self.mainEngine.tradeEngine.gateway.__str__())
        if self.mainEngine.tradeEngine.gatewayStatus == "Connected":
            self.label_Status.setText('Status: Connected')
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor('green'))
            self.label_Status.setPalette(palette)
        else:
            self.label_Status.setText('Status: UnConnected')
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor('red'))
            self.label_Status.setPalette(palette)
