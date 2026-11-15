"""报告与证据：失败落盘 + extras 内嵌 + 终端汇总"""
import datetime
import html as html_lib
import json
import logging
import os

import pytest
from pytest_html import extras

from support.paths import ARTIFACT_DIR, LOG_DIR

logger = logging.getLogger(__name__)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败时：落盘 JSON + 把证据嵌进 HTML 报告"""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    client = item.funcargs.get("client")
    exchange = getattr(client, "last_exchange", None) if client else None
    if exchange is None:
        return

    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = item.name.replace("[", "_").replace("]", "").replace("/", "_")
    path = os.path.join(ARTIFACT_DIR, f"{safe}_{ts}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "test": item.nodeid,
            "error": str(report.longrepr)[:1000],
            "last_exchange": exchange,
        }, f, ensure_ascii=False, indent=2)

    logger.info(f"失败现场已保存: {path}")

    extra_list = getattr(report, "extras", [])
    escaped = html_lib.escape(json.dumps(exchange, ensure_ascii=False, indent=2))
    extra_list.append(extras.html(
        "<div style='font-size:12px;'>"
        "<strong>失败现场</strong>"
        f"<pre style='white-space:pre-wrap;margin:6px 0 0 0;'>{escaped}</pre>"
        "</div>"
    ))
    report.extras = extra_list


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """跑完在控制台末尾打印证据数量"""
    if os.path.isdir(ARTIFACT_DIR):
        files = [f for f in os.listdir(ARTIFACT_DIR) if f.endswith(".json")]
        terminalreporter.write_line(f"artifacts 目录共 {len(files)} 个证据文件")