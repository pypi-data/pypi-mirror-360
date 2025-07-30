import argparse
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Annotated

import requests

try:
    import pytest  # noqa: F401
except ImportError:
    os.system("pip install --default-timeout=3 pytest")

try:
    import typer
except ImportError:
    os.system("pip install --default-timeout=3 typer")
    import typer

app = typer.Typer(
    add_completion=True,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
    pretty_exceptions_short=False,
)

# Global variables
url = "http://localhost:8080/v1/completions"
model = "vllm-acc"
headers = {"Content-Type": "application/json"}


def test_vllm_acc_with_temperature0():
    """Test the accuracy of the API."""
    response = requests.post(
        url,
        headers=headers,
        json={
            "model": model,
            "prompt": "San Francisco is a",
            "max_tokens": 28,
            "temperature": 0,
        },
        timeout=10000,
    )
    res = response.json()
    assert (
        res["choices"][0]["text"]
        == " city that is known for its vibrant culture, stunning architecture, and breathtaking views. However, one of the most iconic features of the city is"
    ), f"response: {res}"


def test_vllm_acc_with_temperature0_concurrent16():
    def request2vllm(session) -> str:
        """Test the accuracy of the API."""
        response = session.post(
            url,
            headers=headers,
            json={
                "model": model,
                "prompt": "San Francisco is a",
                "max_tokens": 28,
                "temperature": 0,
            },
            timeout=60,  # 减少超时时间以适应多并发测试
        )
        res = response.json()
        return res["choices"][0]["text"]

    # 创建会话池
    res_list = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = executor.map(request2vllm, [requests.Session() for _ in range(16)])
        for future in futures:
            res_list.append(future)

    assert all(
        res
        == " city that is known for its vibrant culture, stunning architecture, and breathtaking views. However, one of the most iconic features of the city is"
        for res in res_list
    ), f"response: {res_list}"


def test_vllm_acc_with_temperature0_6():
    """Test the accuracy of the API."""
    response = requests.post(
        url,
        headers=headers,
        json={
            "model": model,
            "prompt": "San Francisco is a",
            "max_tokens": 28,
            "temperature": 0.6,
        },
        timeout=10000,
    )
    res = response.json()
    assert (
        res["choices"][0]["text"]
        == " city that is known for its diverse neighborhoods, each with its own unique character and charm. From the bustling streets of Chinatown to the"
    ), f"response: {res}"


@app.command()
def run_llm_serve_acc_test(
    model_name: Annotated[str, typer.Option()],
    port=8000,
    host="localhost",
):
    global url, model
    url = f"http://{host}:{port}/v1/completions"
    model = model_name

    os.system(f"pytest {__file__} -s -v")


if __name__ == "__main__":
    app()
