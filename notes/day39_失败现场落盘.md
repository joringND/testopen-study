# Day39 学习笔记：失败现场落盘——让报告自己带证据（第 7 周 Day3）

> 日期：2026-11-10
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 7 周 · Day39
> 状态：✅ 1 passed, 1 failed（--runxfail）；artifacts/test_fail_dump_20261110_232518.json 生成，490 字节
> 里程碑：失败自动留证——请求/响应/报错三样一次性落盘

---

## 一、今日目标

失败时证据都在本机（控制台 + `logs/run.log`）。用例挂了、报告发出去、三天后回看——证据不在手边。今天让**失败自动把"最后一次请求 + 响应 + 报错"落成 JSON** 存进 `artifacts/`。

## 二、今日涉及文件

| 操作 | 文件 | 说明 |
|---|---|---|
| 【修改】 | `api_client.py` | `__init__` 加 `self.last_exchange = None`；`_log()` 末尾记录最近一次交换 |
| 【修改】 | `conftest.py` | 补 `import os / datetime / logging`；新增 `pytest_runtest_makereport` 钩子 |
| 【新建】 | `day39_homework.py` | 1 条通过用例 + 1 条 xfail 演示失败 |
| 【新增目录】 | `artifacts/` | 由 `os.makedirs(exist_ok=True)` 自动创建 |

## 三、机制链

```
用例执行（call 阶段）→ 断言失败
        ↓
pytest_runtest_makereport 拦截（hookwrapper）
        ↓
item.funcargs["client"] → client.last_exchange
        ↓
artifacts/{用例名}_{时间戳}.json
        ↓
日志输出「失败现场已保存: ...」
```

**一句话**：pytest 在报告生成前给你一次拦截机会，抓住它就能留证。

## 四、代码改动

### 4.1 api_client.py

`__init__` 里（`self.session = requests.Session()` 附近）：

```python
        self.last_exchange = None      # 最近一次请求/响应，供失败落盘
```

`_log()` 末尾追加：

```python
    def _log(self, method, path, resp, cost):
        logger.info(f"{method} {path} -> {resp.status_code} {cost}ms")
        if cost > 500:
            logger.warning(f"{method} {path} -> {resp.status_code} {cost}ms 慢请求")
        logger.debug(f"resp={resp.text[:200]}")
        # ↓ 留存最近一次交换
        req = resp.request
        self.last_exchange = {
            "method": method,
            "path": path,
            "url": req.url if req is not None else None,
            "req_body": str(req.body)[:500] if req is not None else None,
            "status": resp.status_code,
            "resp_text": resp.text[:2000],
            "cost_ms": cost,
        }
```

**两个细节**：

- `resp.request` 是 requests 的 `PreparedRequest`——真正发出去的那份，URL 已拼好、body 已编码，比手记的 `path` 更可信
- `req.body` 可能是 **bytes**（表单/上传），`json.dump` 遇 bytes 直接 `TypeError`，所以 `str()` 包裹后再截断

### 4.2 conftest.py

顶部 import 补充：

```python
import os
import datetime
import logging

logger = logging.getLogger(__name__)
```

文件末尾新增：

```python
ARTIFACT_DIR = "artifacts"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败时，把最后一次请求/响应落盘到 artifacts/"""
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
    path = f"{ARTIFACT_DIR}/{safe}_{ts}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "test": item.nodeid,
            "error": str(report.longrepr)[:1000],
            "last_exchange": exchange,
        }, f, ensure_ascii=False, indent=2)

    logger.info(f"失败现场已保存: {path}")
```

### 4.3 day39_homework.py（新建）

```python
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
```

运行：

```powershell
& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pytest day39_homework.py -v --runxfail
```

## 五、实际落盘证据（真实产物）

```json
{
  "test": "day39_homework.py::test_fail_dump",
  "error": "day39_homework.py:15: in test_fail_dump\n    assert data[\"age\"] == 28, f\"实际年龄是 {data['age']}\"\nE   AssertionError: 实际年龄是 27\nE   assert 27 == 28",
  "last_exchange": {
    "method": "GET",
    "path": "/get_user",
    "url": "http://127.0.0.1:8000/get_user",
    "req_body": "None",
    "status": 200,
    "resp_text": "{\"code\": 0, \"name\": \"张三\", \"age\": 27}",
    "cost_ms": 1
  }
}
```

**这份证据的价值**：`status: 200` + `resp_text` 里 `age: 27` + `error` 是断言 28 ≠ 27——**接口是好的，断言写错了**。这类失败占日常一半，有现场一眼分清，没现场只能重跑猜。

运行日志也把时间线摆出来：

```
23:25:17 INFO api_client: POST /login -> 200 4ms
23:25:18 INFO api_client: GET /get_user -> 200 1ms
23:25:18 INFO conftest: 失败现场已保存：artifacts/test_fail_dump_20261110_232518.json
FAILED
```

**请求成功 → 断言失败 → hook 落盘**，三步各自留痕。

## 六、五个关键设计决策

| 代码 | 为什么 |
|---|---|
| `@pytest.hookimpl(hookwrapper=True)` + `yield` | 要等 pytest 把 `report` 造好才能读 `failed` / `longrepr`；直接 return 会被框架覆盖 |
| `report.when != "call"` | setup 挂 = fixture 问题（没发请求可存）；teardown 挂 = 用例本身其实过了 |
| `item.funcargs.get("client")` | 从已注入的 fixture 实例取证据；用例没写 client 参数就跳过 |
| `os.makedirs(exist_ok=True)` | 首次自动建目录；不加 `exist_ok` 第二次跑会抛 `FileExistsError` |
| `item.name.replace("[","_")` | 参数化用例名含 `[case0]`，**Windows 文件名不允许方括号**，不替换会写失败 |

## 七、今日坑

### 1. `log_file_encoding` 不是 pytest 8 的选项

```
PytestConfigWarning: Unknown config option: log_file_encoding
```

Day38 给出的这条配置在 pytest 8.4.2 **不生效**——pytest 8 的日志文件默认 UTF-8，无需也无法用 ini 指定。删掉该行即可。**配置项写错不会报错，只会静默忽略 + 警告**（CI 加 `-W error` 会直接构建失败）。若要自定义编码，只能自己挂 `logging.FileHandler(path, encoding="...")`。

### 2. `item.name` 不能直接当文件名

参数化后是 `test_x[case0]`，方括号在 Windows 路径里非法。必须过滤 `[` `]` `/` `\`。

### 3. `req.body` 可能是 bytes

上传/表单请求的 body 是 `bytes`，`json.dump` 遇 bytes 抛 `TypeError: Object of type bytes is not JSON serializable`。`str()` 包一层。

### 4. 用例没发请求就失败会怎样

`exchange is None` → 直接 return，不落盘。所以 `__init__` 里 `self.last_exchange = None` 的初始化是**显式声明状态**：区分"从未发过请求"和"属性不存在"，也避免后续直接访问时报 `AttributeError`。

## 八、练习答案

**1. 文件名带环境**

```python
    env = item.config.getoption("--env")
    path = f"{ARTIFACT_DIR}/{safe}_{env}_{ts}.json"
```

hook 里不能注入 fixture，但可以走 `item.config` 拿命令行参数。

**2. 没发过请求就失败**

`client.last_exchange` 为 `None` → 跳过落盘，不会生成空文件。初始化 `None` 是为了让"从未请求"有明确默认值，避免属性缺失导致的 `AttributeError`。

**3. `str(report.longrepr)[:1000]` 为什么截断**

fail 的 longrepr 含完整堆栈 + 参数化数据，可能几 KB 到几十 KB；不截断会让每个证据文件膨胀，报告也放不下。1000 字符足够看清错误类型与关键行。

## 九、自测答案

**1. `report.when` 的三种值**

`setup`（fixture 准备阶段）/ `call`（用例体执行）/ `teardown`（清理阶段）。

**2. 为什么用 `hookwrapper=True`**

钩子要在 pytest 生成 `report` 之后才能读到结果；`hookwrapper` 用 `yield` 把控制权先交回框架，结束后再取 `outcome.get_result()`。

**3. 为什么只在 call 阶段落盘**

setup 失败说明 fixture 挂了，用例体根本没执行、也没发请求，没有现场可存；teardown 失败时用例本身是通过的，记录它反而误导。

**4. `resp.request` 是什么**

requests 的 `PreparedRequest`——最终被发送的那一份：URL 已拼接、body 已编码、headers 已生成。比用例里手拼的 path 更接近服务端实际收到的内容。

**5. 文件名安全化**

```python
safe = item.name.replace("[", "_").replace("]", "").replace("/", "_").replace("\\", "_")
```

## 十、明日预告（Day40）

把 `artifacts` 的路径和失败日志一起嵌进 HTML 报告（pytest-html 的 `extras`），再用 `run_tests.bat` 一键全量跑 + 自动打开报告。

---

*笔记由 AI 根据当日学习内容整理。*
