# ===== conftest.py：pytest 自动加载，fixture 全局共享 =====
import os
import datetime
import logging
import json
import pytest
import requests
from api_client import ApiClient
from pytest_html import extras
import html as html_lib

logger=logging.getLogger(__name__)

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

ARTIFACT_DIR="artifacts"

@pytest.hookimpl(hookwrapper=True)#必须等 pytest 把 report 造好，才能读到 failed / longrepr
def pytest_runtest_makereport(item,call):
    """用例失败时，把最后一次请求、响应落盘到artifacts/"""
    outcome=yield#必须等 pytest 把 report 造好，才能读到 failed / longrepr
    report=outcome.get_result()
    #只要 call 阶段（setup 挂是 fixture 问题、teardown 挂用例本身是过的）
    if report.when != "call" or not report.failed:
        return

    client=item.funcargs.get("client")#从已完成注入的 fixture 里取实例；没写 client 的用例拿到 None，直接跳过
    exchange=getattr(client,"last_exchange",None) if client else None
    if exchange is None:
        return

    os.makedirs(ARTIFACT_DIR,exist_ok=True)#第一次跑自动建目录；不加 exist_ok 第二次会抛 FileExistsError
    ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    #参数化用例名长这样 test_x[case0]，Windows 文件名不允许方括号路径字符，不替换会写失败
    safe=item.name.replace("[","_").replace("]","").replace("/","_")
    path=f"{ARTIFACT_DIR}/{safe}_{ts}.json"

    with open(path,"w",encoding="utf-8") as f:
        json.dump({
            "test":item.nodeid,
            "error":str(report.longrepr)[:1000],
            "last_exchange":exchange,
        },f,ensure_ascii=False,indent=2)

    logger.info(f"失败现场已保存：{path}")
    # 把证据直接内嵌进报告（self-contained 模式也可见）
    extra_list = getattr(report, "extras", [])
    escaped = html_lib.escape(json.dumps(exchange, ensure_ascii=False, indent=2))
    extra_list.append(extras.html(
        "<div style='font-size:12px;'>"
        "<strong>失败现场</strong>"
        f"<pre style='white-space:pre-wrap;margin:6px 0 0 0;'>{escaped}</pre>"
        "</div>"
    ))
    # ↓ 新增：第二条「请求摘要」（一行速览，打开报告先看这个）
    summary = f"{exchange['method']} {exchange['path']} -> {exchange['status']} {exchange['cost_ms']}ms"
    extra_list.append(extras.html(
        "<div style='font-size:12px;'><strong>请求摘要</strong>"
        f"<pre style='white-space:pre-wrap;margin:6px 0 0 0;'>{html_lib.escape(summary)}</pre></div>"
    ))

    report.extras = extra_list

def pytest_terminal_summary(terminalreporter):#往控制台写内容，write_line() 就是它
    """跑完在控制台末尾打印证据文件数量"""
    if os.path.isdir(ARTIFACT_DIR):
        files = [f for f in os.listdir(ARTIFACT_DIR) if f.endswith(".json")]
        terminalreporter.write_line(f"artifacts 目录共 {len(files)} 个证据文件")