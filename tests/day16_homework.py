import pytest
from my_tools import check_status
# 练习1：参数化 check_status
# 4 组数据：(200, "通过")、(404, "接口不存在")、(500, "服务器错误")、(403, "其他异常")
# 用 @pytest.mark.parametrize 实现，跑出 4 passed
@pytest.mark.parametrize("status,expect",[
(200,"通过"),
(404,"接口不存在"),
(500,"服务器错误"),
(403,"其他异常"),
])
def test_status(status,expect):
    assert check_status(status)==expect
# 练习2：参数化加法
# 3 组数据：(1, 2, 3)、(10, 20, 30)、(-1, 1, 0)
# 断言 a + b == expect
@pytest.mark.parametrize("a,b,expect",[
    (1,2,3),
    (10,20,30),
    (-1,1,0),
])
def test_plus(a,b,expect):
    assert a+b==expect
# 练习3：fixture 造数据 + 用例
# 写 fixture make_cases：返回 3 条用例字典（含 name/status）
# 用例1：断言 200 状态的用例数 >= 1
# 用例2：遍历 test_cases 断言所有 status 都在 [200, 404, 500, 201] 里
@pytest.fixture
def make_cases():
    print("\n[[准备]构造测试数据]")
    data=[
        {"name":"登录","status":200},
        {"name":"下单","status":200},
        {"name":"支付","status":500},
    ]
    yield data
    print("[清理]删除测试数据")

# 用例1：只依赖 fixture
def test_count_200(make_cases):
    count = 0
    for case in make_cases:
        if case["status"] == 200:
            count += 1
    assert count >= 1

# 用例2：遍历时取每个 case 的 status 字段
def test_cases(make_cases):
    for case in make_cases:              # 遍历每条用例字典
        assert case["status"] in [200, 404, 500, 201]

#@pytest.mark.parametrize("a, b", [(1, 2), (3, 4)]) 会生成几条用例？
print("会生成2条用例")
#参数化里第一个参数的 "a, b" 是什么？和函数参数什么关系？
print("参数化的第一个参数'a,b'指的是一组用例，代表传入函数的普通参数")
#fixture 里 yield 前和 yield 后分别什么时候执行？
print("yield前用例执行前把数据交给用例；yield后在用例执行后才执行")
#写一个参数化用例：3 组数据断言 n * 2 == expect（(1,2)、(3,6)、(5,10)）
@pytest.mark.parametrize("n,expect",[
    (1,2),
    (3,6),
    (5,10),
])
def test_double(n,expect):
    assert n*2==expect
#写一个 fixture make_user：yield 一个字典 {"name": "张三", "age": 27}，再写用例断言 age == 27
@pytest.fixture
def make_user():
    data=[
        {"name":"张三","age":27},
    ]
    yield data  #可以去掉data=[{"name":"张三","age":27}],
                #简写为yield {"name": "张三", "age": 27}直接交一个字典
    print("执行完成，清理数据")


def test_user(make_user):
    for user in make_user:
        assert user["age"]==27#直接传入字典后用assert make_user["age"] == 27，不用遍历