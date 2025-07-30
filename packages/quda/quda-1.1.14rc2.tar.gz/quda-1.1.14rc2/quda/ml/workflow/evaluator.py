# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/7/2 14:46
Email: yundi.xxii@outlook.com
Description: 
---------------------------------------------
"""

from typing import Sequence, TYPE_CHECKING

import mlflow
import ylog

from ..utils import extract_feature_names, get_timedelta_names
from sklearn.model_selection import train_test_split

if TYPE_CHECKING:
    from .workflow import WorkFlow
    from ..data import DataLoader


def train(workflow: 'WorkFlow',
          iterables: Sequence,
          batch_size: int = -1,
          features: list[str] | None = None,
          valid_size: float = 0.2,
          shuffle: bool = False,
          random_state: int = 42, ):
    """
    通用增量训练流程，支持分批加载数据,预处理，模型训练与保存

    Parameters
    ----------
    workflow: 'WorkFlow'
    iterables: Sequence
        可迭代对象
    batch_size: int
        每次训练的批次，默认 -1: 全量训练
    features: list[str]|None
        特征名, 默认None。会排除date,time,asset,price,以timedelta命名的收益列
    valid_size: float
        验证集比例，默认0.2
    shuffle: bool
        是否打乱 iterables, 默认 False
    random_state: int
        随机数种子，默认 42

    Returns
    -------

    """
    batch_size = batch_size if batch_size > 0 else len(iterables)
    iterables = sorted(iterables)

    mlflow.autolog()
    mlflow.sklearn.autolog(disable=True)

    with mlflow.start_run() as top_run:
        top_run_id = top_run.info.run_id
        ylog.info(f"Started mlflow.run: {top_run_id}")
        params = {
            "data.beg": iterables[0],
            "data.end": iterables[-1],
            "batch_size": batch_size,
            "shuffle": shuffle,
            "random_state": random_state,
        }
        mlflow.log_params(params, run_id=top_run_id)
        train_batch_list = [iterables[i:i + batch_size] for i in range(0, len(iterables), batch_size)]
        for i, train_batch in enumerate(train_batch_list):
            beg, end = train_batch[0], train_batch[-1]
            evals_result = {}
            with mlflow.start_run(nested=True, ) as partial_run:
                partial_run_id = partial_run.info.run_id
                ylog.info(f"Started mlflow.run: {partial_run_id}")
                ylog.info(f"Preparing on batch_{i + 1}({i + 1}/{len(train_batch_list)}) - {beg} >>> {end}")
                params["data.beg"] = beg
                params["data.end"] = end
                mlflow.log_params(params, run_id=partial_run_id)
                # 加载训练数据
                train_list_, valid_list_ = train_test_split(train_batch,
                                                            test_size=valid_size,
                                                            shuffle=shuffle,
                                                            random_state=random_state)
                train_dl = workflow.data.fetch(train_list_,
                                               batch_size=-1,
                                               eager=True)
                train_data = next(train_dl)
                if workflow.preprocessor:
                    train_data = workflow.preprocessor.partial_fit_transform(train_data)
                if valid_list_:
                    valid_dl = workflow.data.fetch(valid_list_,
                                                   batch_size=-1,
                                                   eager=True)
                    valid_data = next(valid_dl)
                    if workflow.preprocessor:
                        valid_data = workflow.preprocessor.fit_transform(valid_data)
                else:
                    valid_data = None

                if not features:
                    features = extract_feature_names(train_data.columns)
                else:
                    features = features
                if workflow.trainer.input_example is None:
                    workflow.trainer.input_example = train_data[features].head().to_pandas()
                target = get_timedelta_names(train_data.columns)
                if len(target) >= 1:
                    ylog.info(f"Target column found: {target}, use {target[0]}")
                else:
                    raise ValueError("Miss target columns in data")

                target = target[0]

                ylog.info("Building dataset.train...")
                train_data = workflow.trainer.create_dataset(data=train_data,
                                                             features=features,
                                                             target=target, )

                if valid_data is not None:
                    ylog.info("Building dataset.valid...")
                    valid_data = workflow.trainer.create_dataset(data=valid_data,
                                                                 features=features,
                                                                 target=target, )

                ylog.info(f"Training on batch_{i + 1}({i + 1}/{len(train_batch_list)}) - {beg} >>> {end}")

                # 训练模型
                workflow.trainer.fit(train_data=train_data,
                                     valid_data=valid_data,
                                     init_model=workflow.trainer.model,
                                     evals_result=evals_result,
                                     **workflow.trainer_params)

                # 保存模型
                # model_name = f"checkpoint_{i + 1}"
                # model_info = self.trainer.save_model(model, model_name, )
                # self.trainer.model = mlflow.pyfunc.load_model(model_info.model_uri)
                workflow.trainer.model = mlflow.pyfunc.load_model(f"runs:/{partial_run_id}/model")

                model = None


def predict(data_loader: 'DataLoader',
            model_uri: str,
            iterables: Sequence,
            batch_size: int = -1,
            features: list[str] | None = None,
            index: tuple[str] = ("date", "time", "asset"), ):
    """
    模型预测

    Parameters
    ----------
    data_loader: 'DataLoader',

    model_uri: str

    iterables: Sequence
        待评估的序列
    batch_size: int
        每次读取数据的批次，默认 -1: 全量读取
    features: list[str]|None
        特征名, 默认None。会排除date,time,asset,price,以timedelta命名的收益列
    index: tuple[str]
    Returns
    -------

    """
    import polars as pl

    batch_size = batch_size if batch_size > 0 else len(iterables)
    iterables = sorted(iterables)
    test_batch_list = [iterables[i:i + batch_size] for i in range(0, len(iterables), batch_size)]
    mod = mlflow.pyfunc.load_model(model_uri)
    preds = list()
    for i, test_batch in enumerate(test_batch_list):
        beg, end = test_batch[0], test_batch[-1]
        ylog.info(f"Preparing on batch_{i + 1}({i + 1}/{len(test_batch_list)}) - {beg} >>> {end}")
        test_dl = data_loader.fetch(test_batch, batch_size=-1,)
        test_data = next(test_dl)
        if not features:
            features = extract_feature_names(test_data.columns)
        else:
            features = features

        timedelta_names = get_timedelta_names(test_data.columns)

        ylog.info(f"Predicting on batch_{i + 1}({i + 1}/{len(test_batch_list)}) - {beg} >>> {end}")
        pred = mod.predict(test_data[features].to_numpy())
        pred = pl.Series(name="pred", values=pred)
        pred_batch = test_data.select(index).with_columns(pred)
        for timedelta_name in timedelta_names:
            pred_batch = pred_batch.with_columns(test_data[timedelta_name])
        preds.append(pred_batch)
    if preds:
        pred_df = pl.concat(preds)
    else:
        pred_df = None
    return pred_df
