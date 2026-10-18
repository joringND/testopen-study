#ApiClient类的雏形
import requests

class ApiClient:
    # __init__：造对象时自动执行，把"属性"装好
    def __init__(self,base_url):
        self.base_url=base_url #属性1：地址（只写一次！）
        self.session=requests.session()# 属性2：会话（登录态自动带）
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

client=ApiClient("http://127.0.0.1:8000")  # 造一台"客户端机器人"，地址只填一次
client.login("test","123") # 登录（session 自动存 cookie）
data=client.get_user().json()# 查用户（自动带 cookie）
print(data["name"])# 张三

class Dog:                       # class + 类名（首字母大写）
    def __init__(self,name,age):# 造对象时自动执行
        self.name=name           # self.xxx = 对象的属性
        self.age=age
    def bark(self):              # 方法必须带 self（第一个参数）
        return "汪汪"

dog=Dog("旺财",3)# 造对象 → __init__ 自动跑 → dog.name = "旺财"
print(dog.bark())# 汪汪
# __init__ 不需要你调 ——Dog(...) 时就自动执行
# 方法里第一个参数永远是 self（表示 "我自己"），调用时不用传
# 不写 __init__ 的类也能用，但对象就没有 "开工装属性" 这一步（属性得手动加）