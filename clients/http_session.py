"""传输层：只负责发请求、记录一次请求/响应交换"""
import logging
import time

import requests

logger = logging.getLogger(__name__)


class HttpSession:
    def __init__(self, base_url, timeout=5):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.token = None
        self.last_exchange = None

    def _log(self, method, path, resp, cost_ms):
        """记录一次交换。字段照你现有 _log 的实现抄，不要改字段名"""
        record = {
            "method": method,
            "path": path,
            "url": resp.request.url,
            "req_body": str(resp.request.body)[:500],
            "status": resp.status_code,
            "resp_text": resp.text[:1000],
            "cost_ms": cost_ms,
        }
        self.last_exchange = record
        level = logging.WARNING if cost_ms > 500 else logging.INFO
        logger.log(level, f"{method} {path} -> {resp.status_code} {cost_ms}ms")

    def request(self, method, path, auth=True, **kwargs):
        """纯传输：拼 URL、按需带 token、计时、记交换"""
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        start = time.time()
        resp = self.session.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
        cost_ms = int((time.time() - start) * 1000)
        self._log(method, path, resp, cost_ms)
        return resp
# 两个要点：
# timeout 变成构造参数（默认 5），以后换环境不用改代码里的字面量
# auth=True 是「要不要带 token」的开关，login 会传 auth=False——传输层不判断 “这是登录接口”，只认参数