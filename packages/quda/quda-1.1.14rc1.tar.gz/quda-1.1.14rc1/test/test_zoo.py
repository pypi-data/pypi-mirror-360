# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/8 14:29
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 
---------------------------------------------
"""
import time

import polars as pl
from quda.data.zoo import base
import ylog
import ygo

from quda.data.zoo.base import fac_components


# from quda.factor.core import FactorContext

def test_components():
    test_date = "2025-05-06"
    w = fac_components(index_code="000852").get_value(test_date)
    ylog.info(w)

def test_base_quote():
    test_date1 = "2025-05-06"
    test_date2 = "2025-07-04"
    data1 = base.fac_base_quote.get_value(test_date1)
    data2 = base.fac_base_quote(env="rt").get_value(test_date2)
    ylog.info(data1.head())
    ylog.info(data2.head())

def test_filter():
    test_date = "2025-05-06"
    data = base.fac_filter.get_value(test_date)
    ylog.info(data.filter(pl.col("cond") > 0))

def test_filter_notindex():
    test_date = "2025-05-06"
    data = base.fac_filter_notindex(index_codes=["000016", ]).get_value(test_date)
    ylog.info(data.filter(pl.col("cond").is_null()))



if __name__ == '__main__':
    # print(FactorContext.__dataclass_fields__.keys())
    # print(ygo.fn_info(ygo.delay(base.fac_prev_close.fn)(env="rt")))
    # test_base_quote()
    # test_filter()
    # test_components()
    test_filter_notindex()