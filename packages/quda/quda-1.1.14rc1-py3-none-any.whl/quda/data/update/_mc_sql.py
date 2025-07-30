# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/29 18:10
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

def sql_StockKlineDay(date, tb_name):
    return f"""
    select date,
           replaceRegexpAll(order_book_id, '[^0-9]', '')                          as asset,
           total_turnover                                                         as amount,
           volume,
           prev_close,
           open,
           high,
           low,
           close,
           limit_up,
           limit_down,
           if(num_trades < 0, 0, if(num_trades > toInt64(volume), 0, num_trades)) as num_trades
    from {tb_name}
        prewhere date = '{date}'
    order by asset
    """


def sql_StockKlineMinute(date, tb_name):
    return f"""
    select EventDate                                                              as date,
           replaceRegexpAll(order_book_id, '[^0-9]', '')                          as asset,
           formatDateTime(datetime, '%T')                                         as time,
           total_turnover                                                         as amount,
           volume,
           open,
           high,
           low,
           close,
           if(num_trades < 0, 0, if(num_trades > toInt64(volume), 0, num_trades)) as num_trades
    from {tb_name}
        prewhere EventDate = '{date}'
    order by asset
    """


def sql_IndexKlineMinute(date, tb_name):
    return f"""
    select EventDate                                     as date,
           replaceRegexpAll(order_book_id, '[^0-9]', '') as asset,
           formatDateTime(datetime, '%T')                as time,
           total_turnover                                as amount,
           volume,
           open,
           high,
           low,
           close
    from {tb_name}
        prewhere EventDate = '{date}'
    order by asset
    """


def sql_IndexKlineDay(date, tb_name):
    return f"""
    select date,
           replaceRegexpAll(order_book_id, '[^0-9]', '') as asset,
           total_turnover                                as amount,
           volume,
           prev_close,
           open,
           high,
           low,
           close
    from {tb_name}
        prewhere date = '{date}'
    order by asset
    """