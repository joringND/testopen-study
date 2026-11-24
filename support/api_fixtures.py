"""客户端类 fixture"""
import pytest
import requests

from api_client import ApiClient


@pytest.fixture
def client(base_url):
    return ApiClient(base_url)

@pytest.fixture
def check_client():
    return requests

@pytest.fixture
def make_token():
    return "token123"


# check_client / make_token 原样搬过来：
# 依赖 base_url 或 ApiClient 的，都属于这一层