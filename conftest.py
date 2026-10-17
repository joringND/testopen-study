# ===== conftest.py：pytest 自动加载，fixture 全局共享 =====
import pytest
import requests
@pytest.fixture
def base_url():
    """测试环境基础地址——换环境只改这里"""
    return "http://127.0.0.1:8000"

@pytest.fixture
def check_client():
    return requests

@pytest.fixture
def make_token():
    return "token123"