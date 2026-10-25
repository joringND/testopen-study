# ===== conftest.py：pytest 自动加载，fixture 全局共享 =====
import json
import pytest
import requests
from api_client import ApiClient

ENV="test"# 切换环境：只改这一行

@pytest.fixture
def base_url():
    """测试环境基础地址——换环境只改这里"""
    with open("config/env.json","r",encoding="utf-8") as f:
        envs=json.load(f)
        return envs[ENV]
#base_url从"写死的字符串"变成"查表的结果"——环境名→地址的映射放配置文件，切环境 = 改 ENV 一个字母

@pytest.fixture
def check_client():
    return requests

@pytest.fixture
def make_token():
    return "token123"

@pytest.fixture
def client(base_url):          # fixture 里用另一个 fixture（依赖注入）
    return ApiClient(base_url)