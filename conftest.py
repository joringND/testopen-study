# ===== conftest.py：pytest 自动加载，fixture 全局共享 =====
import json
import pytest
import requests
from api_client import ApiClient

#ENV="test"# 切换环境：只改这一行(day25框架工程化使用，已废弃)
# ---- 新增：注册 --env 命令行参数 ----
def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="test",
                     help="运行环境: test/pre")

@pytest.fixture(scope="session")
def env_name(request):
    return request.config.getoption("--env")

# @pytest.fixture
# def base_url():
#     """测试环境基础地址——换环境只改这里"""
#     with open("config/env.json","r",encoding="utf-8") as f:
#         envs=json.load(f)
#         return envs[ENV]
# base_url从"写死的字符串"变成"查表的结果"——环境名→地址的映射放配置文件，切环境 = 改 ENV 一个字母
#day25框架工程化使用，已废弃

@pytest.fixture(scope="session")
def base_url(env_name):
    with open("config/env.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)                 # {"test": "...", "pre": "..."}
    assert env_name in cfg, \
        f"环境不存在: {env_name}，可选 {list(cfg.keys())}"
    return cfg[env_name]                   # ✅ 直接按 key 取

@pytest.fixture
def check_client():
    return requests

@pytest.fixture
def make_token():
    return "token123"

@pytest.fixture
def client(base_url):          # fixture 里用另一个 fixture（依赖注入）
    return ApiClient(base_url)