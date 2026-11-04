import json
import requests
import pytest
BASE="http://127.0.0.1:8000"

def load_cases():
    """收集阶段执行：读 json 返回登录场景列表"""
    with open("data/login_cases.json","r",encoding="utf-8") as f:
        return json.load(f)["login_cases"]

@pytest.mark.parametrize("case",load_cases())
def test_login_ddt(case):
    resp=requests.post(f"{BASE}/login",
                        json={"user":case["user"],"pwd":case["pwd"]},
                        timeout=5)
    assert resp.status_code==case["expected"],f"{case}"

# 在 login_cases.json 里再加一组 {"user": "vip", "pwd": "wrong", "expected": 401}，重跑后用例数变几条？
print('5条')
# 为什么不能把 load_cases() 放进用例函数内部 for 循环测？一句话、
print('for 循环 = 1 条用例跑 N 遍（失败即停、无法定位）；parametrize = N 条独立用例（隔离、逐条报告）\
      先挂先停：第 1 组数据断言失败 → 整个函数抛错终止 → 后面 3 组测不到\
      报告无法定位：失败了显示 test_login_loop 一行，看不出是哪组数据挂的（[case2] admin 还是 [case3] wrong？）\
      脏了状态，影响后面')
# @pytest.mark.parametrize 和 @pytest.fixture(params=...) 的区别？
print('''
          @pytest.fixture(params=[...])    @pytest.mark.parametrize("参数名", 数据列表)
参数怎么进	 request.param	                 直接作为函数参数
作用对象	fixture（准备阶段）	               用例（执行阶段）
跑几次	     params 长度	                  数据列表长度
''')
# parametrize 的数据（load_cases()）什么时候执行？文件不存在会怎样？
print('load_cases() 是在收集阶段执行的,文件不存在会报错')
# 数据驱动的好处？（一句话）
print('方便管理和改动用例，实现数据与代码分离')
# 写代码：parametrize 3 组 (user, pwd, expected) 测登录（不读 json，直接写列表）
@pytest.mark.parametrize("user,pwd,expected",[
    ("test","123",200),
    ("vip","123",200),
    ("admin","123",401),
])
def test_login_homework(user,pwd,expected):
    resp=requests.post(f"{BASE}/login",
                       json={"user":user,"pwd":pwd},
                       timeout=5)
    assert resp.status_code==expected
# login_cases.json 里加一组数据，用例会自动多跑一条吗？为什么？
print('会自动多跑一条。parametrize 在收集阶段把数据列表展开成用例，数据组数 = 用例条数，\
      所以加一组数据 → 自动多一条 [case4]，不用改任何代码。')
