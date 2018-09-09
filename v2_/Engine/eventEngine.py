# -*- coding: utf-8 -*-
"""
Created at: 2018/6/21 15:58

@Author: Qian
"""

from collections import defaultdict
from PyQt5 import QtCore
from queue import Queue, Empty
from threading import Thread

from .eventType import EVENT_TIMER


################################################
# 事件类
class Event:
    def __init__(self, type_=None):
        self.type_ = type_
        self.dict_ = {}


################################################
# 事件引擎
class EventEngine:

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
    def __onTimer(self):
        event = Event(type_=EVENT_TIMER)
        self.put(event)

    # -------------------------------------------------
    def start(self, timer=True):
        self.__active = True
        self.__thread.start()
        if timer:
            self.__timer.start(1000)

    # -------------------------------------------------
    def stop(self):
        self.__active = False
        self.__timer.stop()
        self.__thread.join()

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
    def put(self, event):
        self.__queue.put(event)

    # -------------------------------------------------
    def registerGeneralHandler(self, handler):
        if handler not in self.__generalHandlers:
            self.__generalHandlers.append(handler)

    # -------------------------------------------------
    def unregisterGeneralHandler(self, handler):
        if handler in self.__generalHandlers:
            self.__generalHandlers.remove(handler)
