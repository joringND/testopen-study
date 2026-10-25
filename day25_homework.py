import json
import pytest
from api_client import ApiClient
@pytest.mark.smoke
def test_login_ok(client):
    resp=client.login("test","123")
    assert resp.json()["code"]==0

@pytest.mark.smoke
def test_login_wrong(client):
    resp=client.login("test","wrong")
    assert resp.json()["code"]==401

@pytest.mark.full
def test_get_user_after_login(client):
    client.login("test","123")
    data=client.get_user().json()
    assert data["name"]=="张三"

@pytest.mark.full
def test_get_order_after_login(client):
    client.login("test","123")
    data=client.get_order().json()
    assert data["order_id"]=="ORD-1001"
# 只跑 2 条冒烟    
# "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pytest -m smoke
# 跑除 full 外的        
# "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pytest -m "not full" 
# 只列用例不执行  
# "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pytest --co
# 区分：-m smoke 是 "选择标记"，-m 不要和 -m pytest 混淆 —— 前者是 pytest 的筛选参数，后者是 "以模块方式运行"

#skip = 门禁前置检查；函数体 = 检查后才轮到的执行；assert 写什么都影响不到跳过的判定。 
import sys
@pytest.mark.skipif(sys.version_info<(3,10),reason="需要Python3.10+的新特性")
def test_python_version_feature():
    assert True

@pytest.mark.skip(reason="该功能下版本才实现")
def test_not_implemented_yet():
    assert False   
#一条 SKIPPED (需要 Python 3.10+)（你的 Python 3.9 满足条件→跳过）
# 一条 SKIPPED (该功能下个版本才实现)—— 失败但跳过，报告不红。    

# pytest.ini 里 markers 注册是干嘛的？（不注册会怎样？）
print("markers用来注册自定义标记，消除PytestUnknownMarkWarning")
# -m smoke 和 -m "not smoke" 分别跑什么？
print("分别跑标记为冒烟的用例和非冒烟的用例，没打任何标记的也会被选中")
# 跳过（SKIPPED）和失败（FAILED）有什么区别？skipif 什么时候用？
print("skipped是跑不了的用例跳过不报错，failed是报错，跳过不等于失败。\
      skipif在需要判断跳过条件的时候使用，条件成立才跳过")
# 写代码：读 env.json 返回 base_url 的 fixture（完整可跑）
ENV="test"
@pytest.fixture
def base_url():
    with open("config/env.json","r",encoding="utf-8") as f:
        envs=json.load(f)
        return envs[ENV]
# 思考题：多环境切换的本质是什么？为什么 "地址查表" 比 "地址写死" 好？
print('多环境切换的本质是地址从代码抽离成配置数据,\
      地址查表让 "切环境" 变成 "改数据 / 改环境变量"，CI 也能用 TEST_ENV 覆盖')         