import os
import time
from typing import Annotated

import typer
from typer import prompt

app = typer.Typer(
    add_completion=True,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
    pretty_exceptions_short=False,
)


@app.command(help="检查 MindIE 高性能所需环境变量配置")
def check_mindie_high_preformance_env():
    from pae_toolkit.check_env import check_mindie_high_preformance_env as check_mindie_env

    check_mindie_env()


@app.command(help="检查 vLLM-ascend 高性能所需环境变量配置")
def check_vllm_high_preformance_env():
    from pae_toolkit.check_env import check_vllm_high_preformance_env as check_vllm_env

    check_vllm_env()


@app.command(help="测试大模型服务化正确性")
def val_llm_acc(
    model_name: Annotated[str, typer.Option()],
    port=8000,
    host="localhost",
):
    from pae_toolkit.val.test_llm_serve_acc import run_llm_serve_acc_test

    run_llm_serve_acc_test(
        model_name=model_name,
        port=port,
        host=host,
    )


# @app.command(help="启动单机P&D服务")
def start_single_machine_pd_server(
    start_npu_id: int = typer.Option(-1),
    p_node_num: int = typer.Option(-1),
    npu_num_per_p_node: int = typer.Option(-1),
    d_node_num: int = typer.Option(-1),
    npu_num_per_d_node: int = typer.Option(-1),
    docker_image: str = typer.Option(""),
    model_path: str = typer.Option(""),
):
    from pae_toolkit.pd import Config, start_pd

    config = Config()
    config.start_npu_id = int(prompt("起始的NPU ID")) if start_npu_id < 0 else start_npu_id
    config.p_node_num = int(prompt("P节点数量")) if p_node_num < 0 else p_node_num
    config.npu_num_per_p_node = (
        int(prompt("每个P节点NPU数量")) if npu_num_per_p_node < 0 else npu_num_per_p_node
    )
    config.d_node_num = int(prompt("D节点数量")) if d_node_num < 0 else d_node_num
    config.npu_num_per_d_node = (
        int(prompt("每个D节点NPU数量")) if npu_num_per_d_node < 0 else npu_num_per_d_node
    )
    config.docker_image = str(prompt("Docker镜像")) if docker_image == "" else docker_image
    config.model_path = str(prompt("模型路径")) if model_path == "" else model_path
    return start_pd(config)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
