# -*- coding: utf-8 -*-
"""
@author: Fanchen
@Created At: 2018/12/17 14:43
"""

import os
import re
import json
import requests
from multiprocessing.pool import ThreadPool

from trader.exceptions import ParamException


class BaseQuotation:
    name = "BaseQuotation"
    headers = {}
    login_info = {}

    def __init__(self):
        self.stock_list = []
        pass

    def load_stock_list(self):
        pass

    def save_stock_list(self):
        pass

    def add_stock(self, stock_code):
        pass

    def delete_stock(self, stock_code):
        pass

    def get_market_data(self, stock_list):
        pass

    def set_login_info(self, login_info_dict):
        pass


#################################################
# 新浪行情获取
class Sina(BaseQuotation):
    name = "SinaQuotation"

    max_num = 800  # 一次最多查询800个股票
    stock_api = "http://hq.sinajs.cn/?format=text&list="
    grep_detail = re.compile(r'(\w{2}\d+)=([^\s][^,]+?)%s%s' % (r',([\.\d]+)' * 29, r',([-\.\d:]+)' * 2))
    headers = {
        'Accept-Encoding': 'gzip, deflate, sdch',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36',
    }

    # -------------------------------------------------
    def __init__(self):
        super(Sina, self).__init__()
        self.__session = requests.Session()
        self.__session.headers.update(self.headers)
        self.load_stock_list()

    # -------------------------------------------------
    # 加载股票代码列表
    def load_stock_list(self):
        file_path = os.path.join(os.path.curdir, "stock_list.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                dict_ = json.load(f)
            self.stock_list = self.gen_standard_stock_list(dict_["stock_list"])

    # -------------------------------------------------
    # 保存股票代码列表
    def save_stock_list(self):
        file_path = os.path.join(os.path.curdir, "stock_list.json")
        if os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump({"stock_list": self.stock_list}, f)

    # -------------------------------------------------
    # 向stock_list中添加股票
    def add_stock(self, stock_code):
        if isinstance(stock_code, list):
            self.stock_list.extend(self.gen_standard_stock_list(stock_code))
        elif isinstance(stock_code, str):
            self.stock_list.extend(self.gen_standard_stock_list([stock_code, ]))
        else:
            raise ParamException("参数错误：`stock_code`参数形式错误，应形如 ['000001', ] 或 '000001' ")

    # -------------------------------------------------
    # 在stock_list中删除股票
    def delete_stock(self, stock_code):
        if isinstance(stock_code, list):
            stock_code = self.gen_standard_stock_list(stock_code)
        elif isinstance(stock_code, str):
            stock_code = self.gen_standard_stock_list([stock_code, ])
        else:
            return None

        for i in stock_code:
            if i in self.stock_list:
                self.stock_list.remove(i)

    # -------------------------------------------------
    # 将所有股票代码转换成标准形式，即如 'sz000001'
    def gen_standard_stock_list(self, stock_list):
        return [self.get_stock_type(i) + i[-6:] for i in stock_list]

    # -------------------------------------------------
    # 获取指定股票行情
    def get_market_data(self, stock_list=None):
        # 准备参数
        if not stock_list:
            stock_list = self.stock_list
        param_list = self.__gen_param(stock_list)

        pool = ThreadPool(len(param_list))
        try:
            result = pool.map(self.__request_market_data, param_list)
        finally:
            pool.close()

        return self.__parse([i for i in result if i is not None])

    # -------------------------------------------------
    # 通过api请求行情数据
    def __request_market_data(self, param):
        r = self.__session.get(self.stock_api + param)
        return r.text

    # -------------------------------------------------
    # 解析返回的结果
    def __parse(self, response_list):
        stocks_data = ''.join(response_list)
        grep_str = self.grep_detail
        result = grep_str.finditer(stocks_data)
        stock_dict = {}
        for stock_match_object in result:
            stock = stock_match_object.groups()
            stock_dict[stock[0]] = dict(
                name=stock[1],
                code=stock[0],
                open=float(stock[2]),
                close=float(stock[3]),
                now=float(stock[4]),
                high=float(stock[5]),
                low=float(stock[6]),
                buy=float(stock[7]),
                sell=float(stock[8]),
                turnover=int(stock[9]),
                volume=float(stock[10]),
                bid1_volume=int(stock[11]),
                bid1=float(stock[12]),
                bid2_volume=int(stock[13]),
                bid2=float(stock[14]),
                bid3_volume=int(stock[15]),
                bid3=float(stock[16]),
                bid4_volume=int(stock[17]),
                bid4=float(stock[18]),
                bid5_volume=int(stock[19]),
                bid5=float(stock[20]),
                ask1_volume=int(stock[21]),
                ask1=float(stock[22]),
                ask2_volume=int(stock[23]),
                ask2=float(stock[24]),
                ask3_volume=int(stock[25]),
                ask3=float(stock[26]),
                ask4_volume=int(stock[27]),
                ask4=float(stock[28]),
                ask5_volume=int(stock[29]),
                ask5=float(stock[30]),
                date=stock[31],
                time=stock[32],
            )
        return stock_dict

    # -------------------------------------------------
    # 用于生成请求所需的参数
    def __gen_param(self, stock_list):
        if self.max_num >= len(stock_list):
            param = ','.join(stock_list)
            return [param, ]
        else:
            param_list = []
            request_num = len(stock_list) // self.max_num + 1
            for i in range(request_num):
                num_start = self.max_num * i
                num_end = self.max_num * (i + 1)
                param = ','.join(stock_list[num_start:num_end])
                param_list.append(param)
            return param_list

    # -------------------------------------------------
    @staticmethod
    def get_stock_type(stock_code):
        """
        判断股票ID对应的证券市场
        匹配规则
        ['50', '51', '60', '90', '110'] 为 sh
        ['00', '13', '18', '15', '16', '18', '20', '30', '39', '115'] 为 sz
        ['5', '6', '9'] 开头的为 sh， 其余为 sz
        :param stock_code:股票ID, 若以 'sz', 'sh' 开头直接返回对应类型，否则使用内置规则判断
        :return 'sh' or 'sz'
        """

        assert type(stock_code) is str, 'stock code need str type'
        if stock_code.startswith(('sh', 'sz')):
            return stock_code[:2]
        elif stock_code.startswith(('50', '51', '60', '90', '110', '113', '132', '204')):
            return 'sh'
        elif stock_code.startswith(('00', '13', '18', '15', '16', '18', '20', '30', '39', '115', '1318')):
            return 'sz'
        elif stock_code.startswith(('5', '6', '9', '7')):
            return 'sh'
        return 'sz'


if __name__ == '__main__':
    # 测试
    s = Sina()
    s.load_stock_list()
    r = s.get_market_data()
    s.add_stock('000002')
    s.add_stock('sh600002')
    s.delete_stock('000001')
    s.delete_stock('600001')
    s.save_stock_list()
    pass
