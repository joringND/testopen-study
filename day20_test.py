#判断题（说理由）：
# pytest 用例没有 assert 会怎样？（假通过）
print("pytest 用例没有 assert 会不执行断言，造成用例的假通过")
# @pytest.mark.parametrize 3 组数据生成几条用例？装饰器只作用于哪个函数？
print("生成3条用例，装饰器只作用于它下面的第一个函数")
# pytest -s 的作用？pytest 默认怎么处理 print？
print("pytest -s 的作用输出捕获，用来展示print内容，pytest默认只在用例失败的时候展示print")
# 填空题：
# 4. conftest.py 需要 import 吗？它定义的 fixture 其他测试文件怎么用？
print("conftest.py不需要import，它定义的fixture在pytest启动时自动调用，其他测试文件会自动读取")
# 5. fixture 里 yield 前和 yield 后分别什么时候执行？fixture 可以 return 哪些类型？
print("yield前在用例执行前执行，yield后在用例执行后执行;\
      fixture可以return fixture 可以 return 任意类型：字符串、数字、字典、列表、元组、对象（模块 /requests）、函数、None…… 返回什么由用例需要什么决定")
# 代码题（写完整代码，运行验证）：
# 6. 参数化用例：check_status 3 组数据断言（200→"通过"、404→"接口不存在"、500→"服务器错误"）
import pytest
import requests
from my_tools import check_status
@pytest.mark.parametrize("status,expect",[
    (200,"通过"),
    (404,"接口不存在"),
    (500,"服务器错误"),
])
def test_check_status(status,expect):
    assert check_status(status)==expect
# 7. fixture make_token：return "token123"，写用例断言它 == "token123"
def test_check_token(make_token):
    assert make_token=="token123"
# 8. 用 pytest 测试 safe_divide：正常除法断言 + pytest.raises(ZeroDivisionError) 除零
def safe_divide(a, b):
    if b == 0:
        raise ZeroDivisionError("除数不能为0")
    return a / b

# 正常除法 → 断言结果
def test_safe_divide_ok():
    assert safe_divide(10, 2) == 5          # ✅ 有 assert

# 除零 → 断言"应该抛异常"
def test_safe_divide_error():
    with pytest.raises(ZeroDivisionError):   # ✅ 预期异常
        safe_divide(10, 0)
# 9. 打 mock 接口：参数化 3 组 (path, expect)，结合 conftest 的 base_url 断言状态码
@pytest.mark.parametrize("path,expect",[
    ("/status/200",200),
    ("/status/201",201),
    ("/status/404",404),
    ("/status/500",500),
])
def test_check_status_code(base_url,path,expect):
    resp=requests.get(base_url+path,timeout=5)
    assert resp.status_code==expect
# 10. 说理题：为什么 "打印统计结果" 的代码不能放模块顶层？（pytest 执行机制）
print("pytest 启动时先 import 文件（收集阶段）再跑用例。顶层代码在 import 时就执行。\
      此时用例一条都没跑，所以依赖用例结果的代码（统计、全局列表）放顶层必然报错或为空。")
