# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License.
Created on 2025/6/25 15:05
Email: yundi.xxii@outlook.com
Description:
---------------------------------------------
"""

from collections.abc import Sequence
from typing import Literal
import numpy as np
import ylog
import polars as pl

def get_timedelta_names(columns: Sequence[str], ) -> list[str]:
    """
    Return a list of column names that can be successfully parsed into <pandas>.Timedelta object.

    Parameters
    ----------
    columns: Sequence[str]
        A Sequence of strings representing column names to be evaluated for Timedelta

    Returns
    -------
    list[str]

    Examples
    --------
    >>> get_timedelta_names(['1s', '2min', 'invalid', '3H'])
    ['1s', '2min', '3H']

    """
    from pandas import Timedelta
    def _is_valid_timedelta(s: str) -> bool:
        try:
            Timedelta(s)
            return True
        except ValueError:
            return False

    return [col for col in columns if _is_valid_timedelta(col)]


def extract_feature_names(columns: Sequence[str], ) -> list[str]:
    """
    Extract a list of valid feature column names by excluding index-like(date/time/asset)、price-like(price)、time-like columns.
    Parameters
    ----------
    columns: Sequence[str]
        A sequence of strings representing all available column names.

    Returns
    -------
    list[str]

    Examples
    --------
    >>> extract_feature_names(['date', 'time', 'asset', 'open', 'high', '1s', 'volume', 'price'])
    ['open', 'high', 'volume']

    """
    return_cols = get_timedelta_names(columns)
    exclude = {"date", "time", "asset", 'price', *return_cols}
    return [col for col in columns if col not in exclude]

def preprocess_features(df: pl.DataFrame,
                        target_col: str,
                        missing_threshold: float = 0.95,
                        standardize: bool = True,
                        var_threshold: float = 0.01,
                        index: tuple[str] = ("date", "time", "asset")) -> pl.DataFrame:
    """
    预处理阶段: 去除缺失值过高和低方差/常量特征
    Parameters
    ----------
    df: pl.DataFrame
        输入数据
    target_col: str
        目标列名称
    var_threshold: float
        方差阈值，低于此值的特征将被删除
    missing_threshold: float
        缺失值比例阈值，高于此值的特征将被删除
    standardize: bool
        是否对特征进行标准化(z-score)
    index: tuple[str]
        索引列, 预处理步骤会跳过这些列

    Returns
    -------
    df_cleaned: pl.DataFrame
        清洗后的DataFrame
    """
    ylog.info("Preprocessing...")
    df = df.fill_nan(None)
    skip_cols = set(index)
    if target_col:
        skip_cols.add(target_col)
    features = [col for col in df.columns if col not in skip_cols]

    def filter_cols(data):
        """
        删除常量列
        """
        return (
            data[0]
            .transpose(include_header=True,
                       column_names=["cond"],
                       header_name="feat_name")
            .filter(pl.col("cond"))
            .drop_nulls("cond")
            ["feat_name"].to_list()
        )

    # 删除常量列
    feat_consts = df[features].select(pl.col(c).drop_nulls().n_unique() for c in features)
    not_const_exprs = filter_cols(feat_consts > 1)

    # 处理 inf
    df = (
        df
        .with_columns(pl.col(c)
                      .cast(pl.Float32)
                      .replace([np.inf, -np.inf], None) for c in not_const_exprs
                      )
    )
    # 删除缺失值比例过高的列
    feat_null_ratio = df[not_const_exprs].null_count() / df.height
    valid_exprs = filter_cols(feat_null_ratio <= missing_threshold)
    # 标准化(可选)
    if standardize:
        df = (
            df
            .select(
                *skip_cols,
                *[(pl.col(c) - pl.col(c).mean()) / pl.col(c).std() for c in valid_exprs],
            )
        )
    # 删除常量或低方差特征
    # 计算各列方差
    if standardize:
        feat_var = df[valid_exprs].select(pl.all().var())
        high_var_exprs = filter_cols(feat_var > var_threshold)
        return df.select(*index, *high_var_exprs, target_col)
    return df.select(*index, *valid_exprs, target_col)

def fast_rfe(df,
             target_col: str,
             tail_label: tuple[float] = (5, 95),
             index: tuple[str] = ("date", "time", "asset"),
             missing_threshold: float = 0.4,
             standardize: bool = True,
             var_threshold: float = 0.01,
             fill_null_strategy: Literal[
                                     "forward", "backward", "mean", "zero", "max", "min", "one"] | None = "forward"):
    """特征筛选"""
    from lightgbm import LGBMRegressor
    if hasattr(df, "__call__"):
        df = df()
    if isinstance(df, pl.LazyFrame):
        df = df.collect()
    # 预处理
    df = preprocess_features(df,
                             target_col=target_col,
                             index=index,
                             missing_threshold=missing_threshold,
                             standardize=standardize,
                             var_threshold=var_threshold,
                             )
    # 处理空值
    skip_cols = set(index) if index else set()
    skip_cols.add(target_col)
    feat_names = [feat for feat in df.columns if feat not in skip_cols]
    fill_null_over_spec = {"partition_by": "asset", "order_by": ["date", "time"]}
    df = (
        df
        .with_columns(pl.col(c)
                      .fill_null(strategy=fill_null_strategy)
                      .over(**fill_null_over_spec)
                      for c in feat_names)
        .with_columns(pl.col(target_col)
                      .fill_null(strategy=fill_null_strategy)
                      .over(**fill_null_over_spec))
        .drop_nulls()
    )

    X = df[feat_names].to_numpy()
    y = df[target_col].to_numpy().ravel()

    # 根据label来减少样本数量
    q_low, q_high = np.percentile(y, tail_label)
    mask = (y < q_low) | (y > q_high)
    X = X[mask]
    y = y[mask]

    ylog.info("Running Fast-RFE...")
    model = LGBMRegressor(n_estimators=100, random_state=42, )
    model.fit(X, y, )
    importance = model.feature_importances_
    # 排序并且提出最不重要的前k个特征
    sorted_feats = sorted(zip(feat_names, importance), key=lambda x: x[1], reverse=True)
    selected_feats = [f for f, s in sorted_feats if s > 0]
    # todo: 相关性 > 0.9 的特征保留重要性大的
    # corr_df = df[selected_feats].corr()
    # for feat in selected_feats:
    return selected_feats


def is_notebook():
    import sys
    return "ipykernel" in sys.modules

def hydra_wrapper(config_path, config_name):
    """将 hydra.main 装饰器转为方法调用"""
    import os
    from hydra import main
    abs_config_path = os.path.abspath(config_path)
    if not os.path.exists(abs_config_path):
        ylog.error(f"Miss {abs_config_path}")
        return
    return main(version_base=None, config_path=abs_config_path, config_name=config_name)