import requests
import pytest

resp=requests.get("https://httpbin.org/get",params={"name":"zhangsan"},timeout=5)

resp.status_code #状态码：200/404/500
resp.json()   #响应体转字典/列表（必须是 JSON 格式）
resp.text     #原始文本
#httpbin.org/get 会把你的参数原样回显到 JSON 里（args 字段），是完美的测试靶场。

@pytest.mark.parametrize("path,expect",[
    ("/status/200", 200),
    ("/status/404", 404),
    ("/status/500", 500),
])
def test_http_status(path,expect):
    resp=requests.get("https://httpbin.org"+path,timeout=5)
    assert resp.status_code==expect

@pytest.mark.parametrize("name",["zhangsan","lisi","wangwu"])
def test_echo_param(name):
    resp=requests.get("https://httpbin.org/get",params={"name":name},timeout=5)
    assert resp.status_code==200
    assert resp.json()["args"]["name"]==name # 服务器回显参数 = 你传的参数

#fixture 管理 base_url（环境切换的雏形）
@pytest.fixture
def base_url():
    """测试环境基础地址——以后换成正式环境只改这里"""
    return "http://127.0.0.1:8000"
@pytest.mark.parametrize("path,expect",[
("/status/200", 200), ("/status/404", 404),
])
def test_status_fixture(base_url,path,expect):
    resp=requests.get(base_url+path,timeout=5)
    assert resp.status_code==expect

# 练习1：参数化 httpbin 状态接口
# 4 组：( "/status/200", 200 )、("/status/201", 201)、("/status/404", 404)、("/status/500", 500)
# 断言 resp.status_code == expect
BASE_URL = "http://127.0.0.1:8000"
@pytest.mark.parametrize("path,expect",[
    ("/status/200", 200),
    ("/status/201", 201),
    ("/status/404", 404),
    ("/status/500", 500),
    ])
def test_http_status_homework1(path,expect):
    resp=requests.get(BASE_URL+path,timeout=5)
    assert resp.status_code==expect
# 练习2：带参数请求 + 内容断言
# GET https://httpbin.org/get，params={"user": "test", "pwd": "123"}
# 断言 status_code == 200
# 断言 resp.json()["args"]["user"] == "test"
def test_http_status_homework2():
    resp=requests.get(BASE_URL+ "/get",params={"user": "test", "pwd": "123"},timeout=5)
    assert resp.status_code==200
    assert resp.json()["args"]["user"] == "test"
# 练习3：fixture 提供 base_url + 参数化
# 写 fixture base_url 返回 "https://httpbin.org"
# 参数化 2 组：( "/status/200", 200 )、("/status/503", 503)
# 用例里 requests.get(base_url + path, timeout=5) 并断言
@pytest.fixture
def base_url():
    return "http://127.0.0.1:8000"
@pytest.mark.parametrize("path,expect",[
    ( "/status/200", 200 ),
    ("/status/503", 503),
    ])
def test_http_status_homework3(base_url,path,expect):
    resp=requests.get(base_url + path, timeout=5)
    assert resp.status_code==expect

# resp.status_code 是什么类型？一般怎么判断接口成功？
print("resp.status_code是int类型，判断resp.status_code是否等于200")
# resp.json() 返回什么类型？如果响应不是 JSON 会怎样？
print("resp.json() 返回字典或列表，如果响应不是json会导致用例报错，\
      遇到这种情况，先 resp.text 看原始内容，确认接口到底返回了什么")
# params={"name": "test"} 传的是什么？对应 HTTP 的什么位置？
print('params 对应 HTTP 的 "查询字符串"，params 会把字典拼到 URL 的 ? 后面—— 这就是它的 "HTTP 位置"。')
# 写用例：GET https://httpbin.org/get，断言 status_code == 200
def test_status_https():
    resp=requests.get("https://httpbin.org/get",timeout=5)
    assert resp.status_code==200
# 写参数化用例：3 组 (path, expect) 断言状态码（200/404/500）
@pytest.mark.parametrize("path,expect",[
    ("/status/200", 200),
    ("/status/404", 404),
    ("/status/500", 500)
    ])
def test_status_https_practice(path,expect):
    resp=requests.get("https://httpbin.org"+path,timeout=5)
    assert resp.status_code==expect