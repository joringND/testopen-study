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
