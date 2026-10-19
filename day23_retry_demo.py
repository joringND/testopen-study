# 练习5（核心验证：401 自动重试）：
#   import requests 手动登录一次拿 token-A（最新）→ 再手动登录一次（LATEST 变 token-B）
#   → 此时用 ApiClient 请求 get_user（它会用自己缓存的旧 token）→ 第一次 401 → 自动重新登录 → 重试成功
#   验证方式：打印第一次响应和最终响应的状态码（应看到 401 → 200），断言最终 data["name"] == "张三"
# day23_retry_demo.py —— 亲眼看到 401 → 自动重试 → 200
import requests
from api_client import ApiClient

# 1. 建 client 并登录，缓存一个 token
client = ApiClient("http://127.0.0.1:8000")
client.login()
print("client 缓存的 token:", client.token)        # 比如 token-1

# 2. 模拟"token 被别人刷新了"：手动登录一次 → 最新 token 变了
requests.post("http://127.0.0.1:8000/login",
              json={"user": "test", "pwd": "123"}, timeout=5)
print("外部登录了一次（最新 token 已变）")

# 3. 先用 session 手动带"旧 token"请求 → 应该是 401
resp_old = client.session.get(
    "http://127.0.0.1:8000/get_user",
    headers={"Authorization": f"Bearer {client.token}"},
    timeout=5,
)
print("旧 token 请求状态码:", resp_old.status_code)   # 401（证明已过期）

# 4. 再用 client.get_user() → _request 自动重新登录 + 重试 → 最终 200
data = client.get_user().json()
print("client.get_user() 最终结果:", data)           # {'code': 0, 'name': '张三', 'age': 27}
assert data["name"] == "张三"