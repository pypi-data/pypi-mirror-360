# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/7/4 10:38
Email: yundi.xxii@outlook.com
Description: 
---------------------------------------------
"""

from .core.store.database import (
    NAME,
    DB_PATH,
    CONFIG_PATH,
    get_settings,
    sql,
    put,
    has,
    tb_path,
    read_ck,
    read_mysql,
)
from .factor import Factor
from .core.qdf import from_polars

__version__ = "1.1.7"

def update():

    """
    通过全局配置文件中的`UPDATES`配置项来更新数据，需要遵循统一编写标准。每个数据源需要定义 `CONFIG` 字典和 `fetch_fn` 方法。

    添加新的更新任务步骤：

    - **Step 1**: 实现具体的数据更新逻辑

    创建一个新的 Python 文件（如：`my_project/data/update/update_news.py`），

    并在其中定义如下内容：

    >>> import quda
    >>>
    >>> CONFIG = {'news/tb1': 'SELECT * FROM source_table'}  # SQL 查询语句或其它来源标识
    >>>
    >>> def fetch_fn(tb_name, db_conf):
    ...     query = CONFIG.get(tb_name)
    ...     return quda.read_mysql(query, db_conf=db_conf)

    - **Step 2**: 在配置文件中添加配置

    在 {quda.DB_PATH}/conf/settings.toml 添加配置

    [UPDATES.news_data]

    mod = "my_project.data.update.update_news"

    update_time = "16:30"

    db_conf = "DATABASES.mysql"

    mode = "auto"

    beg_date = "2020-01-01"

    """

    from .core import updater
    import ygo
    import ylog

    update_settings = get_settings().get("UPDATES")
    if not update_settings:
        ylog.warning(f"Missing provider update configuration.")
        return
    for task, task_conf in update_settings.items():
        ylog.info(f"[{task} config]: {task_conf}")
        mod = ygo.module_from_str(task_conf["mod"])
        for tb_name in mod.CONFIG.keys():
            ygo.delay(updater.submit)(tb_name=tb_name,
                                      fetch_fn=ygo.delay(mod.fetch_fn)(db_conf=task_conf.get("db_conf")),
                                      **task_conf)()
    updater.do(debug_mode=True)


__all__ = [
    "NAME",
    "DB_PATH",
    "CONFIG_PATH",
    "get_settings",
    "sql",
    "put",
    "has",
    "tb_path",
    "read_ck",
    "read_mysql",
    "from_polars",
    "Factor",
]
