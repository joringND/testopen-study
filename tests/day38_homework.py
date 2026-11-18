import logging
import pytest

logger=logging.getLogger(__name__)

def test_logger_exists():
    """logger带自己的名字，日志里能看出出处"""
    assert logger.name=="day38_homework"

def test_request_log_visible(client,caplog):
    """一次真实请求，应产生一条INFO日志（caplog抓取）"""
    caplog.set_level(logging.INFO,logger="api_client")
    resp=client.get_user()
    assert resp.status_code==200
    texts=[r.getMessage() for r in caplog.records]
    assert any("GET /get_user -> 200 " in t for t in texts),f"没抓到请求日志：{texts}"

@pytest.mark.xfail(reason='演示失败现场，配合-l 看局部变量')
def test_fail_show_locals(client):
    """故意失败，跑-l 时能看到data/resp的值"""
    resp=client.get_user()
    data=resp.json()
    logger.info(f"拿到用户数据：{data}")
    assert data["age"]==28,f"实际年龄{data['age']}"

def test_where_logs_go(client, caplog):
    caplog.set_level(logging.INFO, logger="api_client")
    client.get_user()
    logger.info("用例自己的日志")
    assert len(caplog.records) >= 2      # 内存里：login + get_user + 自己这条