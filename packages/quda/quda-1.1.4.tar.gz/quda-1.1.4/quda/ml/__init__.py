# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/6/25 10:20
Email: yundi.xxii@outlook.com
Description: 
---------------------------------------------
"""

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .data import DataLoader
    from .workflow import WorkFlow
else:
    import ygo
    DataLoader = ygo.lazy_import("quda.ml.data.DataLoader")
    WorkFlow = ygo.lazy_import("quda.ml.workflow.WorkFlow")

__version__ = "0.2.16"

__all__ = [
    "WorkFlow",
    "DataLoader",
]

