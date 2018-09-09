# -*- coding: utf-8 -*-
"""
Created at: 2018/6/21 15:21

@Author: Qian
"""

import psutil
from PyQt5 import QtWidgets, QtCore, QtGui

from .trade import *
from .helper import *
from .market import *

from my_modules.trader.Engine import Event
from my_modules.trader.Engine.eventType import *


#################################################
# 主窗口
class MainWindow(QtWidgets.QMainWindow):
    signalStatusBar = QtCore.pyqtSignal(type(Event()))

    # -------------------------------------------------
    def __init__(self, mainEngine, eventEngine):
        super(MainWindow, self).__init__()

        self.mainEngine = mainEngine
        self.eventEngine = eventEngine

        self.gatewayNameList = []
        self.widgetDict = {}
        self.appDetailList = []

        self.initUI()
        self.resize(1000, 600)
        self.loadWindowSetting('custom')

        # -------------------------------------------------
    def initUI(self):
        self.setWindowTitle('MyTrader')
        self.initCentral()
        self.initMenu()
        self.initStatusBar()

    # -------------------------------------------------
    def initCentral(self):
        widgetMarketW, dockMarketW = self.createDock(MarketWindow, u"Market", QtCore.Qt.RightDockWidgetArea)
        widgetOrderM, dockOrderM = self.createDock(OrderMonitor, u"Orders", QtCore.Qt.BottomDockWidgetArea)
        widgetPositionM, dockPositionM = self.createDock(PositionMonitor, u"Position", QtCore.Qt.BottomDockWidgetArea)
        widgetLogM, dockLogM = self.createDock(LogMonitor, u"Log", QtCore.Qt.BottomDockWidgetArea)
        widgetTradeW, dockTradeW = self.createDock(TradeWindow, u"Trade", QtCore.Qt.LeftDockWidgetArea)

        self.tabifyDockWidget(dockOrderM, dockPositionM)
        self.tabifyDockWidget(dockOrderM, dockLogM)

        self.resizeDocks([dockTradeW, dockMarketW], [200, 800], QtCore.Qt.Horizontal)
        self.resizeDocks([dockMarketW, dockOrderM], [350, 150], QtCore.Qt.Vertical)
        dockOrderM.raise_()

        widgetPositionM.itemDoubleClicked.connect(widgetTradeW.close_position)

        self.saveWindowSettings('default')

    # -------------------------------------------------
    def initMenu(self):
        menuBar = self.menuBar()

        gatewayMenu = menuBar.addMenu(u"Gateway")
        for gateway_name in self.mainEngine.tradeEngine.gatewayDict:
            gatewayMenu.addAction(self.createAction(gateway_name, lambda: self.setGateway(gateway_name)))

        dataAPIMenu = menuBar.addMenu(u"Data API")
        for dataApi_name in self.mainEngine.dataApiDict:
            dataAPIMenu.addAction(self.createAction(dataApi_name, lambda: self.setDataApi(dataApi_name)))

        helpMenu = menuBar.addMenu(u"help")
        helpMenu.addAction(self.createAction(u"About", self.openAbout))

    # -------------------------------------------------
    def initStatusBar(self):
        self.statusLabel = QtWidgets.QLabel()
        self.statusLabel.setAlignment(QtCore.Qt.AlignLeft)

        self.statusBar().addPermanentWidget(self.statusLabel)
        self.statusLabel.setText(self.getCpuMemory())

        self.sbCount = 0
        self.sbTrigger = 10
        self.signalStatusBar.connect(self.updateStatusBar)
        self.eventEngine.register(EVENT_TIMER, self.signalStatusBar.emit)

    # -------------------------------------------------
    def updateStatusBar(self):
        self.sbCount += 1

        if self.sbCount == self.sbTrigger:
            self.sbCount = 0
            self.statusLabel.setText(self.getCpuMemory())

    # -------------------------------------------------
    def getCpuMemory(self):
        cpuPercent = psutil.cpu_percent()
        memoryPercent = psutil.virtual_memory().percent
        return u"CPU utilization: {cpu}%    Memory utilization: {memory}%".format(cpu=cpuPercent, memory=memoryPercent)

    # -------------------------------------------------
    def addConnectAction(self):
        pass

    # -------------------------------------------------
    def createAction(self, actionName, function, iconPath=''):
        action = QtWidgets.QAction(actionName, self)
        action.triggered.connect(function)

        if iconPath:
            icon = QtGui.QIcon(iconPath)
            action.setIcon(icon)

        return action

    # -------------------------------------------------
    def createOpenAppFunction(self):
        pass

    # -------------------------------------------------
    def test(self):
        pass

    # -------------------------------------------------
    def openAbout(self):
        try:
            self.widgetDict['aboutW'].show()
        except KeyError:
            self.widgetDict['aboutW'] = AboutWidget(self)
            self.widgetDict['aboutW'].show()

    # -------------------------------------------------
    def setGateway(self, gateway_name):
        event = Event(EVENT_GATEWAY)
        event.dict_['gateway_name'] = gateway_name
        event.dict_['gateway_class'] = self.mainEngine.tradeEngine.gatewayDict.get(gateway_name)
        self.mainEngine.tradeEngine.put(event)

    # -------------------------------------------------
    def setDataApi(self, dataApi_name):
        event = Event(EVENT_DATAAPI)
        event.dict_['dataApi_name'] = dataApi_name
        event.dict_['dataApi_class'] = self.mainEngine.dataApiDict.get(dataApi_name)
        self.eventEngine.put(event)

    # -------------------------------------------------
    def openContract(self):
        pass

    # -------------------------------------------------
    def openSettingEditor(self):
        pass

    # -------------------------------------------------
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, "Exit", "Are you sure to exit?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            for widget in self.widgetDict.values():
                widget.close()
            self.saveWindowSettings('custom')

            self.mainEngine.exit()
            event.accept()
        else:
            event.ignore()

    # -------------------------------------------------
    def createDock(self, widgetClass, widgetName, widgetArea):
        widget = widgetClass(self.mainEngine, self.eventEngine)
        dock = QtWidgets.QDockWidget(widgetName)
        dock.setWidget(widget)
        dock.setObjectName(widgetName)
        dock.setFeatures(dock.DockWidgetFloatable | dock.DockWidgetMovable)
        self.addDockWidget(widgetArea, dock)
        return widget, dock

    # -------------------------------------------------
    def saveWindowSettings(self, settingName):
        setting = QtCore.QSettings("MyTrader", settingName)
        setting.setValue('state', self.saveState())
        setting.setValue('geometry', self.saveGeometry())

    # -------------------------------------------------
    def loadWindowSetting(self, settingName):
        setting = QtCore.QSettings('MyTrader', settingName)
        state = setting.value('state')
        geometry = setting.value('geometry')

        # 尚未初始化
        if state is None:
            return
        elif isinstance(state, QtCore.QVariant):
            self.restoreState(state.toByteArray())
            self.restoreGeometry(geometry.toByteArray())
        else:
            content = u'载入窗口配置异常，请检查'
            self.mainEngine.writeLog(content)

    # -------------------------------------------------
    def restoreWindow(self):
        self.loadWindowSetting('default')
        self.showMaximized()


#################################################
class AboutWidget(QtWidgets.QDialog):

    # -------------------------------------------------
    def __init__(self, parent=None):
        super(AboutWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('About MyTrader')
        text = u"""
            Developed by Q.
            
            """
        label = QtWidgets.QLabel()
        label.setText(text)
        label.setMinimumWidth(500)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(label)

        self.setLayout(vbox)


if __name__ == '__main__':
    pass
