# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License.
Created on 2025/6/25 15:05
Email: yundi.xxii@outlook.com
Description: 主流程控制
---------------------------------------------
"""

import ygo
from omegaconf import DictConfig, OmegaConf
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

from ..data import DataLoader
from ..pipeline import IncrementalPipeline
from ..trainer import BaseIncrementalTrainer
from ..utils import is_notebook, hydra_wrapper
from .evaluator import train, predict


class WorkFlow(BaseEstimator):
    """
    构建 训练工作流: 从数据加载->预处理->增量训练。支持 sklearn式更改配置、从配置文件中加载
    """

    def __init__(self,
                 data: list,
                 trainer: BaseIncrementalTrainer,
                 preprocessor: list | None = None,
                 trainer_params: dict | None = None):
        """
        构造工作流

        Parameters
        ----------
        data: list
            数据加载步骤
        trainer: BaseIncrementalTrainer
            训练器：quda.ml.trainer.BaseIncrementalTrainer 的实现实例
        preprocessor: list
            预处理步骤，默认None: 不做预处理
        trainer_params:
            训练器参数
        """
        # 初始化
        self.data = DataLoader(steps=data)
        self.trainer = trainer
        if isinstance(self.trainer, type):
            self.trainer = self.trainer()
        assert isinstance(self.trainer,
                          BaseIncrementalTrainer), "trainer must be a subclass of `BaseIncrementalTrainer`"
        self.trainer_params = trainer_params
        self.preprocessor = IncrementalPipeline(preprocessor) if preprocessor else None
        self.pipe = Pipeline([
            ("data", self.data.pipe),
            ("trainer", self.trainer)
        ])
        if self.preprocessor:
            self.pipe.steps.insert(1, ("preprocessor", self.preprocessor.pipe))

        self._html_repr = self.pipe._html_repr

    @classmethod
    def initialize(cls, cfg: DictConfig) -> 'WorkFlow':
        """
        从 解析出来的 初始化 workflow
        """

        from hydra.utils import instantiate

        # 构建 data pipeline
        data_steps = []
        data_steps = instantiate(cfg.data)
        data_steps = [(name, step) for d in data_steps for name, step in d.items()]

        # 构建 preprocessor
        preprocessor_steps = None
        if cfg.get("preprocessor"):
            preprocessor_steps = []
            preprocessor_steps = instantiate(cfg.preprocessor)
            preprocessor_steps = [(name, step) for d in preprocessor_steps for name, step in d.items()]

        # 构建 trainer
        trainer = instantiate(cfg.trainer.trainer)

        # trainer_params
        trainer_params = instantiate(cfg.trainer.trainer_params)
        trainer_params = OmegaConf.to_container(trainer_params, resolve=True)

        wf = cls(data=data_steps,
                 trainer=trainer,
                 preprocessor=preprocessor_steps,
                 trainer_params=trainer_params)
        return wf

    @classmethod
    def from_conf(cls, config_path: str = "conf", config_name: str = "config") -> 'WorkFlow':
        """
        配置驱动:从配置文件中构建工作流


        Examples
        --------
        >>> import quda.ml
        >>> workflow = quda.ml.WorkFlow.from_conf(config_path='conf', config_name="config")
        >>> workflow.set_params(...) # 更改配置
        >>> workflow.fit(...) # 开始训练

        Returns
        -------
        """
        if is_notebook():
            print(f"""Run in notebook, please use hydra to run.
::code::
from hydra import initialize, compose
with initialize(version_base=None, config_path='{config_path}'):
    cfg = compose(config_name='{config_name}')
wf = quda.ml.WorkFlow.initialize(cfg)
""")
            return

        hydra_main = hydra_wrapper(config_path, config_name)
        if hydra_main is not None:
            return hydra_main(cls.initialize)()

    @classmethod
    def train(cls, cfg: DictConfig):
        """
        从解析后的config运行配置
        Returns
        -------
        """
        wf = cls.initialize(cfg)
        sig_params = ygo.fn_signature_params(train)
        params = {k: v for k, v in cfg.items() if k in sig_params}
        if params:
            from hydra.utils import instantiate
            params = instantiate(params)
        return train(workflow=wf, **params)

    @classmethod
    def train_conf(cls, config_path: str = "conf", config_name: str = "config", ):
        """
        从配置文件中创建 WorkFlow 对象，并且运行 train

        Returns
        -------

        """

        if is_notebook():
            print(f"""Run in notebook, please use hydra to run.
::code::
from hydra import initialize, compose
with initialize(version_base=None, config_path='{config_path}'):
    cfg = compose(config_name='{config_name}')
quda.ml.WorkFlow.train(cfg)
""")
            return
        hydra_main = hydra_wrapper(config_path, config_name)
        if hydra_main is not None:
            return hydra_main(cls.train)()

    @classmethod
    def predict(cls, cfg: DictConfig):
        """
        从解析后的config运行配置

        Returns
        -------
        polars.DataFrame
        """
        data_loader = DataLoader.initialize(cfg)
        sig_params = ygo.fn_signature_params(predict)
        params = {k: v for k, v in cfg.items() if k in sig_params}
        if params:
            from hydra.utils import instantiate
            params = instantiate(params)
        return predict(data_loader=data_loader, **params)

    @classmethod
    def predict_conf(cls, config_path: str = "conf", config_name: str = "config",):
        """
        从配置文件中运行预测

        Parameters
        ----------
        config_path: str
        config_name: str

        Returns
        -------
        polars.DataFrame
        """
        if is_notebook():
            print(f"""Run in notebook, please use hydra to run.
::code::
from hydra import initialize, compose
with initialize(version_base=None, config_path='{config_path}'):
    cfg = compose(config_name='{config_name}')
quda.ml.WorkFlow.predict(cfg)
""")
            return
        hydra_main = hydra_wrapper(config_path, config_name)
        if hydra_main is not None:
            return hydra_main(cls.predict)()
