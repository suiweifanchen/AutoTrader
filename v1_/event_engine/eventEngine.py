# -*- coding: utf-8 -*-
"""
Created at: 18-4-8 上午7:08

@Author: Qian
"""

from time import sleep
from threading import Thread
from queue import Queue, Empty
from collections import defaultdict
from PyQt5 import QtCore

from .eventType import *


#################################################
# 事件对象
class Event:
    """事件对象"""

    # -------------------------------------------------
    def __init__(self, type_=None):
        self.type_ = type_
        self.dict_ = {}


#################################################
# 事件引擎
class EventEngine:
    """计时器使用PyQt的QTimer的计时器"""

    # -------------------------------------------------
    def __init__(self):
        self.__queue = Queue()

        self.__active = False

        self.__thread = Thread(target=self.__run)

        self.__timer = QtCore.QTimer()
        self.__timer.timeout.connect(self.__onTimer)

        self.__handlers = defaultdict(list)
        self.__generalHandlers = []

    # -------------------------------------------------
    def __onTimer(self):
        event = Event(type_=EVENT_TIMER)
        self.put(event)

    # -------------------------------------------------
    def __run(self):
        while self.__active:
            try:
                event = self.__queue.get(block=True, timeout=1)
                self.__process(event)
            except Empty:
                pass

    # -------------------------------------------------
    def __process(self, event):
        if event.type_ in self.__handlers:
            [handler(event) for handler in self.__handlers[event.type_]]
        if self.__generalHandlers:
            [handler(event) for handler in self.__generalHandlers]

    # -------------------------------------------------
    def start(self, timer=True):
        self.__active = True
        self.__thread.start()
        if timer:
            self.__timer.start(1000)

    # -------------------------------------------------
    def restart(self, timer=True):
        # 已关闭的线程不能在start(), 需要重建新线程
        if not self.__thread.is_alive():
            self.__thread = Thread(target=self.__run)
            self.__timer = QtCore.QTimer()
            self.__timer.timeout.connect(self.__onTimer)

            self.start(timer=timer)

    # -------------------------------------------------
    def stop(self):
        self.__active = False
        self.__timer.stop()
        self.__thread.join()

    # -------------------------------------------------
    def put(self, event):
        self.__queue.put(event)

    # -------------------------------------------------
    def register(self, type_, handler):
        handlerList = self.__handlers[type_]
        if handler not in handlerList:
            handlerList.append(handler)

    # -------------------------------------------------
    def unregister(self, type_, handler):
        handlerList = self.__handlers[type_]
        if handler in handlerList:
            handlerList.remove(handler)
        if not handlerList:
            del self.__handlers[type_]

    # -------------------------------------------------
    def registerGeneralHandlers(self, handler):
        if handler not in self.__generalHandlers:
            self.__generalHandlers.append(handler)

    # -------------------------------------------------
    def unregisterGeneralHandlers(self, handler):
        if handler in self.__generalHandlers:
            self.__generalHandlers.remove(handler)


class EventEngine2:
    """计时器使用python线程的事件驱动引擎"""

    # -------------------------------------------------
    def __init__(self):
        # 事件队列
        self.__queue = Queue()

        # 事件引擎开关
        self.__active = False

        # 事件处理线程
        self.__thread = Thread(target=self.__run)

        # 计时器，用于触发计时器事件
        self.__timer = Thread(target=self.__runTimer)
        # 计时器开关
        self.__timerActive = False
        # 计时器触发间隔（默认1秒）
        self.__timerSleep = 1

        # 这里的__handlers是一个字典，用来保存对应的事件调用关系
        # 其中每个键对应的值是一个列表，列表中保存了对该事件进行监听的函数功能
        self.__handlers = defaultdict(list)
        # __generalHandlers是一个列表，用来保存通用回调函数（所有事件均调用）
        self.__generalHandlers = []

    # -------------------------------------------------
    # 引擎运行
    def __run(self):
        while self.__active:
            try:
                event = self.__queue.get(block=True, timeout=1)  # 获取事件的阻塞时间设为1秒
                self.__process(event)
            except Empty:
                pass

    # -------------------------------------------------
    # 处理事件
    def __process(self, event):
        # 检查是否存在对该事件进行监听的处理函数
        if event.type_ in self.__handlers:
            # 若存在，则按顺序将事件传递给处理函数执行
            [handler(event) for handler in self.__handlers[event.type_]]

        # 调用通用处理函数进行处理
        if self.__generalHandlers:
            [handler(event) for handler in self.__generalHandlers]

    # -------------------------------------------------
    # 运行在计时器线程中的循环函数
    def __runTimer(self):
        while self.__timerActive:
            # 创建计时器事件
            event = Event(type_=EVENT_TIMER)
            self.put(event)
            sleep(self.__timerSleep)

    # -------------------------------------------------
    # 引擎启动, timer：是否要启动计时器
    def start(self, timer=True):
        # 将引擎开关设置为启动
        self.__active = True
        # 启动时间处理线程
        self.__thread.start()

        # 启动计时器,计时器事件间隔默认设定为1秒
        if timer:
            self.__timerActive = True
            self.__timer.start()

    # -------------------------------------------------
    # 引擎停止
    def stop(self):
        # 将引擎开关设置为停止
        self.__active = False

        # 停止计时器
        self.__timerActive = False
        self.__timer.join()

        # 等待事件处理线程退出
        self.__thread.join()

    # -------------------------------------------------
    # 注册事件处理函数监听
    def register(self, type_, handler):
        # 尝试获取该事件类型对应的处理函数列表，若无defaultDict会自动创建新的list
        handlerList = self.__handlers[type_]

        if handler not in handlerList:
            handlerList.append(handler)

    # -------------------------------------------------
    # 注销事件处理函数监听
    def unregister(self, type_, handler):
        # 尝试获取该事件类型对应的处理函数列表，若无则忽略该次注销请求
        handlerList = self.__handlers[type_]

        # 如果该函数存在于列表中，则移除
        if handler in handlerList:
            handlerList.remove(handler)

        # 如果函数列表为空，则从引擎中移除该事件类型
        if not handlerList:
            del self.__handlers[type_]

    # -------------------------------------------------
    # 向事件队列中存入时间
    def put(self, event):
        self.__queue.put(event)

    # -------------------------------------------------
    # 注册通用事件处理函数监听
    def registerGeneralHandler(self, handler):
        if handler not in self.__generalHandlers:
            self.__generalHandlers.append(handler)

    # -------------------------------------------------
    # 注册通用事件处理函数监听
    def unregisterGeneralHandler(self, handler):
        if handler in self.__generalHandlers:
            self.__generalHandlers.remove(handler)
