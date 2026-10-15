#参数化：一条用例，N组数据
import pytest
from my_tools import check_status

# 以前：复制粘贴 3 遍
# def test_status_200(): assert check_status(200) == "通过"
# def test_status_404(): assert check_status(404) == "接口不存在"
# def test_status_500(): assert check_status(500) == "服务器错误"

#参数化：1个函数+3组数据
@pytest.mark.parametrize("status,expect",[
(200,"通过"),
(404,"接口不存在"),
(500,"服务器错误"),
(403,"其他异常"),
])
def test_status(status,expect):
    assert check_status(status)==expect

import pytest
# ===== fixture：测试环境的准备与清理 =====
@pytest.fixture
def test_data():
    print("\n[准备]构造测试数据")
    data=[
        {"name":"登录","status":200},
        {"name":"下单","status":200},
        {"name":"支付","status":500},
    ]
    yield data #yield前=准备：yield把数据交给用例
    print("[清理]删除测试数据") #用例跑完运行

# ===== 用例：参数名 = fixture 函数名，自动注入 =====
def test_count(test_data):
    assert len(test_data)==3

def test_has_failure(test_data):
    status_list=[c["status"] for c in test_data]
    assert 500 in status_list
#参数化 + fixture 结合
@pytest.mark.parametrize("name,status",[
    ("登录",200),("支付",500),
])
def test_case(test_data,name,status):
    # fixture 提供数据，参数化提供不同断言
    assert check_status(status) in ["通过","接口不存在","服务器错误","其他异常"]
    