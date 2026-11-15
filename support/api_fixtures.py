"""客户端类 fixture"""
import pytest

from api_client import ApiClient


@pytest.fixture
def client(base_url):
    return ApiClient(base_url)


# check_client / make_token 原样搬过来：
# 依赖 base_url 或 ApiClient 的，都属于这一层