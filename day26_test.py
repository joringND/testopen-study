# 1. 同一个 requests.Session() 登录后，再发 GET 为什么不用手动带 token/cookie？
print("答案：session 内部有 cookie jar，登录响应 Set-Cookie 后后续请求自动携带")

# 2. token 和 cookie 是一个东西吗？区别是什么？
print("答案：cookie = 浏览器侧键值存储（自动带）；token = 服务端签发的凭证（手动放 Authorization 头）。\
      我们的框架走 Authorization，mock 的 Set-Cookie 只是保留")

# 3. 第一次调用 client.get_user() 之前没有手动 login，为什么能成功？
print("答案：代码中写到当self.token is None时，会先执行login(),这就是懒登录")
# 4. fixture 默认作用域是____；每个用例拿到的 client 是____（同一个/不同）对象。
print('答案：fixture默认作用域是"function"（函数级）—— 但这里的 function 不是 "第一个函数"，而是 "每个测试函数 / 用例级别"，\
      每个用例执行前，pytest 都重新创建一次 fixture。每个用例拿到的 client 是不同对象，（互不串数据）')

# 5. 跑 python -m pytest -m "not smoke"，会选中哪些用例？
print("答案：会选中所有没有带上smoke标记的用例，包括其他标记以及未被标记的用例")

# 6. 写 fixture base_url：从 config/env.json 读 test 环境的地址（完整代码）
import pytest
import json
ENV="test"
@pytest.fixture
def base_url():
    with open("config/env.json","r",encoding="utf-8")as f:
        envs=json.load(f)
        return envs[ENV]
# 7. 数据驱动：3 组登录数据 (test/123→0) (test/wrong→401) (admin/123→401)，参数化断言 code
@pytest.mark.parametrize("name,pwd,expect_code",[
    ("test","123",0),
    ("test","wrong",401),
    ("admin","123",401)
])
def test_login_ok(client,name,pwd,expect_code):
    resp=client.login(name,pwd)
    assert resp.json()["code"]==expect_code
# 8. 定义 Calculator 类（__init__ 存 name，add(a,b) 返回 a+b），造对象断言 add(1,2)==3
class Calculator:
    def __init__(self,name):
        self.name=name
    def add(self,a,b):
        return a+b
def test_add():
    calc=Calculator("计算器")
    assert calc.add(1,2)==3
# 9. 为什么 mock_server.py 每次改代码后必须重启？不重启会怎样？
print("答案：因为serve_forever 跑的是启动那一刻的代码。它启动时是按照最后一次保存的代码进行配置，\
      当代码改动后，之前已启动的配置不会更改。为了新改动生效，必须重启")

# 10. 要给框架新加一个接口 /get_orders，需要改哪些文件？分别改什么？
print("""
答案：需要改3处文件，首先api_client.py添加改动：
def get_orders(self):
    return self._request("GET","/get_orders")
    其次，mock_server.py在do_get方法下添加
    elif self.path == "/get_orders":
        auth = self.headers.get("Authorization", "")
        if auth == f"Bearer {LATEST_TOKEN}":
            self._send(200, {"code": 0, "order_id": "ORD-1001", "amount": 99.9})
        else:
            self._send(401, {"code": 401, "msg": "token 过期或未登录"})
    最后，在执行的用例文件中添加：
    def test_get_order_after_login(client):
    client.login("test","123")
    data=client.get_orders().json()
    assert data["order_id"]=="ORD-1001"
    """)