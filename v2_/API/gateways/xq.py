# -*- coding: utf-8 -*-
"""
Created at: 2018/7/10 17:41

@Author: Qian
"""

import requests

from .helper import BaseGateway


class XQ(BaseGateway):
    __headers = {
        'Host': "xueqiu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        'Accept-Language': "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        'Accept-Encoding': "gzip, deflate, br",
        'Upgrade-Insecure-Requests': "1",
        'Connection': "keep-alive",
        'Cache - Control': "max - age = 0",
    }

    # -------------------------------------------------
    def __init__(self, cookies, portfolio_code, portfolio_market):
        super(XQ, self).__init__()
        self.cookies = self.__parse_cookies(cookies)
        self.portfolio_code = portfolio_code
        self.portfolio_market = portfolio_market

        self.__session = requests.Session()
        self.__session.headers.update(self.__headers)
        self.__session.cookies.update(self.cookies)

    # -------------------------------------------------
    # covert cookies string to dict
    @staticmethod
    def __parse_cookies(string):
        cookies = {}

        if string.startswith("Cookie:"):
            string = string[7:]
        cookies_elements = [i.strip() for i in string.split(";")]
        for element in cookies_elements:
            key, value = element.strip().split("=", 1)
            cookies[key] = value

        return cookies

    # -------------------------------------------------
    def connect(self, cookies=None, portfolio_code=None, portfolio_market=None):
        if isinstance(cookies, str):
            self.cookies = self.__parse_cookies(cookies)
            self.__session.cookies.update(self.cookies)
        if portfolio_code:
            self.portfolio_code = portfolio_code
        if portfolio_market:
            self.portfolio_market = portfolio_market

        page = self.__session.get("https://xueqiu.com/")
        if page.text.__contains__('<div class="nav__user-info__main">'):
            return True
        else:
            return False

    # -------------------------------------------------
    def init_account(self):
        pass

    # -------------------------------------------------
    def buy(self, code, quantity):
        pass

    # -------------------------------------------------
    def sell(self, code, quantity):
        pass

    # -------------------------------------------------
    def __str__(self):
        return "XQ"
