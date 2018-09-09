# -*- coding: utf-8 -*-
"""
Created at: 18-4-9 上午3:53

@Author: Qian
"""

import re
import requests
from multiprocessing.pool import ThreadPool


#################################################
# 新浪行情获取类
class SinaQuotation:
    max_num = 800
    stock_api = "http://hq.sinajs.cn/?format=text&list="
    grep_detail = re.compile(r'(\d+)=([^\s][^,]+?)%s%s' % (r',([\.\d]+)' * 29, r',([-\.\d:]+)' * 2))
    grep_detail_with_prefix = re.compile(r'(\w{2}\d+)=([^\s][^,]+?)%s%s' % (r',([\.\d]+)' * 29, r',([-\.\d:]+)' * 2))

    # -------------------------------------------------
    def __init__(self):
        self._session = requests.session()
        stock_codes = self.load_stock_codes()
        self.stock_list = self.gen_stock_list(stock_codes)

    # -------------------------------------------------
    def load_stock_codes(self):
        # just a test
        return ['sh000001', '399001', '399005', '399006', '399300', 'sz000001', ]

    # -------------------------------------------------
    # return specific stocks real quotation
    def stocks(self, stock_codes, prefix=False):
        if type(stock_codes) is not list:
            stock_codes = [stock_codes]

        stock_list = self.gen_stock_list(stock_codes)
        return self.get_stock_data(stock_list, prefix=prefix)

    # -------------------------------------------------
    # return all market quotation snapshot
    def market_snapshot(self, prefix=True):
        return self.get_stock_data(self.stock_list, prefix=prefix)

    # -------------------------------------------------
    def gen_stock_list(self, stock_codes):
        stock_with_exchange_list = self._gen_stock_prefix(stock_codes)

        if self.max_num > len(stock_with_exchange_list):
            request_list = ','.join(stock_with_exchange_list)
            return [request_list]

        stock_list = []
        request_num = len(stock_codes) // self.max_num + 1
        for range_start in range(request_num):
            num_start = self.max_num * range_start
            num_end = self.max_num * (range_start + 1)
            request_list = ','.join(stock_with_exchange_list[num_start:num_end])
            stock_list.append(request_list)
        return stock_list

    # -------------------------------------------------
    def _gen_stock_prefix(self, stock_codes):
        return [self.get_stock_type(code) + code[-6:] for code in stock_codes]

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
        if stock_code.startswith(('50', '51', '60', '90', '110', '113', '132', '204')):
            return 'sh'
        if stock_code.startswith(('00', '13', '18', '15', '16', '18', '20', '30', '39', '115', '1318')):
            return 'sz'
        if stock_code.startswith(('5', '6', '9', '7')):
            return 'sh'
        return 'sz'

    # -------------------------------------------------
    def get_stocks_by_range(self, params):
        headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36',
        }
        r = self._session.get(self.stock_api+params, headers=headers)
        return r.text

    # -------------------------------------------------
    def get_stock_data(self, stock_list, **kwargs):
        pool = ThreadPool(len(stock_list))
        try:
            result = pool.map(self.get_stocks_by_range, stock_list)
        finally:
            pool.close()
        return self.format_response_data([x for x in result if x is not None], **kwargs)

    # -------------------------------------------------
    def format_response_data(self, response_data, prefix=False):
        stocks_detail = ''.join(response_data)
        grep_str = self.grep_detail_with_prefix if prefix else self.grep_detail
        result = grep_str.finditer(stocks_detail)
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
