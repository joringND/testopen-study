# mock_server.py —— v3：token 会过期（只有最新 token 有效）
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

COUNTER = [0]           # 登录次数计数（列表是为了在函数里改全局）
LATEST_TOKEN = "token-0"

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        if self.path.startswith("/status/"):
            code = int(self.path.split("/")[-1])
            self._send(code, {"code": code, "msg": "status ok"})
        elif self.path == "/get_user":
            global LATEST_TOKEN
            auth = self.headers.get("Authorization", "")
            if auth == f"Bearer {LATEST_TOKEN}":      # 只认最新 token
                self._send(200, {"code": 0, "name": "张三", "age": 27})
            else:
                self._send(401, {"code": 401, "msg": "token 过期或未登录"})
        else:
            self._send(404, {"code": 404, "msg": "not found"})

    def do_POST(self):
        global LATEST_TOKEN, COUNTER
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if self.path == "/login":
            if body.get("user") == "test" and body.get("pwd") == "123":
                COUNTER[0] += 1
                LATEST_TOKEN = f"token-{COUNTER[0]}"    # 每次登录发新 token
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Set-Cookie", f"token={LATEST_TOKEN}")
                self.end_headers()
                self.wfile.write(json.dumps(
                    {"code": 0, "token": LATEST_TOKEN, "msg": "登录成功"},
                    ensure_ascii=False).encode("utf-8"))
            else:
                self._send(401, {"code": 401, "msg": "账号或密码错误"})
        elif self.path == "/echo":
            self._send(200, {"code": 0, "echo": body})
        else:
            self._send(404, {"code": 404, "msg": "not found"})

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    print("mock_server v3 已启动: http://127.0.0.1:8000（token 每次登录都换）")
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()