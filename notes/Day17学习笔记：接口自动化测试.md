# Day17 学习笔记：接口自动化测试

> 日期：2026-10-16
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第3周 · Day17
> 状态：✅ 全部完成（练习 3 题 + 自测 5 题通过）

---

## 一、接口自动化测试 = 请求 → 断言

```
requests.get(url, params=..., timeout=5)  →  resp 响应对象  →  assert 断言
```

**和 Day12 的区别**：Day12 是"打接口 + 打印结果 + 人眼看报告"；Day17 是"打接口 + assert 自动判定"。测试能不能过，机器说了算。

## 二、requests 响应对象三件套

```python
resp = requests.get(url, params={"name": "test"}, timeout=5)

resp.status_code   # 状态码（int 类型）：200 / 404 / 500
resp.json()        # 响应体解析成 Python 对象（dict / list）
resp.text          # 原始文本
```

## 三、核心写法

### 1. 参数化 + 状态码断言

```python
@pytest.mark.parametrize("path, expect", [
    ("/status/200", 200),
    ("/status/404", 404),
])
def test_http_status(base_url, path, expect):
    resp = requests.get(base_url + path, timeout=5)
    assert resp.status_code == expect
```

### 2. 带参数请求 + 内容断言

```python
def test_echo_param():
    resp = requests.get("http://127.0.0.1:8000/get",
                        params={"user": "test", "pwd": "123"}, timeout=5)
    assert resp.status_code == 200
    assert resp.json()["args"]["user"] == "test"   # 服务器回显参数
```

### 3. fixture 提供 base_url（环境切换雏形）

```python
@pytest.fixture
def base_url():
    """测试环境基础地址——换环境只改这里"""
    return "http://127.0.0.1:8000"
```

## 四、Mock 服务器（测开必备技能）

**为什么**：后端没好/外网不稳时，测试自己搭"假接口"。

```python
# mock_server.py —— 本地假接口服务器（标准库，无需装包）
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

class MockHandler(BaseHTTPRequestHandler):
    def _send(self, code, data=None):
        body = json.dumps(data or {}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith("/status/"):
            code = int(path.split("/")[-1])
            self._send(code, {"code": code})
        elif path == "/get":
            query = parse_qs(urlparse(self.path).query)
            self._send(200, {"args": {k: v[0] for k, v in query.items()}})
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    print("mock 服务器启动: http://127.0.0.1:8000")
    HTTPServer(("127.0.0.1", 8000), MockHandler).serve_forever()
```

**运行方式（两个终端）**：
- 终端1：`python mock_server.py`（保持运行）
- 终端2：`pytest test_day17.py -v`

## 五、今日错误复盘（重点）

### 🐛 坑1：URL 多拼一个 /get

```python
requests.get("https://httpbin.org/get" + path)   # ❌ → /get/status/200（路由不存在，404）
requests.get("https://httpbin.org" + path)       # ✅ → /status/200
```

### 🐛 坑2：参数凭空出现（Day16 坑复发）

```python
def test_http_status_homework2(path, expect):   # ❌ 没参数化却声明参数 → fixture not found
def test_http_status_homework2():               # ✅ 无参
```

**每个用例的参数来源必须靠它自己**：紧跟自己的 parametrize 装饰器，或同名 fixture。

### 🐛 坑3：装饰器只作用于紧贴的函数

```python
@pytest.mark.parametrize(...)   # ← 只管下面这个
def test_homework1(...):        # ✅ 被参数化
def test_homework2(...):        # ❌ 不受影响，普通用例
```

### 🐛 坑4：httpbin.org 国内访问不稳（网络层问题）

- 现象：`ReadTimeout`（5秒没回应）、`SSLError`（SSL 握手失败）
- 结论：**不是代码错，是网络问题**；外网不稳时换稳定靶场（本地 mock）

### ⚠️ 自测补充

- `resp.json()` 响应不是合法 JSON 会**抛 JSONDecodeError**（不是"响应错了"）
- `params={...}` 拼到 URL 的 `?` 后面 = HTTP 查询字符串（query string）

## 六、练习批改记录

| 项目 | 判定 |
|---|---|
| 练习1 参数化状态接口×4 | ⚠️→✅（URL 删 /get） |
| 练习2 带参数+内容断言 | ⚠️→✅（删 path/expect 参数） |
| 练习3 fixture base_url×2 | ✅ |
| 自测 5 题 | ✅（2 处补充） |

## 七、明日预告（Day18）

**conftest.py + 测试报告**
- conftest.py：fixture 全局共享（所有测试文件都能用，不用重复写）
- pytest-html：测试报告（企业汇报/CI 必备的漂亮 HTML 报告）
- 接口测试从"自己看"到"出报告给别人看"

---

*笔记由 AI 根据当日学习内容整理。*
