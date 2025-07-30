# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/23 15:09
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 
---------------------------------------------
"""

import abc
import mlflow


class BaseIncrementalTrainer(abc.ABC):
    """
    支持增量训练和mlflow管理的通用基础类

    该抽象基类定义了所有增量训练模型必须实现的核心接口，包括数据集构建(`create_dataset`)、训练流程(`fit`).
    """

    def __init__(self,
                 experiment_name: str, ):
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
        self.model = None
        self.input_example = None

    @abc.abstractmethod
    def create_dataset(self, data, features: list[str], target: str):
        """
        创建模型特定的数据集对象。

        子类需要实现此方法以将原始数据转换为模型可以接受的输入格式(如`lightgbm.Dataset`)

        Parameters
        ----------
        data: polars.DataFrame
            原始数据集，通常包含特征列和目标列
        features: list[str]
            特征列名列表
        target: str
            目标列名

        Returns
        -------
        object
            模型所需要的数据集对象(如`lightgbm.Dataset`)
        """
        pass

    @abc.abstractmethod
    def fit(self,
            train_data,
            valid_data=None,
            init_model=None,
            evals_result: dict | None = None,
            **model_params):
        """
        执行模型训练

        子类应该实现此方法以完成具体的训练逻辑，支持增量训练

        Parameters
        ----------
        train_data: object
            训练集对象，由`create_dataset`生成
        valid_data: object
            验证集对象，由`create_dataset`生成
        init_model: object, optional
            初始模型或者check_point.uri, 用于增量训练或者断点训练, 默认None
        evals_result: dict, optional
            用于存储评估结果的字典，默认None
        **model_params: dict
            模型超参

        Returns
        -------
        object
            训练完成的模型对象
        """
        pass

    def save_model(self, model, name: str):
        """保存模型到MLflow"""
        from mlflow.models.signature import infer_signature
        from lightgbm import Booster
        from torch.nn import Module
        signature = infer_signature(self.input_example)
        if isinstance(model, Booster):
            return mlflow.lightgbm.log_model(model, name=name, signature=signature, input_example=self.input_example)
        elif isinstance(model, Module):
            return mlflow.pytorch.log_model(model, name=name, signature=signature, input_example=self.input_example)
        else:
            raise ValueError("Unsupported model type")
