#POST+json=参数：登录
import requests
resp=requests.post(
    "http://127.0.0.1:8000/login",
    json={"user":"test","pwd":"123"},#json= → 自动转 JSON + Content-Type: application/json
    timeout=5,
)
print(resp.status_code)#200
print(resp.json())#{'code': 0, 'token': 'token123', 'msg': '登录成功'}

#headers:带token访问需登录接口
resp=requests.get(
    "http://127.0.0.1:8000/get_user",
    headers={"Authorization":"Bearer token123"},#手动带头部
    timeout=5,
)
print(resp.status_code) #200（不带 header 会 401）
print(resp.json())# {'code': 0, 'name': '张三', 'age': 27}

#session：登录一次，自动带cookie
s=requests.Session()#建一个会话
resp=s.post("http://127.0.0.1:8000/login",json={"user":"test","pwd":"123"},timeout=5)
print(resp.json())#登录成功，服务器种下cookie:token=token123

#后续请求不用手动带 token —— session 自动带上 cookie
resp2=s.get("http://127.0.0.1:8000/get_user",timeout=5)
print(resp2.json())#{'code': 0, 'name': '张三', 'age': 27}

#json断言：不只看状态码，看响应体
resp=requests.post(
    "http://127.0.0.1:8000/login",
    json={"user":"test","pwd":"123"},
    timeout=5,
)
data=resp.json()                    # 响应体 → 字典
assert resp.status_code==200        # 1. HTTP 层
assert data["code"]==0              # 2. 业务码
assert data["token"]=="token123"    # 3. 具体字段

#三层断言：HTTP 状态码 → 业务 code → 关键字段 —— 这就是 "接口测试真的在测业务"。
