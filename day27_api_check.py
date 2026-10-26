#查看接口完整返回
# day27_api_check.py —— 专门"看接口返回"的调试脚本
import requests

resp = requests.post("http://127.0.0.1:8000/login",json={"user": "test", "pwd": "123"}, timeout=5)
token = resp.json()["token"]
print(resp.json())
print(resp.json().keys())

# ② 带 token 查用户（认证接口必须带 Authorization 头）
resp2 = requests.get("http://127.0.0.1:8000/get_user",
                     headers={"Authorization": f"Bearer {token}"}, timeout=5)
print("get_user 返回:", resp2.json())
print("get_user keys:", resp2.json().keys())