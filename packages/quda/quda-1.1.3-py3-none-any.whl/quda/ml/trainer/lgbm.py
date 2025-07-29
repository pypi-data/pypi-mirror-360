# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/23 20:34
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 
---------------------------------------------
"""

import ylog

from .base import BaseIncrementalTrainer
import lightgbm as lgb


class LightGBMTrainer(BaseIncrementalTrainer):

    def __init__(self, experiment_name: str = "LightGBM-Incremental",):
        super().__init__(experiment_name)

    def create_dataset(self, data, features: list[str], target: str):
        return lgb.Dataset(data[features].to_numpy(), label=data[target].to_numpy(), feature_name=features)

    def fit(self,
            train_data: lgb.Dataset,
            valid_data: lgb.Dataset | None = None,
            init_model=None,
            evals_result: dict | None = None,
            **model_params):
        evals_result = dict() if evals_result is None else evals_result
        _params = {**model_params}

        # 检查 参数
        params = {"early_stopping_rounds": 10,
                  "num_boost_round": 100,
                  "log_eval_period": 10}
        for check in params.keys():
            if check not in _params:
                ylog.warning(f"Missing `{check}`, set default value: {params.get(check)}")
            else:
                params[check] = _params.pop(check)

        early_stopping_callback = lgb.early_stopping(params["early_stopping_rounds"])
        verbose_eval_callback = lgb.log_evaluation(params["log_eval_period"])
        callbacks = [early_stopping_callback, verbose_eval_callback,]

        valid_sets = [train_data, ]
        valid_names = ["train"]
        if valid_data is not None:
            valid_sets.append(valid_data)
            valid_names.append("valid")

        model = lgb.train(
            _params,
            train_set=train_data,
            init_model=init_model,
            valid_sets=valid_sets,
            valid_names=valid_names,
            num_boost_round=params.get("num_boost_round"),
            callbacks=callbacks,
        )

        return model
