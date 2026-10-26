import pytest

#参数化 fixture：params 里的每个值，fixture 都生成一次
@pytest.fixture(params=["test","vip","admin"])
def account(request):
    return request.param #request.param=当前这一轮的值

#这条用例会自动跑3次（每个account一次）
def test_account_type(account):
    assert isinstance(account,str)
    print(f"\n当前账号：{account}")

@pytest.fixture
def per_case():
    print("\n[function]每个用例都初始化")
    yield "case-data"
    print("\n[function]每个用例都清理")

@pytest.fixture(scope="module")
def per_module():
    print("\n[module]整个文件只初始化一次")
    yield "module-data"
    print("[module]整个文件只清理一次")

def test_a(per_case,per_module):
    print("per_case 的值是:", per_case)        # 会打印: per_case 的值是: case-data
    print("per_module 的值是:", per_module)    # 会打印: per_module 的值是: module-data

def test_b(per_case,per_module):
    pass

from api_client import ApiClient

@pytest.fixture
def logged_client(client):
    client.login("test", "123")        # setup：用例前登录
    yield client                       # 用例在这里执行（拿到已登录的 client）
    client.token = None                # teardown：用例后清登录态（避免影响下一条）

def test_after_login(logged_client):
    data = logged_client.get_user().json()
    assert data["name"] == "张三"

@pytest.fixture(params=["test", "vip"])
def logged_client_v2(request, client):
    client.login(request.param, "123")      # setup：登录不同账号（参数化）
    yield client
    client.token = None                     # teardown

def test_after_login_v2(logged_client_v2):
    data = logged_client_v2.get_user().json()
    assert data["name"] == "张三"           # 两个账号都能查用户（mock 里 test/vip 都能登录）

# 练习1：参数化 fixture —— 3 组账号跑通（知识点1）
# 练习2：作用域对比 —— 观察 function/module 打印次数（知识点2）
# 练习3：logged_client —— 登录+清理前后置（知识点3），跑通断言
# 练习4（进阶）：把 logged_client 改成参数化 fixture：
#   params=["test","vip"]，每条用例自动登录不同账号再查数据
#   提示：request.param 当账号，client.login(request.param, "123")

# @pytest.fixture(params=[...]) 是干嘛的？request.param 是什么？
print('是用来参数化fixture，使用一个fixture生成多组数据。request.param 拿当前参数')
# 参数化 fixture 一条用例会跑几次？
print('params 列表里有几个值，用例就跑几次')
# scope="module" 和 scope="session" 的区别？什么时候用 module？
print('scope="module"指定该fixture一个文件只建一次；scope="session"指定该fixture整个测试会话只建一次；\
      读一次大文件或启动一次服务时可以使用scope="module"。')
# yield 前和 yield 后的代码分别在什么时候执行？（说一个真实场景）
print('yield前的代码在用例执行前执行，yield的代码在用例执行后执行，真实场景如：登录——用-清理')
# 写代码：登录 + 清理的 fixture（完整可跑，yield 前后置）
from api_client import ApiClient
@pytest.fixture()
def log_client(client):
    client.login("test","123")
    yield client
    client.token=None
