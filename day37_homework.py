import json
import pytest


def test_env_config(env_name, base_url):
    with open("config/env.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)
    assert base_url == cfg[env_name]       # ✅ 同样直接取


def test_env_name_valid(env_name):
    assert env_name in ("test", "pre", "prod")


def test_real_api_only_in_test(env_name, client):
    """真实请求只在 test 环境跑；pre/prod 是假地址，跳过"""
    if env_name != "test":
        pytest.skip(f"当前是 {env_name} 假环境，跳过真实请求")
    resp = client.get_user()
    assert resp.status_code == 200
    assert resp.json()["name"] == "张三"

# 思考：base_url 用 session 作用域，如果改成 function 会怎样？（不会错，但有什么浪费？）
print('不会出错，但每个用例都重新 open 一次 env.json（重复磁盘 IO）；\
      而且配置只读、会话内不变，重复读毫无意义。session 作用域只读一次、全会话复用 ——只读配置用 session\
      （Day31 原则的正向应用）')
# 思考：Jenkins 里跑用例时，--env 和 “环境变量” 哪种方式更好？为什么？
print('''
两者都行，实战倾向：
--env 更显式：pytest --env pre 写在构建命令里，报错清晰（环境不存在会立刻提示可选值）
环境变量更通用：ENV=pre 能跨工具 / 跨语言复用（Docker、部署脚本都认），CI 里常用 --env ${ENV} 把 Jenkins 参数拼进去
结论：框架内用 --env，CI 层用变量传值，两者结合（Jenkins 参数 → 拼进命令行）
''')
# 🤖 AI 自测 5 题（一起发我）
# 用例里写死 BASE = "http://127.0.0.1:8000" 有什么问题？（说出两个）
print('''
① 换环境要改 N 个文件 N 处，漏一处 = 一半打测试一半打预发，报告全乱
② 地址散落无法集中管理，运维 / CI 无法按环境切换（不改代码就跑不了别的环境）
''')
# pytest_addoption 是干什么的？
print('pytest 的钩子函数，用来注册自定义命令行参数（如 --env），\
      注册后 conftest 里用 request.config.getoption("--env") 读取')
# request.config.getoption("--env") 返回什么？
print('返回命令行传的值字符串：默认 "test"，传 --env pre 就是 "pre"（没传时用 addoption 的 default）')
# 配置是只读的，fixture 该用什么作用域？理由？
print('session—— 配置整个会话不变，读一次就够；function 会每个用例重复读文件，纯浪费')
# 写代码：conftest 里注册 --env + env_config fixture（读 env.json 返回地址）    
import json
import pytest

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="test",
                     help="运行环境: test/pre")

@pytest.fixture(scope="session")
def env_name(request):
    return request.config.getoption("--env")

@pytest.fixture(scope="session")
def env_config(env_name):
    with open("config/env.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)
    assert env_name in cfg, f"环境不存在: {env_name}，可选 {list(cfg.keys())}"
    return cfg[env_name]