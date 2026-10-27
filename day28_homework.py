import pytest
import requests
from api_client import ApiClient
@pytest.mark.xfail(reason="已知bug:/get_orders 接口未实现")
def test_get_orders():
    resp=requests.get("http://127.0.0.1:8000/get_orders",timeout=5)
    data = resp.json()
    assert resp.status_code==200 # 现在会失败 → XFAIL（不算失败）
    assert data["code"] == 0, f"登录失败！实际返回: {data}"   # ← 失败时这个提示直接显示

# skip  → 用例根本不执行（我不测了）
# xfail → 用例照常执行，只是"结果早就知道"（测了，但知道会挂）    

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):  # 预期这段代码会抛异常
        1/0                                 # 没抛 → 用例失败
#接口测试里常用：预期非法参数时接口返回 401（一般用断言状态码；raises 用于 Python 层异常）。

@pytest.fixture()
def log_client(client):
    client.login("test","123")
    yield client
    client.token=None

def test_get_user(log_client):
    data = log_client.get_user().json()
    assert "name" in data.keys()# 返回里必须有 token 这个 key
    assert data["name"] == "张三"# 精确断言
    assert data["age"] == 27              # 顺手把 age 也断上

    # 想验证"登录成功、有 token"→ 查 client.token（login 时存的对象属性）
    assert log_client.token               # 登录成功会存下 token（非空即通过）
    assert "token" in log_client.token

# 练习1：xfail 基础 —— 一条故意失败的用例，标 xfail
@pytest.mark.xfail(reason="练习：故意失败验证 XFAIL")
def test_will_fail():
    assert 1 == 2

# 练习2：xfail + reason，和普通 FAILED 对比
def test_real_fail():                          # 不标 xfail → FAILED
    assert 1 == 2

# 练习3：断言加提示（故意失败看提示）
def test_assert_message():
    data = {"code": 0, "name": "张三"}
    assert data["name"] == "李四", f"名字不对！实际是: {data['name']}"
#机制：assert 失败 = 立即抛异常 = 函数当场终止
#assert 一旦不成立，立刻抛出 AssertionError 中断整个函数—— 第 2 行代码根本没机会运行，所以它的提示信息自然不打印
def test_assert_order_demo2():
    resp = requests.get("http://127.0.0.1:8000/get_orders", timeout=5)
    # assert resp.status_code == 200, "① 状态码不对"   ← 注释掉
    assert resp.json()["code"] == 0, "② 业务code不对"   # 这次能看到提示！

# xfail 和 skip 的区别是什么？（一句话）
print("""
skip  用例根本不执行（我不测了）
xfail 用例照常执行，只是"结果早就知道"（测了，但知道会挂）
""")
# XFAIL 和 XPASS 分别代表什么？strict=True 后 XPASS 会怎样？
print("""
XFAIL代表跑了但预期失败：已知bug或用例未实现
XPASS代表Xfail的用例竟然成功了。配 strict=True 后 XPASS 反而不被允许（说明 bug 已修，应摘掉 xfail）。
""")
# assert data["code"] == 0, f"...{data}" 逗号后面那段的作用？
print('作用是失败时提示会直接显示')
# pytest.raises 什么时候用？写一行用法示例
def test_divide_error():
    with pytest.raises(ZeroDivisionError):
        1/0
# 写代码：一条 /get_orders 用例，标 xfail (reason="接口未实现")（完整可跑）
@pytest.mark.xfail(reason="已知bug:/get_orders 接口未实现")
def test_get_orders():
    resp=requests.get("http://127.0.0.1:8000/get_orders",timeout=5)
    assert resp.status_code==200

def test_check_object():
    client = ApiClient("http://127.0.0.1:8000")
    print("client 的属性:", client.__dict__)#obj.__dict__（实例自己的属性字典，一行全列出）
    print("client 有哪些成员:", dir(client))#dir(obj)（连方法一起全列出，用 type() 先看是啥类型
    resp = requests.post("http://127.0.0.1:8000/login",
                         json={"user": "test", "pwd": "123"}, timeout=5)
    print("Response 类型:", type(resp))
    print("Response 成员:", dir(resp))
#记法：dir() 里能看到全部候选，但哪些是属性、哪些是方法，取决于它定义时有没有 () 调用
#属性是 "名字"，方法是 "动作"
#查数据用 .keys()；查对象属性看类定义里的 self.xxx 或 obj.__dict__；想全览用 dir(obj)；方法要加括号、属性不加
