# ===== mock_server.py：本地假接口服务器 =====
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
            code = int(path.split("/")[-1])       # /status/404 → 404
            self._send(code, {"code": code})
        elif path == "/get":
            query = parse_qs(urlparse(self.path).query)
            self._send(200, {"args": {k: v[0] for k, v in query.items()}})
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, *args):                 # 静音，不刷屏
        pass

if __name__ == "__main__":
    print("mock 服务器启动: http://127.0.0.1:8000")
    HTTPServer(("127.0.0.1", 8000), MockHandler).serve_forever()