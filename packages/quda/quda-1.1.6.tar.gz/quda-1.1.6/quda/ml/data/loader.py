# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/6/25 15:05
Email: yundi.xxii@outlook.com
Description: 数据加载器，支持分批加载和流水线处理
---------------------------------------------
"""
from collections.abc import Sequence

from omegaconf import DictConfig
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline
from tqdm.auto import tqdm

from ..utils import is_notebook, hydra_wrapper


class DataLoader(BaseEstimator):
    """
    数据加载器

    该类封装了 `sklearn.pipeline.Pipeline`，支持以批处理方式执行多个数据转换步骤，
    并能将结果合并为一个 `polars.DataFrame`。适用于大规模数据集的流式处理。

    Attributes
    ----------
    pipe : sklearn.pipeline.Pipeline
        内部使用的数据处理流水线对象。
    """

    def __init__(self,
                 steps: list):

        """
        初始化 DataLoader 实例。

        Parameters
        ----------
        steps : list of (str, transformer) tuples
            流水线中的各个处理步骤，格式与 sklearn 的 Pipeline 相同。

            示例：

            >>> steps = [('step1', Transformer1()), ('step2', Transformer2())]

        See Also
        --------
        sklearn.pipeline.Pipeline : sklearn 中用于构建数据处理流程的标准类。

        """
        pipe_steps = list()
        if steps:
            for name, step in steps:
                if isinstance(step, type):
                    pipe_steps.append((name, step()))
                else:
                    pipe_steps.append((name, step))
        self.pipe = Pipeline(pipe_steps)
        self._html_repr = self.pipe._html_repr

    def fetch(self,
              iterables: Sequence,
              batch_size: int = -1,
              show_progress: bool = True,
              eager: bool = True):
        """
        分批次加载并处理数据。

        将输入的可迭代对象按 `batch_size` 分批加载。每个单位(iterables.item)的数据会通过 `Pipeline` 进行转换，
        最终合并成一个 `polars.DataFrame` 返回。

        Parameters
        ----------
        iterables: Sequence
            可迭代对象
        batch_size: int
            每次处理的数据量大小。默认为 -1，表示一次性返回所有数据。
        eager: bool
        show_progress

        Yields
        -------
        polars.DataFrame | polars.LazyFrame
            处理后的数据批次，合并为一个 DataFrame 后逐个返回。

        Examples
        --------
        >>> from sklearn.preprocessing import FunctionTransformer
        >>> import pandas as pd
        >>>
        >>> steps = [('transformer', FunctionTransformer(lambda x: pd.DataFrame({"x": [x]})))]
        >>> loader = DataLoader(steps)
        >>> data = [1, 2, 3, 4, 5]
        >>> for batch in loader.fetch(data, batch_size=2):
        ...     print(batch)

        """

        from polars import concat, LazyFrame

        batch_size = batch_size if batch_size > 0 else len(iterables)
        ranger = range(0, len(iterables), batch_size)
        ranger = tqdm(ranger, desc=f"{self.__class__.__name__}.fetching") if show_progress else ranger
        for i in ranger:
            batch = iterables[i: i + batch_size]
            lfList = [self.pipe.fit_transform(item) for item in batch]
            if batch_size > 1:
                lf = concat(lfList)
            else:
                lf = lfList[0]
            if isinstance(lf, LazyFrame) and eager:
                lf = lf.collect()
            yield lf

    def set_params(self, **params):
        """允许通过类似 sklearn 的 params__value设置参数"""
        self.pipe.set_params(**params)

    def get_params(self, deep=True):
        """返回所有步骤的参数，用于 mlflow logging 或者 gridsearch cv"""
        return self.pipe.get_params(deep=deep)

    @classmethod
    def initialize(cls, cfg: DictConfig) -> 'DataLoader':
        """
        从 解析出来的 初始化 DataLoader
        """

        from hydra.utils import instantiate

        # 构建 data pipeline
        data_steps = []
        data_steps = instantiate(cfg.data)
        data_steps = [(name, step) for d in data_steps for name, step in d.items()]
        return cls(data_steps)

    @classmethod
    def from_conf(cls, config_path: str, config_name: str) -> 'DataLoader':
        if is_notebook():
            print(f"""Run in notebook, please use hydra to run.
::code::
from hydra import initialize, compose
with initialize(version_base=None, config_path='{config_path}'):
    cfg = compose(config_name='{config_name}')
dl = quda.ml.DataLoader.initialize(cfg)
""")
            return

        hydra_main = hydra_wrapper(config_path, config_name)
        if hydra_main is not None:
            return hydra_main(cls.initialize)()
