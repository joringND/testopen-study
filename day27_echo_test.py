# day27_echo_test.py —— 三步法实战：测 /echo 回显
from api_client import ApiClient
import pytest

def test_echo():
    client = ApiClient("http://127.0.0.1:8000")
    payload = {"hello": "world"}
    data = client.echo(payload).json()
    assert data["echo"] == payload