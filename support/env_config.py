"""环境配置：--env 参数 + 环境相关 fixture"""
import json

import pytest

from support.paths import CONFIG_PATH


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="test", help="环境: test/pre")


@pytest.fixture(scope="session")
def env_name(request):
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def base_url(env_name):
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    assert env_name in cfg, f"环境 {env_name} 不存在，可选 {list(cfg.keys())}"
    return cfg[env_name]