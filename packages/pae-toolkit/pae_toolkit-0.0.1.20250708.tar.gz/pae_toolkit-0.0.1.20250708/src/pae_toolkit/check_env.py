from typing import Any, List, Tuple
import os
import platform
import shlex
import subprocess

from rich import print as rprint
from rich.markdown import Markdown
from rich.panel import Panel

from pae_toolkit.util.timer import Timer

base_env_dict:dict[str, str |int |List[str|int] |Tuple[float, float]] = {
    "PYTORCH_NPU_ALLOC_CONF": "expandable_segments:True",
    "OMP_PROC_BIND": "false",
    "OMP_NUM_THREADS": [100,1],
    "TASK_QUEUE_ENABLE": 2,
    "CPU_AFFINITY_CONF": [2, 1],  # 0: no affinity, 1: cpu affinity, 2: cpu affinity + numa
    "HCCL_OP_EXPANSION_MODE": "AIV",
    "HCCL_DETERMINISTIC": "false",  # 关闭确定性计算
    "HCCL_CONNECT_TIMEOUT": 7200,  # 建链等待时间
    "HCCL_EXEC_TIMEOUT": 0,  # 设备间执行等待时间
    "ASCEND_LAUNCH_BLOCKING": [0, ""],  # 非阻塞模式
    "NPU_MEMORY_FRACTION": (0.94, 0.97),
    "INF_NAN_MODE_FORCE_DISABLE": 1,
}

def check_env(env_dict: dict[str, Any], desc: str = ""):
    print(f"Environment variables {desc}:")
    env_suggest_str = "#!/bin/bash\nrm -rf /root/mindie /root/ascend"
    is_env_flag = True
    for environment in env_dict:
        flag = False
        expected_env_value = env_dict[environment]
        env_value = os.getenv(environment)
        env_value = env_value if env_value else ""
        if isinstance(expected_env_value, str):
            if env_value == str(expected_env_value):
                flag = True
        elif isinstance(expected_env_value, int):
            if env_value == str(expected_env_value):
                flag = True
        elif isinstance(expected_env_value, tuple):
            if (
                env_value
                and float(env_value) >= expected_env_value[0]
                and float(env_value) <= expected_env_value[1]
            ):
                flag = True
        elif isinstance(expected_env_value, list):
            if env_value in [str(i) for i in expected_env_value]:
                flag = True
        else:
            print("Unknown type")

        if flag:
            rprint(f"\t[green][√][/green] [white]{environment}={env_value}[/white]")
        else:
            is_env_flag = False
            rprint(
                f'\t[red][X][/red] [white]{environment}={env_value}, expected="{expected_env_value}"[/white]'
            )
            if isinstance(expected_env_value, str) or isinstance(expected_env_value, int):
                os.environ[environment] = str(expected_env_value)
            elif isinstance(expected_env_value, tuple):
                os.environ[environment] = str(expected_env_value[0])
            elif isinstance(expected_env_value, list):
                os.environ[environment] = str(expected_env_value[0])
            env_suggest_str += f'\nexport {environment}="{os.environ[environment]}"'

    if is_env_flag:
        rprint(Panel("环境相应配置已设置成功。", title="Tip"))
    else:
        rprint("[bold yellow][Tip] Following cmd to set the environment variables:[/bold yellow]")
        print(env_suggest_str)

cpu_power_suggestion = """
执行 `yum install kernel-tools` or `apt install cpufrequtils` 命令安装工具，\\
安装成功后执行 `cpupower -c all frequency-set -g performance` 开启 CPU性能模式
"""

def check_machine_info():
    print("System Info:")
    system_info = {
        "操作系统名称及版本号": platform.platform(),
        "操作系统的位数": ' '.join(platform.architecture()),
        "处理器信息": platform.processor(),
        "Python版本": platform.python_version(),
        "CPU核数": str(os.cpu_count()),
    }
    for k, v in system_info.items():
        print(f"{k}: {v}")

    if platform.system() == "Linux":
        cmd_res = subprocess.run(
            shlex.split("cat /sys/kernel/mm/transparent_hugepage/enabled"), capture_output=True
        ).stdout.decode()
        if cmd_res.split()[0] == "[always]":
            rprint("[green]Transparent Hugepages is enabled[/green]")
        else:
            rprint("[red]Transparent Hugepages is disabled[/red]")

    if True:
        rprint(Panel(Markdown(cpu_power_suggestion), title="CPU Power"))


def check_mindie_high_preformance_env():
    env_dict:dict[str, str |int |List[str|int] |Tuple[float, float]] = {
        **base_env_dict,
        "MINDIE_LOG_TO_STDOUT": 0,
        "MINDIE_LOG_TO_FILE": 1,
        "MINDIE_LOG_LEVEL": ["info", "INFO", "error", "ERROR", "info; llm:error; server:error"],
        "MINDIE_ASYNC_SCHEDULING_ENABLE": 1,  # 异步双发射
        "ATB_LLM_HCCL_ENABLE": 1,
        "ATB_LLM_COMM_BACKEND": "hccl",
        "ATB_WORKSPACE_MEM_ALLOC_ALG_TYPE": 3,
        "ATB_WORKSPACE_MEM_ALLOC_GLOBAL": 1,
        "ATB_LLM_ENABLE_AUTO_TRANSPOSE": 0,
        # MindIE 2.0RC1
        "ATB_LAYER_INTERNAL_TENSOR_REUSE": 1,
        "ATB_OPERATION_EXECUTE_ASYNC": 1,
        "ATB_CONVERT_NCHW_TO_ND": 1,
        "ATB_CONTEXT_WORKSPACE_SIZE": 0,
        "ATB_LAUNCH_KERNEL_WITH_TILING": 1,
    }
    check_machine_info()
    check_env(env_dict)


def check_vllm_high_preformance_env():
    env_dict:dict[str, str |int |List[str|int] |Tuple[float, float]]  = {
        **base_env_dict,
        "VLLM_USE_V1": 1,

    }
    turbo_env_dict:dict[str, str |int |List[str|int] |Tuple[float, float]] = {
        "VLLM_OPTIMIZATION_LEVEL": 3,
        "USING_LCCL_COM": 1,
        "USING_SAMPLING_TENSOR_CACHE": 1,
    }
    check_machine_info()
    check_env(env_dict, desc="VLLM High Performance Mode")
    check_env(turbo_env_dict, desc="MindIE Turbo Mode")
