import requests
import pytest
from my_tools import check_status

# base_url 来自 conftest.py，直接用
@pytest.mark.parametrize("path,expect",[
    ("/status/200",200),
    ("/status/404",404),
    ("/status/500",500)
])
def test_status(base_url,path,expect):
    resp=requests.get(base_url+path,timeout=5)
    assert resp.status_code==expect

#结合 check_status 断言（Day12 的工具 + pytest）
@pytest.mark.parametrize("status_code,expect",[
    (200, "通过"),
    (404, "接口不存在"),
    (500, "服务器错误"),
])
def test_check_status(status_code,expect):
    assert check_status(status_code)==expect

#生成 HTML 报告
#"C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pytest day18_test.py --html=report.html --self-contained-html
# --html=report.html：生成 HTML 报告文件
# --self-contained-html：把样式打包进单文件（发别人也能打开）

# 练习1：把 Day17 的 base_url 迁移到 conftest.py（上面第2步已做）
# 然后 test_day18.py 里用 base_url 打 mock 接口（上面第3步已做）
# 跑通确认

# 练习2：写一个 fixture check_client 返回 requests 模块（假装是"测试客户端"）
# @pytest.fixture
# def check_client():
#     return requests
# 用例：def test_baidu(check_client):
#     resp = check_client.get("http://127.0.0.1:8000/status/200", timeout=5)
#     assert resp.status_code == 200
def test_baidu(check_client):
    resp=check_client.get("http://127.0.0.1:8000/status/200",timeout=5)
    assert resp.status_code==200
# 练习3：故意写错一个断言（比如 expect 写成 201），生成报告
# 跑 --html=report.html --self-contained-html
# 打开报告，观察失败用例怎么显示，然后改回正确再跑一次
@pytest.mark.parametrize("path,expect",[
    ("/status/200",200)
])
def test_check_status_homework3(base_url,path,expect):
    resp=requests.get(base_url+path,timeout=5)
    assert resp.status_code==expect

# conftest.py 需要 import 吗？pytest 怎么找到它？
print("conftest.py不需要import，pytest 启动时自动加载")
# conftest.py 里定义的 fixture，其他测试文件怎么用？
print("只需在conftest.py写一次，所有测试文件直接用")
# --html=report.html 和 --self-contained-html 各是什么作用？
print("--html=report.html要求以report.html的格式生成报告文件，\
      --self-contained-html把样式打包进单文件（发别人也能打开）")
# 写一个 fixture make_token：return "token123"，再写用例断言它 == "token123"
def test_check_token(make_token):
    assert make_token=="token123"
# 写一个参数化用例：3 组 (status, expect)，结合 conftest 里的 base_url 打 mock 接口断言状态码
@pytest.mark.parametrize("status,expect",[
    (200, "通过"),
    (404, "接口不存在"),
    (500, "服务器错误"),
])
def test_check_status_practice(base_url,status,expect):
    resp=requests.get(base_url+"/status/"+str(status),timeout=5)
    assert check_status(resp.status_code)==expect