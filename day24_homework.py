import json
import pytest
from api_client import ApiClient
#读场景数据（数据驱动）
with open("data/cases.json","r",encoding="utf-8") as f:
    CASES=json.load(f)
# 参数化：每条场景 = 一条用例（ids 给用例起中文名）
@pytest.mark.parametrize("case",CASES,ids=[c["user"]+"-"+c["pwd"] for c in CASES])
def test_login_scene(client,case):
    #① 登录断言（所有场景都测）
    resp=client.login(case["user"],case["pwd"])
    assert resp.json()["code"]==case["expect_code"]

    # ② 条件断言：登录成功才继续查用户、查订单
    if case["expect_code"]==0:
        if case["expect_name"] is not None:            # vip 场景为 null → 跳过
            assert client.get_user().json()["name"] == case["expect_name"]
        if case["expect_order"] is not None:           # 同理
            assert client.get_order().json()["order_id"] == case["expect_order"]
        assert client.get_vip().json()["is_vip"] == case["expect_vip"]
# 练习1：【修改】api_client.py —— 在 get_user() 方法后面加 get_order()
#   方法：get_order(self) → return self._request("GET", "/get_order")
print("已修改")
# 练习2：跑上面 day24_homework.py，确认 3 条用例全过（id 显示 test-123 等）
print("已跑通")
# 练习3：给 cases.json 加第 4 组场景（自己设计）：
#   比如：合法账号 + 故意写错 token 场景？——想一个真实场景加上去，跑通

# 练习4：给 mock 加 /get_vip（vip 用户接口：token 有效返回 {"code":0,"is_vip":true}）
#   然后 cases.json 加 expect_vip 字段 + 用例加 vip 断言
#   （提示：ApiClient 也要加 get_vip 方法——发现规律了吗？加接口=改3处：mock+数据+用例）
print("已跑通")
# 练习5（思考+验证）：如果 mock 的 /get_order 改成了 /get_orders（复数），
#   你要改几个文件？分别改哪里？（验证：全项目搜 get_order） 
print('改两个文件，mock_server.py：do_GET 里 elif self.path == "/get_order",改成 "/get_orders";\
      api_client.py:get_order() 方法里 return self._request("GET", "/get_order")改成 "/get_orders"')
# 数据驱动里 "一行数据" 应该包含什么？（用今天的话说）
print("一行数据应该包含一个完整的测试场景，包括输入+期望输出")
# 登录失败（401）时 client.token 是什么？此时查用户会怎样？（提示：懒登录）
print("登录失败（401）时 self.token 还是 None—— 因为 login() 只在 status_code == 200 时才存 token")
# fixture 默认作用域是什么？每个用例拿到的 client 是同一个对象吗？（为什么不会串数据）
print("fixture的默认作用域是函数级，每个用例重新创建client：独立对象、独立 session、独立 token\
      不串数据的原因：case1 登录成功的 token 只活在 case1 自己的 client 里；case2 拿到的是新 client\
      （token 还是 None）。\
      如果作用域是 session，所有用例共用一个 client，case2 登录失败会把 case1 的登录态弄乱 \
      —— 所以接口测试 client 默认 function 是对的")
# 写代码：从 cases.json 读数据 + 参数化 + 断言登录 code（完整用例）
import json
import pytest

with open("data/cases.json", "r", encoding="utf-8") as f:
    CASES = json.load(f)

@pytest.mark.parametrize("case", CASES, ids=[c["user"] + "-" + c["pwd"] for c in CASES])
def test_login_code(client, case):
    resp = client.login(case["user"], case["pwd"])
    assert resp.json()["code"] == case["expect_code"]
# 思考题：数据驱动后，新加一个测试场景要改几个文件？新加一个接口要改几个文件？为什么？       
print("加测试场景1 个（data/cases.json 加一行）数据驱动后场景 = 数据，代码零改动。\
      加接口3 个（mock 分支 + api_client 方法 + 数据 / 用例断言）行为在 mock、调用在 client、验证在用例")