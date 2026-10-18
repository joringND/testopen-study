# mock_server.py —— 升级版：支持 POST + 登录态 + JSON
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    # 统一发 JSON 响应
    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

    # ===== GET 接口 =====
    def do_GET(self):
        # 保留旧功能：/status/<code>
        if self.path.startswith("/status/"):
            code = int(self.path.split("/")[-1])
            self._send(code, {"code": code, "msg": "status ok"})
        # 需要登录态：header 里带 Bearer token123 或 cookie 里带 token=token123
        elif self.path == "/get_user":
            auth = self.headers.get("Authorization", "")
            cookie = self.headers.get("Cookie", "")
            if auth == "Bearer token123" or "token=token123" in cookie:
                self._send(200, {"code": 0, "name": "张三", "age": 27})
            else:
                self._send(401, {"code": 401, "msg": "未登录"})
        else:
            self._send(404, {"code": 404, "msg": "not found"})

    # ===== POST 接口 =====
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if self.path == "/login":
            if body.get("user") == "test" and body.get("pwd") == "123":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Set-Cookie", "token=token123")   # 登录成功 → 种 cookie
                self.end_headers()
                self.wfile.write(json.dumps(
                    {"code": 0, "token": "token123", "msg": "登录成功"},
                    ensure_ascii=False).encode("utf-8"))
            else:
                self._send(401, {"code": 401, "msg": "账号或密码错误"})
        elif self.path == "/echo":
            self._send(200, {"code": 0, "echo": body})              # 回显收到的 JSON
        else:
            self._send(404, {"code": 404, "msg": "not found"})

    # 去掉默认的请求日志噪音
    def log_message(self, *args):
        pass

if __name__ == "__main__":
    print("mock_server v2 已启动: http://127.0.0.1:8000")
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()