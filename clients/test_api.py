"""业务层：只负责具体接口用例需要的语义"""
from clients.http_session import HttpSession

class TestApi(HttpSession):
    def __init__(self, base_url, user="test", pwd="123"):
        super().__init__(base_url)#self 这个对象，请用父类 HttpSession 的初始化方法来初始化一遍，base_url 给你
        self.user = user
        self.pwd = pwd

    # ---------- 会话 ----------
    def login(self, user=None, pwd=None):
        """user/pwd 不传就用构造时的默认值"""
        user = user if user is not None else self.user
        pwd = pwd if pwd is not None else self.pwd
        resp = self.request("POST", "/login", auth=False,
                            json={"user": user, "pwd": pwd})
        self.token = resp.json().get("token")
        return resp

    def _request(self, method, path, **kwargs):
        """带认证的业务请求：懒登录 + 401 重登"""
        if not self.token:
            self.login()

        resp = self.request(method, path, **kwargs)

        if resp.status_code == 401:
            self.token = None
            self.login()
            resp = self.request(method, path, **kwargs)

        return resp

    # ---------- 业务接口 ----------
    def get_user(self):
        return self._request("GET", "/get_user")

    def get_order(self):
        return self._request("GET", "/get_order")

    def get_vip(self):
        return self._request("GET", "/get_vip")

    def echo(self, payload):
        return self._request("POST", "/echo", json=payload)