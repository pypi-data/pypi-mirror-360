# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/6/26 15:54
Email: yundi.xxii@outlook.com
Description: quda cli 入口
---------------------------------------------
"""

import typer

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo("Run `quda --help` to get more information.")

@app.command()
def init_config():

    """生成模版配置，复制自: quda/ml/conf"""

    typer.echo(f"[QUDA] - Copy quda.ml.conf template.")

    from .app import init_config as init_config_
    init_config_()

@app.command()
def update():

    """数据更新"""
    import quda

    quda.update()




if __name__ == '__main__':
    app()