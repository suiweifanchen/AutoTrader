# -*- coding: utf-8 -*-
"""
Created at: 2018/6/19 11:10

@Author: Qian
"""

import requests


class RequestError(Exception):
    """
    Web Request Error: It may occur when:
        1. your computer could not connect to internet;
        2. your request date is wrong;
    """


class XueQiu:
    url = "https://xueqiu.com/"
    search_stock_url = "https://xueqiu.com/stock/p/search.json"
    headers = {
        'Host': "xueqiu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        'Accept-Language': "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        'Accept-Encoding': "gzip, deflate, br",
        'Connection': "keep-alive",
        'Upgrade-Insecure-Requests': "1",
        'Cache-Control': "max-age=0",
    }

    # -------------------------------------------------
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update(self.headers)
        self.is_connected = False  # 会话未建立
        self.account_config = {'portfolio_market': 'cn'}

    # -------------------------------------------------
    def _set_cookies(self, cookies_string):
        cookies = self._parse_cookies(cookies_string)
        self.s.cookies.update(cookies)

    # -------------------------------------------------
    # parse the cookies string, copied from web explorer, to a dict
    @staticmethod
    def _parse_cookies(cookies_string):
        """
        Parse the cookies string, copied from web explorer, to a dict.
        :param cookies_string: the cookies string is like "Cookie: u.sig=RKDDYcVaYt0JJKDbpYPvXNwQhXE; snbim_minify=true"
        :return: {'u.sig': 'RKDDYcVaYt0JJKDbpYPvXNwQhXE', 'snbim_minify': 'true', }
        """

        cookies = {}

        if cookies_string.startswith("Cookie:"):
            cookies_string = cookies_string[7:]
        cookies_elements = [i.strip() for i in cookies_string.split(";")]
        for element in cookies_elements:
            key, value = element.split("=", 1)
            cookies[key] = value

        return cookies

    # -------------------------------------------------
    # start the session and connect to "https://xueqiu.com/"
    def session_start(self, cookies_string, max_req_num=3):
        if not self.s.cookies:
            self._set_cookies(cookies_string)
        flag = 0
        while True:
            r = self.s.get(self.url)
            if r.status_code == 200:
                self.is_connected = True
                return 1
            elif flag == max_req_num - 1:
                self.is_connected = False
                raise RequestError("Can Not Connect To `https://xueqiu.com/` : check the network and the request data")
            else:
                flag += 1

    # -------------------------------------------------
    def _search_stock_info(self, code):
        data = {
            'code': str(code),
            'size': '300',
            'key': '47bce5c74f',
            'market': self.account_config['portfolio_market'],
        }
        pass

    # -------------------------------------------------
    def buy(self):
        pass

    # -------------------------------------------------
    def sell(self):
        pass

    # -------------------------------------------------
    def close_position(self):
        pass

    # -------------------------------------------------
    def position(self):
        pass

    # -------------------------------------------------
    def balance(self):
        pass

    # -------------------------------------------------
    def account(self):
        pass


if __name__ == '__main__':
    pass
