# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/6/26 15:52
Email: yundi.xxii@outlook.com
Description: 应用层
---------------------------------------------
"""

def init_config():

    """初始化配置文件"""

    from pathlib import Path
    import shutil
    from importlib.resources import files
    import ylog

    source_conf_dir = files("quda.ml").joinpath("conf")
    # 当前工作目录下的 conf/
    target_conf_dir = Path.cwd() / "conf"
    if target_conf_dir.exists():
        ylog.warning(f"[QUDA-ML] - {target_conf_dir} already exists.")
    try:
        shutil.copytree(source_conf_dir, target_conf_dir)
        ylog.info(f"[QUDA-ML] - {target_conf_dir} created.")
    except Exception as e:
        ylog.error(f"[QUDA-ML] - Failed to create {target_conf_dir}\n{e}")

