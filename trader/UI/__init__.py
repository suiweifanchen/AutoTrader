# -*- coding: utf-8 -*-
"""
@author: Fanchen
@Created At: 2018/12/17 14:40
"""

import psutil
from PyQt5 import QtWidgets, QtGui, QtCore

from trader.Engine import Event, EVENT_TIMER,EVENT_TRADE,EVENT_LOG
from .trade import TraderWidget
from .helper import MarketMonitor, LogMonitor, OrderMonitor, PositionMonitor


class MainWindow(QtWidgets.QMainWindow):
    status_bar_signal = QtCore.pyqtSignal(Event)

    # -------------------------------------------------
    def __init__(self, main_engine):
        super(MainWindow, self).__init__()

        self.main_engine = main_engine
        self.gateway_list = self.main_engine.gateway_list  # 存放可用的gateway类
        self.quotation_list = self.main_engine.quotation_list  # 存放可用的quotation类

        self.init_ui()  # 初始化窗口
        self.resize(1000, 600)
        self.load_window_setting('custom')

        # 将事件注册到相应引擎中
        self.register_to_engine(EVENT_TIMER, self.main_engine.event_engine)
        self.trade_widget.register_to_engine(EVENT_TIMER, self.main_engine.event_engine)
        self.trade_widget.register_to_engine(EVENT_TRADE, self.main_engine.trade_engine)
        self.market_monitor.register_to_engine(EVENT_TIMER, self.main_engine.event_engine)
        self.order_monitor.register_to_engine(EVENT_TIMER, self.main_engine.event_engine)
        self.order_monitor.register_to_engine(EVENT_TRADE, self.main_engine.trade_engine)
        self.position_monitor.register_to_engine(EVENT_TIMER, self.main_engine.event_engine)
        self.position_monitor.register_to_engine(EVENT_TRADE, self.main_engine.trade_engine)
        self.log_monitor.register_to_engine(EVENT_LOG, self.main_engine.log_engine)
        # self.main_engine.write_log("Test the `LogEngine` and the `write_log()`")

    # -------------------------------------------------
    # 初始化UI界面
    def init_ui(self):
        self.setWindowTitle('My Trader')
        self.init_menu()  # 初始化菜单栏
        self.init_central()  # 初始化中央主界面
        self.init_status_bar()  # 初始化状态栏

    # -------------------------------------------------
    # 初始化菜单栏
    def init_menu(self):
        menu_bar = self.menuBar()

        gateway_menu = menu_bar.addMenu('Gateway')
        for gateway_ in self.gateway_list:
            gateway_menu.addAction(self.create_action(gateway_.name, self.change_api_func(gateway_, 0)))

        quotation_menu = menu_bar.addMenu('Quotation')
        for quotation_ in self.quotation_list:
            quotation_menu.addAction(self.create_action(quotation_.name, self.change_api_func(quotation_, 1)))

        help_menu = menu_bar.addMenu('Help')
        help_menu.addAction(self.create_action(u"About", self.open_about))

    # -------------------------------------------------
    # 创建菜单栏对应指令操作的动作
    def create_action(self, action_name, function, icon_path=''):
        action = QtWidgets.QAction(action_name, self)
        action.triggered.connect(function)

        if icon_path:
            icon = QtGui.QIcon(icon_path)
            action.setIcon(icon)

        return action

    # -------------------------------------------------
    # 更换gateway或者quotation，创建并返回对应的更换函数，而没有直接更换
    # api_用来传递相应类对象的，即直接将一个class传递过来；
    # api_type用来传递API类型的，0表示gateway，1表示quotation
    def change_api_func(self, api_, api_type):

        def set_api():
            if api_type == 0:
                self.main_engine.gateway = api_()  # 个人觉得此处需要一个进程锁，阻塞其它进程运行
                api = self.main_engine.gateway
            elif api_type == 1:
                self.main_engine.quotation = api_()
                api = self.main_engine.quotation
            else:
                return None

            api_widget = APIWidget(api, self)
            r = api_widget.exec_()
            if r:
                api.set_login_info(api_widget.login_info_dict)
                self.trade_widget.set_api_label(self.main_engine.get_api_status())  # 更新api的状态

        return  set_api

    # -------------------------------------------------
    def open_about(self):
        about_widget = AboutWidget()
        about_widget.exec_()

    # -------------------------------------------------
    def init_central(self):
        self.trade_widget, trade_dock = self.create_dock(TraderWidget, 'Trade', QtCore.Qt.LeftDockWidgetArea)
        self.market_monitor, market_dock = self.create_dock(MarketMonitor, 'Market', QtCore.Qt.RightDockWidgetArea)
        self.order_monitor, order_dock = self.create_dock(OrderMonitor, 'Order', QtCore.Qt.BottomDockWidgetArea)
        self.position_monitor, position_dock = self.create_dock(PositionMonitor, 'Position', QtCore.Qt.BottomDockWidgetArea)
        self.log_monitor, log_dock = self.create_dock(LogMonitor, 'Log', QtCore.Qt.BottomDockWidgetArea)

        self.tabifyDockWidget(order_dock, position_dock)
        self.tabifyDockWidget(order_dock, log_dock)
        order_dock.raise_()

        self.resizeDocks([trade_dock, market_dock], [200, 800], QtCore.Qt.Horizontal)
        self.resizeDocks([market_dock, order_dock], [350, 150], QtCore.Qt.Vertical)

        self.save_window_setting('default')

    # -------------------------------------------------
    # 用一个widget类创建一个实例和一个dock对象
    def create_dock(self, widget_, widget_name, widget_area):
        widget = widget_(self.main_engine, self)
        dock = QtWidgets.QDockWidget(widget_name)
        dock.setWidget(widget)
        dock.setObjectName(widget_name)
        dock.setFeatures(dock.DockWidgetFloatable | dock.DockWidgetMovable)
        self.addDockWidget(widget_area, dock)
        return widget, dock

    # -------------------------------------------------
    def init_status_bar(self):
        self.status_label = QtWidgets.QLabel()
        self.status_label.setAlignment(QtCore.Qt.AlignLeft)

        self.statusBar().addPermanentWidget(self.status_label)
        self.status_label.setText(self.get_cpu_memory())

        self.sb_count = 0
        self.sb_trigger = 10
        self.status_bar_signal.connect(self.update_status_bar)

    # -------------------------------------------------
    def update_status_bar(self):
        self.sb_count += 1

        if self.sb_count == self.sb_trigger:
            self.sb_count = 0
            self.status_label.setText(self.get_cpu_memory())

    # -------------------------------------------------
    def get_cpu_memory(self):
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        return u"CPU utilization:{cpu}%   Memory utilization:{memory}%".format(cpu=cpu_percent, memory=memory_percent)

    # -------------------------------------------------
    def register_to_engine(self, event_type, engine):
        engine.register(event_type, self.status_bar_signal.emit)

    # -------------------------------------------------
    # 保存窗口设置
    def save_window_setting(self, setting_name):
        setting = QtCore.QSettings("MyTrader", setting_name)
        setting.setValue('State', self.saveState())
        setting.setValue('Geometry', self.saveGeometry())

    # -------------------------------------------------
    # 载入窗口设置
    def load_window_setting(self, setting_name):
        setting = QtCore.QSettings("MyTrader", setting_name)
        state = setting.value('State')
        geometry = setting.value('Geometry')

        if state is None:  # 如果尚未初始化，则不操作
            return
        elif isinstance(state, QtCore.QByteArray):
            self.restoreState(state)
            self.restoreGeometry(geometry)
        else:
            content = u'载入窗口配置异常，请检查'
            self.mainEngine.writeLog(content)

    #----------------------------------------------------------------------
    # 还原默认窗口设置
    def restoreWindow(self):
        self.loadWindowSettings('default')

    # -------------------------------------------------
    def closeEvent(self, event, *args, **kwargs):
        reply = QtWidgets.QMessageBox.question(self, 'Exit', "Are you sure to exit?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.save_window_setting('custom')
            self.main_engine.exit()
            event.accept()
        else:
            event.ignore()


class APIWidget(QtWidgets.QDialog):

    # -------------------------------------------------
    def __init__(self, api, parent=None):
        super(APIWidget, self).__init__(parent)
        self.text_dict = {}  # 用于保存text对象，方便之后取出其中数据
        self.login_info_dict = {}  # 用于保存text中的信息
        self.init_ui(api)
        self.setMinimumSize(200, 150)

    # -------------------------------------------------
    def init_ui(self, api):
        self.setWindowTitle(api.name)
        grid = QtWidgets.QGridLayout()
        for i, key in enumerate(api.login_info.keys()):
            label = QtWidgets.QLabel(key)
            text = QtWidgets.QLineEdit(str(api.login_info[key]), self)
            # QLineEdit对象还可以设置显示方式、Validator和事件过滤器
            self.text_dict[key] = text
            grid.addWidget(label, i+1, 1, 1, 1)
            grid.addWidget(text, i+1, 2, 1, 2)

        button_ok = QtWidgets.QPushButton('Ok', self)
        button_ok.clicked.connect(self.ok)
        button_cancel = QtWidgets.QPushButton('Cancel', self)
        button_cancel.clicked.connect(self.cancel)
        grid.addWidget(button_ok, len(api.login_info.keys()), 2, 2, 1)
        grid.addWidget(button_cancel, len(api.login_info.keys()), 3, 2, 1)

        self.setLayout(grid)

    # -------------------------------------------------
    def ok(self):
        for key in self.text_dict:
            self.login_info_dict[key] = self.text_dict[key].text()
        self.done(1)

    # -------------------------------------------------
    def cancel(self):
        self.done(0)


class AboutWidget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(AboutWidget, self).__init__(parent)

        # 设置UI界面
        self.setWindowTitle("About My Trader")
        text = "\nDeveloped By Q.\n"
        label = QtWidgets.QLabel(text)
        label.setMinimumWidth(200)
        v_box = QtWidgets.QVBoxLayout()
        v_box.addWidget(label)
        self.setLayout(v_box)
