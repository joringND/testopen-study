# 练习1：升级 mock v3（照抄）+ 重启
# 验证：连调两次 login()，打印两次的 token（应该不同：token-1、token-2）
import requests
import pytest
resp1 = requests.post("http://127.0.0.1:8000/login",
                      json={"user": "test", "pwd": "123"}, timeout=5)
print("第一次登录 token:", resp1.json()["token"])    # token-1

resp2 = requests.post("http://127.0.0.1:8000/login",
                      json={"user": "test", "pwd": "123"}, timeout=5)
print("第二次登录 token:", resp2.json()["token"])    # token-2（不同！）

# 练习2：新建 api_client.py（照抄完整版）
#   跑通：client = ApiClient("http://127.0.0.1:8000") → client.get_user() → 断言 name == "张三"
#   （不手动 login、不手动 headers——全部自动）
from api_client import ApiClient
client = ApiClient("http://127.0.0.1:8000")
client.get_user()  # 自动登录 + 自动带 token + 401 自动重试
# 练习3：conftest 加 client fixture → 用例改成用 client 参数
# 练习4：建 data/users.json + 数据驱动参数化用例，跑 3 passed
import json
import pytest
from api_client import ApiClient

# 练习3：conftest 的 client fixture —— 直接注入用
def test_get_user_with_client(client):
    data = client.get_user().json()
    assert data["name"] == "张三"

# 练习4：数据驱动 —— 从 data/users.json 读 3 组数据
with open("data/users.json", "r", encoding="utf-8") as f:
    USERS = json.load(f)

@pytest.mark.parametrize("case", USERS)
def test_login_cases(client, case):
    resp = client.login(case["user"], case["pwd"])
    assert resp.json()["code"] == case["expect_code"]    
# self.token 存的是什么？为什么要缓存它而不是每次现登录？
print('存的是登录响应里的 token 字符串（凭证）。缓存是为了一次登录、多次使用—— \
      每次请求都现登录既慢，又会不断刷新 "最新 token" 把自己搞过期（mock v3 里登录一次换一次 token）')
# _request 里 401 重试的逻辑是什么？（用文字 / 伪代码描述）
print("请求返回 401 → 说明 token 可能过期 → 调 self.login() 换新 token（self.token 更新）\
      → 用新 token 重写 Authorization header → 重发同样的请求 → 返回重试后的结果（成功 200 或仍失败 401）。")
# client fixture 的好处？（对比每个用例自己 ApiClient(...)）
print("pytest 自动造好 client 注入用例，所有测试文件直接用 —— \
      不用每个用例自己 ApiClient(...)；改环境地址只改 conftest 一处。")
# 写代码：数据驱动 —— 从 users.json 读 3 组数据参数化登录断言 code
with open("data/users.json", "r", encoding="utf-8") as f:
    USERS = json.load(f)
@pytest.mark.parametrize("case", USERS)
def test_login_cases(client, case):
    assert client.login(case["user"], case["pwd"]).json()["code"] == case["expect_code"]
# 思考题：框架里还有哪些环节可以 "自动"？（至少说 3 个，提示：报告 / 日志 / 失败重跑 / 环境切换）
print("报告自动生成（pytest-html，已会）、日志自动记录（失败 / 请求日志）、失败用例自动重跑、\
      环境自动切换（conftest 读配置）、token 自动刷新（今天已实现）、测试数据自动准备/清理（fixture teardown）、\
      CI 里失败自动通知（Day19 聊过）")