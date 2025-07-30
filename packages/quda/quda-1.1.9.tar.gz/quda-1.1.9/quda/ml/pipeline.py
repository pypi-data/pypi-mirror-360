# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License.
Created on 2025/6/25 15:05
Email: yundi.xxii@outlook.com
Description: 增量流水线
---------------------------------------------
"""

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline


class IncrementalPipeline(BaseEstimator, TransformerMixin):
    """
    支持 partial_fit 的 Pipeline。
    只对支持 partial_fit 的 transformer 执行该操作，其余保存不变。
    """

    def __init__(self, steps: list):
        pipe_steps = list()
        if steps:
            for name, step in steps:
                if isinstance(step, type):
                    pipe_steps.append((name, step()))
                else:
                    pipe_steps.append((name, step))
        self.pipe = Pipeline(pipe_steps)

    def fit(self, X, y=None):
        """完整fit整个pipeline"""
        for _, step in self.pipe.steps:
            X = step.fit_transform(X, y)
        return self

    def transform(self, X):
        for _, step in self.pipe.steps:
            X = step.transform(X)
        return X

    def fit_transform(self, X, y=None, **fit_params):
        return self.fit(X, y).transform(X)

    def partial_fit(self, X, y=None):
        """只对支持 partial_fit 的步骤进行增量更新"""
        for name, step in self.pipe.steps:
            if hasattr(step, "partial_fit"):
                step.partial_fit(X, y)
            else:
                step.fit(X, y)
            X = step.transform(X)
        return self

    def partial_fit_transform(self, X, y=None):
        return self.partial_fit(X, y).transform(X)

    def set_params(self, **params):
        """允许通过类似 sklearn 的 params__value设置参数"""
        self.pipe.set_params(**params)
        return self

    def get_params(self, deep=True):
        """返回所有步骤的参数，用于 mlflow logging 或者 gridsearch cv"""
        return self.pipe.get_params(deep=deep)
