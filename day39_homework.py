import pytest


def test_pass_no_dump(client):
    """通过的用例不该产生 artifacts 文件"""
    resp = client.get_user()
    assert resp.status_code == 200


@pytest.mark.xfail(reason="故意失败，演示失败现场落盘")
def test_fail_dump(client):
    """失败用例应生成 artifacts/*.json"""
    resp = client.get_user()
    data = resp.json()
    assert data["age"] == 28, f"实际年龄是 {data['age']}"

# 文件名带环境：让文件名变成 test_fail_dump_test_2026xxxx.json（提示：hook 里没有 fixture 可注入，用 item.config.getoption("--env")）
print("""
    env = item.config.getoption("--env")
    path = f"{ARTIFACT_DIR}/{safe}_{env}_{ts}.json"
""")
# 没发过请求的失败：如果一条用例纯做数据校验就失败（client 一次没调），hook 会落盘什么？为什么 __init__ 里要初始化 last_exchange = None？
print('`client.last_exchange` 为 `None` → 跳过落盘，不会生成空文件。' \
'初始化 `None` 是为了让"从未请求"有明确默认值，避免属性缺失导致的 `AttributeError`')
# 截断理由：str(report.longrepr)[:1000] 为什么要截断？不截会怎样？
print('fail 的 longrepr 含完整堆栈 + 参数化数据，可能几 KB 到几十 KB；' \
'不截断会让每个证据文件膨胀，报告也放不下。1000 字符足够看清错误类型与关键行')
# 六、AI 自测 5 题
# pytest_runtest_makereport 的 report.when 有哪三种值？分别代表什么？
print('`setup`（fixture 准备阶段）/ `call`（用例体执行）/ `teardown`（清理阶段）')
# 为什么要用 hookwrapper=True，不能直接 def pytest_runtest_makereport(item, call) 返回 report？
print('钩子要在 pytest 生成 `report` 之后才能读到结果；' \
'`hookwrapper` 用 `yield` 把控制权先交回框架，结束后再取 `outcome.get_result()`')
# 为什么只在 call 阶段落盘，setup 阶段失败不用存？
print('setup 失败说明 fixture 挂了，用例体根本没执行、也没发请求，没有现场可存；\
      teardown 失败时用例本身是通过的，记录它反而误导。')
# resp.request 是什么对象？它比你自己记的 URL 可靠在哪？
print('requests 的 `PreparedRequest`——最终被发送的那一份：\
      URL 已拼接、body 已编码、headers 已生成。比用例里手拼的 path 更接近服务端实际收到的内容。')
# 写代码：把 item.name 转成安全的文件名（参数化用例 test_x[case0] 不能直接当文件名）
print("""
safe = item.name.replace("[", "_").replace("]", "").replace("/", "_").replace("\\", "_")
""")