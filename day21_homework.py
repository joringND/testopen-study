# 练习1：POST 登录成功
# POST http://127.0.0.1:8000/login，json={"user": "test", "pwd": "123"}
# 断言：status_code == 200、data["code"] == 0、data["token"] == "token123"
import requests
def test_login_ok():
    resp=requests.post("http://127.0.0.1:8000/login",json={"user": "test", "pwd": "123"},timeout=5)
    data=resp.json()
    assert resp.status_code==200
    assert data["code"]==0
    assert data["token"]=="token123"
# 练习2：POST 登录失败
# 用错误密码 {"user": "test", "pwd": "wrong"}
# 断言：status_code == 401、data["code"] == 401、data["msg"] == "账号或密码错误"
def test_login_fail():
    resp=requests.post("http://127.0.0.1:8000/login",json={"user": "test", "pwd": "wrong"},timeout=5)
    data=resp.json()
    assert resp.status_code==401
    assert data["code"]==401
    assert data["msg"]=="账号或密码错误"
# 练习3：headers 认证
# GET http://127.0.0.1:8000/get_user，headers={"Authorization": "Bearer token123"}
# 断言：data["code"] == 0、data["name"] == "张三"
# 再加一个反例：不带 header 请求 → 断言 status_code == 401
def test_login_headers():
    resp=requests.get("http://127.0.0.1:8000/get_user",headers={"Authorization": "Bearer token123"},timeout=5)
    data=resp.json()
    assert data["code"]==0
    assert data["name"]=="张三"

def test_login_headers_fail():
    resp=requests.get("http://127.0.0.1:8000/get_user",timeout=5)
    assert resp.status_code==401
# 练习4：session 会话
# session 登录 → 用同一个 session 请求 /get_user → 断言 name == "张三"（不手动带 token）
def test_session():
    s=requests.Session()
    resp=s.post("http://127.0.0.1:8000/login",json={"user":"test","pwd":"123"},timeout=5)
    resp2=s.get("http://127.0.0.1:8000/get_user",timeout=5)
    data=resp2.json()
    assert data["name"]=="张三"

# 练习5：参数化登录
# 3 组数据：(test,123)→code 0 / (test,wrong)→401 / (admin,123)→401
# 参数化 + 断言 data["code"]
import pytest
@pytest.mark.parametrize("name,pwd,code",[
    ("test","123",0),
    ("test","wrong",401),
    ("admin","123",401),
])
def test_check_code(name,pwd,code):
    resp=requests.post("http://127.0.0.1:8000/login",json={"user": name, "pwd": pwd},timeout=5)
    data=resp.json()
    assert data["code"]==code

# data= 和 json= 传数据有什么区别？
print("data=传表单字符串或字典以及Content-Type=application/x-www-form-urlencoded，适用于HTML表单\
      json=传字典或列表以及Content-Type=application/json，适用于接口测试")
# headers 一般用来传什么？（至少说 2 种）
print("headers一般用来传token和Content-Type")
# session 和 直接 requests.get 的区别？
print("session登录一次自动带cookie，并且连接采用复用方式，适用于同一用户的多步操作；\
      requests.get每次登录需要手动带cookie，并且连接采用每次新建的方式，适用于一次性请求")
# 写代码：POST /login 断言 code == 0（完整用例）
def test_login_code():
    resp=requests.post("http://127.0.0.1:8000/login",json={"user": "test", "pwd": "123"},timeout=5)
    data=resp.json()
    assert data["code"]==0
# 思考题（不写代码）：真实项目里，token 会过期，session 失效后怎么办？
print("真实项目里，token 会过期，如果单次获取token的有效期长，可以重新获取，填写后重新建立session；\
      若单次获取token的有效期断,需要编写token获取脚本每次session建立前自动获取token并填写")
#请求 → 返回 401（token 过期）
#    → 自动重新登录拿新 token
#    → 用新 token 重发刚才失败的请求
#    → 用例依然通过（用户无感）