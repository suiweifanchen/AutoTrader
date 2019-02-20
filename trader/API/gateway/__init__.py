# -*- coding: utf-8 -*-
"""
@author: Fanchen
@Created At: 2018/12/17 14:42
"""

import os
import re
import json
import requests

from trader.exceptions import InitialException, ParamException, RequestException


class BaseGateway:
    name = "BaseGateway"
    login_info = {}

    def __init__(self):
        pass

    def buy(self):
        pass

    def sell(self):
        pass

    def cancel_order(self, order_id):
        pass

    def get_position(self):
        pass

    def check_api_status(self):
        return True

    def set_login_info(self, login_info_dict):
        pass


class XQ(BaseGateway):
    name = "XQ"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36",
        "Host": "xueqiu.com",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Referer": "https://xueqiu.com",
        "X-Requested-With": "XMLHttpRequest",
    }
    login_info = {}
    account = {
        "portfolio_code": "",
        "portfolio_market": "",
        "multiple": 100000,
        "position": {},
        "balance": 0.0,
        "net_value": 0.0,
    }
    __api = {"portfolio": "https://xueqiu.com/P/"}

    # -------------------------------------------------
    def __init__(self):
        super(XQ, self).__init__()
        self.load_config()
        self.__session = requests.Session()
        self.__session.headers.update(self.headers)
        self.__session.cookies.update(self.login_info['cookies'])

    # -------------------------------------------------
    # 检测连接状况
    def check_api_status(self):
        try:
            page = self.__session.get("https://xueqiu.com/")
            if page.text.__contains__('<div class="nav__user-info__main">'):
                return True
            else:
                return False
        except:
            return False

    # -------------------------------------------------
    # 更新投资组合
    def update_portfolio(self):
        url = self.__api['portfolio'] + self.login_info['portfolio_code']
        response = self.__session.get(url)
        match_info = re.search(r"(?<=SNB.cubeInfo = ).*(?=;\n)", response.text)

        try:
            portfolio_info = json.loads(match_info.group())
            info = portfolio_info.get("view_rebalancing")
            self.account["balance"] = info.get("cash", 0.0)
            self.account["net_value"] = portfolio_info.get("net_value", 0.0)
            for stock in info.get("holdings", []):
                stock_code = stock["stock_symbol"]
                self.account["position"][stock_code] = stock
        except AttributeError:
            # match_info 或 info 为 None
            raise ParamException("请求异常：投资组合信息更新失败，未找到相关信息")
        except:
            # json.loads()处解析错误
            raise ParamException("参数异常：组合信息解析错误")

    # -------------------------------------------------
    # 获取持仓信息
    def get_position(self):
        position_info = {}
        for stock_code in self.account["position"]:
            d = {}
            d['code'] = stock_code
            d['name'] = self.account["position"][stock_code].get("stock_name", "")
            d['direction'] = "Long"
            d['cost'] = ""
            d['volume'] = int(self.account["position"][stock_code].get("volume", 0) * self.account["multiple"])
            d['gateway'] = "XQ"
            position_info[stock_code] = d
        return position_info

    # -------------------------------------------------
    # 加载配置
    def load_config(self):
        file_path = os.path.join(os.path.curdir, "xq.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    dict_ = json.load(f)
            except:
                raise InitialException("XQ配置加载异常：配置文件`xq.json`加载错误")
        else:
            raise InitialException("XQ配置加载异常：配置文件`xq.json`未找到")

        self.login_info['cookies'] = self.parse_cookies_str(dict_.get('cookies', ""))
        self.login_info['portfolio_code'] = dict_.get('portfolio_code', "")
        self.login_info['portfolio_market'] = dict_.get('portfolio_market', "")
        self.account['multiple'] = dict_.get('multiple', 100000)
        self.account['portfolio_code'] = dict_.get('portfolio_code', "")
        self.account['portfolio_market'] = dict_.get('portfolio_market', "")

    # -------------------------------------------------
    # 设置并更新cookies
    def set_login_info(self, cookies):
        if isinstance(cookies, str):
            cookies = self.parse_cookies_str(cookies)
            self.login_info['cookies'] = cookies
        elif isinstance(cookies, dict):
            self.login_info['cookies'] = cookies
        else:
            raise ParamException("参数异常：cookies参数错误，应为字符串或字典类型")

        self.__session.cookies.update(self.login_info['cookies'])

    # -------------------------------------------------
    # 将 cookies字符串 解析成 cookies字典
    @staticmethod
    def parse_cookies_str(cookies):
        if cookies.startswith("Cookie:") or cookies.startswith("cookie:"):
            cookies = cookies[7:].strip()

        cookie_dict = {}
        for record in cookies.split(";"):
            key, value = record.strip().split("=", 1)
            cookie_dict[key] = value

        return cookie_dict


if __name__ == '__main__':
    x = XQ()
    cookies = ""
    x.set_login_info(cookies)
    print(x.check_api_status())
    x.update_portfolio()
    print(x.get_position())
