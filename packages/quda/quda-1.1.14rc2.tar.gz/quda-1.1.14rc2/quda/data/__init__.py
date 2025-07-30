# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/5 16:56
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

from .api import (
    get_industry,
    get_liststatus,
    get_shares,
    get_st,
    get_secumain,
    get_codes,
)
from .tables import (
    TB_STOCK_KLINE_DAY,
    TB_STOCK_KLINE_MINUTE,
    TB_INDEX_KLINE_DAY,
    TB_INDEX_KLINE_MINUTE,
)

def init():
    from ..core.store import database
    import ylog
    import toml
    settings = database.get_settings()
    if (not settings.get("UPDATES.jydata")) or (not settings.get("UPDATES.mc")):
        ylog.warning(f"[provider]missing jydata/mc configuration. writing update config to {database.CONFIG_PATH}")
        update_conf = {
            "updates": {
                "jydata": {
                    "mod": "quda.data.update.update_jydata",
                    "update_time": "16:30",
                    "db_conf": "DATABASES.jy",
                    "mode": "auto",
                },
                "mc": {
                    "mod": "quda.data.update.update_mc",
                    "update_time": "22:00",
                    "db_conf": "DATABASES.ck",
                    "mode": "auto",
                    "beg_date": "2020-01-01",
                }
            }
        }
        settings.update(update_conf)
        with open(database.CONFIG_PATH, 'w') as f:
            toml.dump(settings.as_dict(), f)
            ylog.info("[provider]init success.")


__version__ = "0.1.1b1"

__all__ = [
    "get_st",
    "get_industry",
    "get_liststatus",
    "get_shares",
    "get_secumain",
    "get_codes",
    "TB_STOCK_KLINE_MINUTE",
    "TB_INDEX_KLINE_DAY",
    "TB_STOCK_KLINE_DAY",
    "TB_INDEX_KLINE_MINUTE",
]
