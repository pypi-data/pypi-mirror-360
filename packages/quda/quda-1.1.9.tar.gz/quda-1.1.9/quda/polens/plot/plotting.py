# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2024/12/9 下午1:29
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go

from .. import stats
import ylog
from .options import Options


def table(tb_data: pd.DataFrame, highlight_cols: list[str] = None):
    """绘制表格"""
    cols = tb_data.columns
    cellvalues = [[f'<b>{val}</b>' for val in tb_data[cols[0]]]]
    if highlight_cols is not None:
        col_dict = {k: 1 for k in highlight_cols}
        for col in cols[1:]:
            if col in col_dict:
                cellvalues.append([f'<b>{val}</b>' for val in tb_data[col].tolist()])
            else:
                cellvalues.append(tb_data[col])
    else:
        for col in cols[1:]:
            cellvalues.append(tb_data[col].tolist())
    tb = go.Table(
        header=dict(
            values=[f"<b>{col}</b>" for col in tb_data.columns],
            **Options.Table.header,
        ),
        cells=dict(
            values=cellvalues,  # [d.tolist() for g, d in tb_data.items()],
            **Options.Table.cell,
            fill=dict(color=['gold', 'white']),
        ),
    )
    return go.Figure(data=[tb], )


def distplot(data: pd.Series | pd.DataFrame, bin_size):
    """分布图: 每一列都是一组数据集"""
    if isinstance(data, pd.Series):
        data = data.to_frame()
    hist_data = list()
    group_labels = list()
    for col_name, col_data in data.items():
        hist_data.append(col_data.dropna())
        group_labels.append(col_name)
    fig = ff.create_distplot(hist_data, group_labels, bin_size=bin_size, colors=Options.colors)
    fig.update_layout(**Options.layout, )
    if data.index.name == "date":
        fig.update_xaxes(hoverformat='%Y-%m-%d', tickformat="%Y-%m-%d")
    return fig


def violin(data: pd.Series | pd.DataFrame):
    """index是x-axis, columns是datasets"""
    if isinstance(data, pd.Series):
        data = data.to_frame()
    fig = go.Figure()
    x_axis = data.index
    cols = data.columns
    for i, name in enumerate(cols):
        dataset = data[name]
        fig.add_trace(
            go.Violin(
                x=x_axis,
                y=dataset,
                name=name,
                marker_color=Options.colors[i % len(Options.colors)],
                box_visible=True,
                meanline_visible=True,
            )
        )

    fig.update_layout(**Options.layout, )
    if data.index.name == "date":
        fig.update_xaxes(hoverformat='%Y-%m-%d', tickformat="%Y-%m-%d")
    return fig


def bar(data: pd.Series | pd.DataFrame, title: str = None):
    """index是x-axis, columns是datasets"""
    if isinstance(data, pd.Series):
        data = data.to_frame()
    fig = go.Figure()
    x_axis = data.index
    cols = data.columns
    for i, name in enumerate(cols):
        dataset = data[name]
        fig.add_trace(
            go.Bar(
                x=x_axis,
                y=dataset,
                name=name,
                marker_color=Options.colors[i % len(Options.colors)],
            )
        )

    fig.update_layout(**Options.layout, )
    if title is not None:
        fig.update_layout(title=title)
    if data.index.name == "date":
        fig.update_xaxes(hoverformat='%Y-%m-%d', tickformat="%Y-%m-%d")
    return fig


def lines(data: pd.Series | pd.DataFrame):
    if isinstance(data, pd.Series):
        data = data.to_frame()
    fig = go.Figure()
    x_axis = data.index
    cols = data.columns
    for i, name in enumerate(cols):
        dataset = data[name]
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=dataset,
                name=name,
                mode="lines",
                marker_color=Options.colors[i % len(Options.colors)],
            )
        )

    fig.update_layout(**Options.layout, )
    if data.index.name == "date":
        fig.update_xaxes(hoverformat='%Y-%m-%d', tickformat="%Y-%m-%d")
    return fig


def nv_plot(data: pd.Series, starting_nv: float = 1.0):
    """
    绘制净值曲线
    Parameters
    ----------
    data: pd.Series
        累计净值, index: date
    starting_nv: float
        初始净值，默认 1

    Returns
    -------

    """
    if not isinstance(data, pd.Series):
        ylog.error(f"Input data must be pandas.Series, not {type(data)}")
        return

    # 收益数据
    ret = data.pct_change().fillna(data[0] / starting_nv - 1)
    # 计算指标
    ann_ret = stats.annual_return(ret)
    cum_ret = data[-1] - starting_nv
    ann_sd = stats.annual_volatility(ret)
    running_max = np.maximum.accumulate(data)
    underwater = (data - running_max) / running_max
    mdd = underwater.min()
    sharpe = ann_ret / ann_sd
    calmar = np.inf if mdd >= 0 else -ann_ret / mdd

    # if isinstance(data, pd.Series):
    #     data = data.to_frame()
    x_axis = data.index
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_axis,
            y=data,
            name=data.name,
            mode="lines",
            # marker_color="rgba(255, 0, 0, 0.8)",
            line=dict(width=2, color='rgba(255, 0, 0, 0.8)', ),
        )
    )
    # 添加最大回撤曲线
    fig.add_trace(
        go.Scatter(x=underwater.index,
                   y=underwater,
                   fill='tozeroy',
                   name='动态回撤',
                   fillcolor='rgba(199, 21, 133, 0.4)',
                   line=dict(width=0.5, color='rgba(199, 21, 133, 0.7)', ),
                   hovertemplate='%{fullData.name}:%{y:.2%}<extra></extra>',
                   yaxis="y2",
                   ),
        # secondary_y=True,
    )
    metric = dict(ann_ret=np.round(ann_ret, 3),
                  cum_ret=np.round(cum_ret, 3),
                  ann_sd=np.round(ann_sd, 3),
                  mdd=np.round(mdd, 5),
                  sharpe=np.round(sharpe, 2),
                  calmar=np.round(calmar, 2),)
    fig.add_annotation(
        xref='paper', yref='paper',
        x=0.02, y=2 / 3,
        xanchor='left', yanchor='middle',
        text=f'年化收益: {ann_ret * 100:.2f}% <br>'
             f'累计收益: {cum_ret * 100:.2f}% <br>'
             f'年化波动: {ann_sd * 100:.2f}% <br>'
             f'最大回撤: {mdd * 100:.2f}% <br>'
             f'sharpe: {sharpe:.2f} <br>'
             f'calmar: {calmar:.2f} <br>',
        font=dict(family='Arial, sans-serif',
                  size=12,
                  color='black'),
        align='left',
        borderwidth=2,
        borderpad=5,
        bordercolor='rgba(220, 220, 220, 0.5)',
        showarrow=False, textangle=0,
    )
    fig.update_layout(**Options.layout, yaxis2=dict(overlaying="y",
                                                    side="right",
                                                    gridcolor='lightgrey',
                                                    gridwidth=1,
                                                    griddash='dot',
                                                    range=[2 * mdd, 0]))
    if data.index.name == "date":
        fig.update_xaxes(hoverformat='%Y-%m-%d', tickformat="%Y-%m-%d")
    return fig, metric
