# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/6/27 18:51
Email: yundi.xxii@outlook.com
Description: 
---------------------------------------------
"""

# quda/ml/trainer/pytorch.py

from .base import BaseIncrementalTrainer
import pytorch_lightning as pl
import torch
from mlflow.models.signature import infer_signature


class PyTorchLightningTrainer(BaseIncrementalTrainer):
    def __init__(self, model: pl.LightningModule, datamodule: pl.LightningDataModule, experiment_name="PTL-Incremental"):
        super().__init__(experiment_name=experiment_name)
        self.model = model
        self.datamodule = datamodule
        self.trainer = None

    def create_dataset(self, data, features: list[str], target: str):
        # 将 Polars DataFrame 转换为 Dataset / DataLoader
        return self.datamodule(data, features, target)

    def fit(self, train_data, valid_data=None, init_model=None, evals_result: dict | None = None, **model_params):
        trainer_kwargs = {
            "max_epochs": model_params.get("max_epochs", 10),
            "callbacks": [self._mlflow_callback(evals_result)],
            "logger": False,
        }
        self.trainer = pl.Trainer(**trainer_kwargs)
        self.trainer.fit(self.model, datamodule=self.datamodule)
        return self.model

    def _mlflow_callback(self, evals_result):
        """MLflow logging callback"""
        class MLFlowLoggerCallback(pl.Callback):
            def on_validation_end(self, trainer, pl_module):
                metrics = trainer.callback_metrics
                for key, value in metrics.items():
                    mlflow.log_metric(key, value.item(), step=trainer.global_step)
                evals_result.update(metrics)
        return MLFlowLoggerCallback()
