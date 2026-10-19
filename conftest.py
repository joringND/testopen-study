# ===== conftest.py：pytest 自动加载，fixture 全局共享 =====
import pytest
import requests
from api_client import ApiClient
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

@pytest.fixture
def client(base_url):          # fixture 里用另一个 fixture（依赖注入）
    return ApiClient(base_url)