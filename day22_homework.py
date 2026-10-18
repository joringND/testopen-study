# 练习1：定义 Dog 类（name/age 属性 + bark() 返回"汪汪"），造对象调用，打印 bark()
class Dog:
    def __init__(self,name,age):
        self.name=name
        self.age=age
    def bark(self):
        return "汪汪"
dog=Dog("旺财",3)
print(dog.bark())    
# 练习2：定义 User 类（name/age），方法 introduce() 返回 "我叫xxx，今年xx岁"，造对象断言返回
class User:
    def __init__(self,name,age):
        self.name=name
        self.age=age
    def introduce(self):
        return f"我叫{self.name}，今年{self.age}岁"
def test_user_introduce():    
    user = User("张三", 27)
    assert user.introduce() == "我叫张三，今年27岁"
# 练习3：定义 ApiClient 类（照上面核心代码抄一遍，理解每一行）
#   加一个方法：echo(data) → POST /echo 回显 → 返回 resp
import requests
class ApiClient:
    # __init__：造对象时自动执行，把"属性"装好
    def __init__(self,base_url):
        self.base_url=base_url #属性1：地址（只写一次！）
        self.session=requests.Session()# 属性2：会话（登录态自动带）
    #方法1：登录（行为）
    def login(self,user,pwd):
        resp=self.session.post(
            f"{self.base_url}/login",
            json={"user":user,"pwd":pwd},
            timeout=5,
        )
        return resp
    #方法2：查用户（行为）
    def get_user(self):
        resp=self.session.get(f"{self.base_url}/get_user",timeout=5)
        return resp
    #方法3：echo(data) → POST /echo 回显 → 返回 resp
    def echo(self,data):
        resp=self.session.post(f"{self.base_url}/echo",json=data,timeout=5)
        return resp
# 练习4：用 ApiClient 写一条 pytest 用例：
#   client = ApiClient("http://127.0.0.1:8000")
#   client.login("test", "123") → get_user() → 断言 data["name"] == "张三"
#   （提示：get_user 的 session 已经自动带 cookie，不需要手动 header）
def test_api_client_data_name():
    client=ApiClient("http://127.0.0.1:8000")
    client.login("test", "123")
    data=client.get_user().json()
    assert data["name"]=="张三"
# 练习5：把练习4 的用例改成参数化：3 组 (user, pwd, expect_code)
#   (test,123,0) / (test,wrong,401) / (admin,123,401)
#   断言 client.login(user, pwd).json()["code"] == expect_code
import pytest
@pytest.mark.parametrize("user,pwd,expect_code",[
    ("test","123",0),("test","wrong",401),("admin",123,401),
])
def test_api_client_check_code(user,pwd,expect_code):
    client=ApiClient("http://127.0.0.1:8000")
    data=client.login(user,pwd).json()
    assert data["code"]==expect_code
# 类和对象的区别？（一句话）
print("类是生成对象的模板（图纸），对象是模板造出的实例（实物）。类不包含对象，一个类能造出无数对象")
# __init__ 什么时候执行？self 是什么？
print("__init__：造对象时自动执行，把属性装好,self是对象自己的名字，方法里靠它访问自己的属性")
# 不写 __init__ 的类能用吗？对象创建后属性从哪来？
print("不写 __init__ 的类可以用，对象创建后属性需要手动加")
# 写代码：定义 Calculator 类：__init__(self, name)，方法 add(a, b) 返回 a+b；
# 造对象 calc = Calculator("我的计算器")，断言 calc.add(1, 2) == 3
class Calculator:
    def __init__(self,name):
        self.name=name
    def add(self,a,b):
        return a+b
def test_calc():
    calc=Calculator("我的计算器")
    assert calc.add(1,2)==3
# 思考题：ApiClient 封装后，mock 地址从 8000 改成 8001，你要改几处？为什么？
print('只需改一处，ApiClient("http://127.0.0.1:8001")')