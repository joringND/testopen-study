# api_client.py —— 接口框架核心：自动认证 + 401 自动重试
import requests
class ApiClient:
    def __init__(self,base_url,user="test",pwd="123"):
        self.base_url=base_url
        self.session=requests.Session()
        self.user=user
        self.pwd=pwd
        self.token=None #缓存的token（初始没有）

    #登录：从响应体拿token存起来
    def login(self,user=None,pwd=None):
        user = user if user else self.user      # 传了就用传入的，没传用对象默认的
        pwd = pwd if pwd else self.pwd
        resp=self.session.post(
            f"{self.base_url}/login",
            json={"user":user,"pwd":pwd},
            timeout=5,
        )
        if resp.status_code==200:
            self.token=resp.json()["token"] #存token
        return resp
    # 核心方法：所有请求走这里（自动带 token + 401 重试）
    def _request(self,method,path,**kwargs):
        if self.token is None:   #没token——>先登录
            self.login()
        headers=kwargs.pop("headers",{})
        headers["Authorization"]=f"Bearer {self.token}"#自动带token

        resp=self.session.request(method,f"{self.base_url}{path}",headers=headers,**kwargs)

        if resp.status_code==401:    #token过期
            self.login()             #重新登录（换新token）
            headers["Authorization"]=f"Bearer {self.token}"
            resp=self.session.request(method,f"{self.base_url}{path}",headers=headers,**kwargs)#重试
        return resp #返回最终结果

    #业务方法：只描述"要调哪个接口"，认证交给 _request
    def get_user(self):
        return self._request("GET","/get_user")
    def get_order(self):
        return self._request("GET","/get_order")
    def get_vip(self):
        return self._request("GET","/get_vip")

client = ApiClient("http://127.0.0.1:8000")
client.get_user()  # 自动登录 + 自动带 token + 401 自动重试
# 全程不用管 login/headers/token
