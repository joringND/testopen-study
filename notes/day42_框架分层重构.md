# Day42 学习笔记：框架分层重构（conftest 拆成三个插件）

> 日期：2026-11-15
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 8 周 · 第 1 天
> 主题：把混在根 conftest 里的六种职责拆成 support/ 下三个插件
> 验收：全量 `48 passed, 2 skipped, 7 xfailed in 2.78s`（与拆分前完全一致）

---

## 一、今天解决了什么

拆分前，`conftest.py` 一个文件里同时装着六种职责：

| # | 内容 | 性质 |
|---|---|---|
| 1 | `pytest_addoption` 注册 `--env` | 参数入口 |
| 2 | `env_name` / `base_url` | 配置类 fixture |
| 3 | `client`（及 `check_client` / `make_token`） | 客户端 fixture |
| 4 | `ARTIFACT_DIR = "artifacts"` | 路径常量 |
| 5 | `pytest_runtest_makereport` | 报告钩子（落盘 + extras） |
| 6 | `pytest_terminal_summary` | 终端汇总 |

问题不在"行数多"，而在**改一处要通读全篇**：调日志格式得翻过所有 fixture，加个环境得在三个 fixture 之间找，新人打开 conftest 看不出这个框架有哪些能力。

拆分后，conftest 退化成一张**装配清单**，能力按职责分家。

**关键边界：今天只拆 `conftest.py`，一个用例文件都没动。**
11 个 `dayXX_homework.py` 若挪进 `tests/`，会牵连 `import api_client`、`data/*.json` 相对路径、`pytest.ini` 的 `testpaths`、bat 里的文件名列表——一次改六个变量，风险过高。目录迁移留到框架稳定后（Day45 左右）。

---

## 二、分层前后对比

```
拆分前                              拆分后
┌────────────────────────┐         ┌─────────────────────────────┐
│ conftest.py (~100 行)  │         │ conftest.py                 │
│  · pytest_addoption    │         │  pytest_plugins = (         │
│  · env_name            │   ──→   │    "support.env_config",    │
│  · base_url            │         │    "support.api_fixtures",  │
│  · client              │         │    "support.reporting",     │
│  · ARTIFACT_DIR        │         │  )                          │
│  · makereport hook     │         └─────────────────────────────┘
│  · terminal_summary    │                       │
└────────────────────────┘                       ↓
                                    ┌─────────────────────────────┐
                                    │ support/                    │
                                    │  paths.py      常量         │
                                    │  env_config.py 参数+配置    │
                                    │  api_fixtures.py 客户端     │
                                    │  reporting.py   钩子+证据   │
                                    └─────────────────────────────┘
```

| 维度 | 拆分前 | 拆分后 |
|---|---|---|
| 改日志格式 | 通读 conftest 找到 hook | 只开 `reporting.py` |
| 加一个环境 | 在三个 fixture 间定位 | 只开 `env_config.py` |
| 知道框架有什么能力 | 逐行读 | 看 conftest 三行清单 |
| 一个新 fixture 放哪 | 随手加进 conftest | 按依赖关系归位 |

---

## 三、目标结构与依赖方向

```
testopen-study/
├── conftest.py                 ← 只留装配清单
├── support/
│   ├── __init__.py             ← 空文件，声明为包
│   ├── paths.py                ← 所有路径常量
│   ├── env_config.py           ← --env + env_name + base_url
│   ├── api_fixtures.py         ← client 等 fixture
│   └── reporting.py            ← 落盘钩子 + extras + 终端汇总
├── api_client.py               ← 不动
├── config/env.json             ← 不动
├── day25~39_homework.py        ← 全部不动
└── run_tests.bat               ← 不动
```

**依赖方向必须单向：**

```
paths（无依赖）
  ← env_config
        ← api_fixtures
              ← reporting
```

箭头方向 = "被谁依赖"。`reporting.py` 要读 `client.last_exchange`，所以它依赖 `api_fixtures`；反向绝不成立。一旦 `api_fixtures` 反过来 import `reporting`，就是循环依赖，早晚崩。

---

## 四、五个文件的完整内容

### 4.1 `support/__init__.py`

```python
# 框架支撑模块包
```

空文件即可，作用是让 `support` 成为**包**，从而能用 `support.env_config` 这种带包名的模块路径导入。

### 4.2 `support/paths.py`

```python
"""所有路径常量的唯一出处"""
import os

# support/ 的上一级 = 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_PATH = os.path.join(BASE_DIR, "config", "env.json")
ARTIFACT_DIR = os.path.join(BASE_DIR, "artifacts")
LOG_DIR = os.path.join(BASE_DIR, "logs")
```

**为什么用 `__file__` 推导绝对路径**：原来写 `"config/env.json"` 是相对**当前工作目录**，只有在项目根目录执行 pytest 才有效。用 `BASE_DIR` 拼出来，从任何目录跑都不会找错文件。

`dirname` 两次的含义：`__file__` → `support/paths.py`；第一次 `dirname` → `support/`；第二次 → 项目根。

### 4.3 `support/env_config.py`

```python
"""环境配置：--env 参数 + 环境相关 fixture"""
import json

import pytest

from support.paths import CONFIG_PATH


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="test", help="环境: test/pre")


@pytest.fixture(scope="session")
def env_name(request):
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def base_url(env_name):
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    assert env_name in cfg, f"环境 {env_name} 不存在，可选 {list(cfg.keys())}"
    return cfg[env_name]
```

**只有三个东西：`pytest_addoption` / `env_name` / `base_url`。没有独立的 `env_config` fixture。**

读 json 和 `assert env_name in cfg` 都在 `base_url` 内部——这是你的真实结构，本次拆分**只搬位置、不改逻辑**。

### 4.4 `support/api_fixtures.py`

```python
"""客户端类 fixture"""
import pytest

from api_client import ApiClient


@pytest.fixture
def client(base_url):
    return ApiClient(base_url)
```

`check_client` / `make_token` 若存在，一并放在此文件——判断规则是**依赖 `base_url` 或 `ApiClient` 的 fixture 都属于这一层**。

### 4.5 `support/reporting.py`

```python
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
```

### 4.6 `conftest.py`（最终形态）

```python
"""根 conftest：只做装配，实现都在 support/ 下。"""

pytest_plugins = (
    "support.env_config",
    "support.api_fixtures",
    "support.reporting",
)
```

`pytest_plugins` 是 pytest 的特殊变量，**不需要 import pytest**。

---

## 五、迁移映射表

| conftest 原内容 | 去向 | 备注 |
|---|---|---|
| `import os / json / datetime / logging / html as html_lib` | 按需分到各文件 | 谁用谁 import，不再共享一份 |
| `from pytest_html import extras` | `reporting.py` | 只有它用 |
| `from api_client import ApiClient` | `api_fixtures.py` | 只有它用 |
| `logger = logging.getLogger(__name__)` | `reporting.py` | 名字会变成 `support.reporting` |
| `ARTIFACT_DIR = "artifacts"` | `paths.py` | 改成绝对路径 |
| `pytest_addoption` | `env_config.py` | 必须由插件承载 |
| `env_name` / `base_url` | `env_config.py` | `base_url` 内含读 json + assert |
| `client` / `check_client` / `make_token` | `api_fixtures.py` | 依赖 base_url 的都在此层 |
| `pytest_runtest_makereport` | `reporting.py` | 钩子必须躺在插件里才生效 |
| `pytest_terminal_summary` | `reporting.py` | 同上 |

---

## 六、今天两次翻车复盘

### 翻车 1：我虚构了一个不存在的 fixture

**现象**：任务卡里我给出 `env_config` fixture，用户立刻指出"我的 conftest.py 里本来就没有 env_config"。

**真实结构**：读 json + assert 都在 `base_url` 内部，没有中间层。

**根因**：我按"常见三件套写法"补了一个 fixture，而不是照用户的真实代码拆。这是**教学里最不该犯的错**——拆分的前提是"原样搬家"，虚构结构等于让人按假图纸施工。

**修正**：`env_config.py` 只保留三段（addoption / env_name / base_url），`base_url` 内部逻辑一字不改。

**延伸判断：现在不要引入 `env_config` 中间层**

有人会建议"把读 json 拆成独立 fixture，让 base_url 只取值"——现在别做：

1. 只有 `base_url` 一个消费方，拆出来是多一层转发
2. 拆开后 `base_url` → `env_config` → `env_name`，链路变长，排查多跳一步
3. **等出现第二个也要读 cfg 的 fixture 时再拆**（比如读 `timeout`、`verify_ssl`）

结构与 Day37 同一条原则：**结构跟着需求长，不跟着想象长**。

### 翻车 2：`NameError` → INTERNALERROR 整场崩溃

**现象**：

```
conftest.py, line 94, in pytest_runtest_makereport
    logger.info(f"失败现场已保存：{path}")
NameError: name 'logger' is not defined
```

连第一轮的 `1 passed` 结果都没输出。

**当时的真实状态（半拆状态）**：

| 文件 | hook | logger | 结果 |
|---|---|---|---|
| `support/reporting.py` | ✅ 有 | ✅ 有 | 正常，但**未被加载**（`pytest_plugins` 未含它） |
| `conftest.py` | ✅ 还在第 68 行 | ❌ 第 24 行被注释 | 💥 一跑就崩 |

**根因两条，是叠加的**：

1. **直接原因**：conftest 第 24 行 `#logger=logging.getLogger(__name__)` 被注释掉了，但第 68 行的 hook 还在用它
2. **放大器**：`reporting.py` 里已经有一份完整 hook，但没被 `pytest_plugins` 声明，所以没注册；conftest 那份被注册了却缺依赖

**为什么升级成 INTERNALERROR**：异常发生在 `pytest_runtest_makereport` 这个**全局钩子**内部，异常冒泡到 `wrap_session` → pytest 判定框架自身出错 → 整个 session 中断。pytest-html 的 wrapper 先捕获到该异常，所以 traceback 里能看到 `pytest_html/plugin.py` 那一层。

**正确顺序：先建新、后接线、最后删旧**

```
① 写 reporting.py（定义 + 使用一起写全）   → 两份 hook 并存，能跑
② conftest 加 pytest_plugins 三行           → 第二份开始生效
③ 立刻删 conftest 里的 hook 段             → 只剩 reporting.py 那份
```

**"删一半"比"完全没删"更危险**——它让框架处于既不能跑、也看不出缺什么的状态。

**安全的删法：先复制、后删除、每删一段跑一次**

1. 新文件写完 → 跑一次（两处并存，功能重复但能跑）
2. 从 conftest 删一段 → 立刻跑 `day37_homework.py`（最快验证 fixture 还在）
3. 再删下一段 → 再跑
4. 全删完 → 跑全量

**别一次删完再跑**——出问题时不知道是哪一段删坏的。

### 两个错误层级对照

| 出错位置 | 影响范围 | pytest 报什么 |
|---|---|---|
| 用例体（assert 失败） | 一条用例 | `FAILED`，其余照跑 |
| fixture（setup 抛错） | 一条用例 | `ERROR`，其余照跑 |
| **hook（makereport 内抛错）** | **整个 session** | **`INTERNALERROR`，全部结果丢失** |

hook 是"全局拦截器"，不是"单条逻辑"——所以里面的代码要格外小心。

---

## 七、三条必踩的坑

| 坑 | 现象 | 处置 |
|---|---|---|
| `pytest_plugins` 写进非根 conftest | `Defining 'pytest_plugins' in a non-top-level conftest is no longer supported` | 只允许写在项目根的 conftest |
| 漏了 `support/__init__.py` | `ModuleNotFoundError: No module named 'support.env_config'` | 补空 `__init__.py` |
| 钩子写在普通模块却只 `import` 进 conftest | 报告里静默没有证据，**不报错** | 用 `pytest_plugins` 声明，让模块成为 plugin |

第三条最隐蔽：`from support.reporting import pytest_runtest_makereport` 这种写法**有时看起来也能跑**（因为 pytest 会扫描 conftest 模块成员），但 hook 的注册时机和扫描范围都不确定，属于"靠运气生效"。**官方唯一推荐的方式是 `pytest_plugins`**。

**为什么不用 `from ... import *`**：

1. 显式声明依赖，一眼看得出加载了哪些能力
2. 避免名字意外进入 conftest 命名空间，导致 hook 重复注册
3. 加插件只需在清单里加一行，不用改 import 结构

---

## 八、验收证据

### 8.1 单文件验证

```
day39_homework.py::test_pass_no_dump    PASSED
day39_homework.py::test_fail_dump      FAILED
INFO support.reporting: 失败现场已保存: ...\artifacts\test_fail_dump_20261115_210802.json
artifacts 目录共 22 个证据文件
1 failed, 1 passed in 0.20s
```

三个关键信号：

| 信号 | 含义 |
|---|---|
| 日志前缀 `support.reporting:` | `logger = logging.getLogger(__name__)` 里的 `__name__` 变成了 `support.reporting`，证明 hook 是在插件模块里执行，而非 conftest |
| `失败现场已保存` 正常打印 | hook 拿到了 `client.last_exchange`，落盘链路完整 |
| `artifacts 目录共 22 个证据文件` | `pytest_terminal_summary` 同样在插件里生效 |

### 8.2 全量验证

```
48 passed, 2 skipped, 7 xfailed in 2.78s
```

与拆分前完全一致 → 搬家没有破坏任何功能。**成绩不变，就是分层的验收标准。**

### 8.3 一个操作细节

直接跑 `python -m pytest --html=...` **不会自动打开报告**。自动打开只发生在 `run_tests.bat` 里的 `start "" %REPORT%`。手动跑要自己 `start report_check.html`。

---

## 九、自测 5 题与参考答案

**Q1. 日志前缀从 `api_client:` 变成 `support.reporting:`，证明了什么？**

`logging.getLogger(__name__)` 的 `__name__` 是**模块名**。hook 现在住在 `support/reporting.py`，所以 logger 名变成 `support.reporting`。日志前缀变了 = hook 的执行位置变了 = 插件化成功。

（附带价值：以后看日志就能知道一条记录是哪个模块打的。）

**Q2. 报 `INTERNALERROR` 而不是 `1 failed`，根因是"两份 hook 并存"还是"缺 logger"？**

**直接原因是缺 `logger`**（那一份 hook 缺运行时依赖），**"两份并存"是放大器**（让这个坏 hook 成为唯一被注册的那份）。

如果只有一份 hook 且缺 logger，症状**一样是 INTERNALERROR**——因为异常发生在 hook 内部，与是否有第二份无关。

**Q3. 为什么 hook 里一个 `NameError` 能摧毁整场 session？**

pytest 调用 hook 时没有把异常"降级"成用例失败的机制。用例体里的异常由 `runtestprotocol` 捕获并转成 `report.failed = True`；但 hook 本身抛异常 → 冒泡到 `wrap_session` → pytest 认为框架自己坏了 → `INTERNALERROR`，直接放弃整场。

**Q4. 举一个"以后改需求因此变简单"的例子。**

需求：落盘文件名加环境前缀（`pre_` 前缀）。

改动只需 `reporting.py` 一处：

```python
env = item.config.getoption("--env")
path = os.path.join(ARTIFACT_DIR, f"{env}_{safe}_{ts}.json")
```

**总共 2 行，只碰 reporting.py，不动 conftest、不动任何用例。** 拆分前则要在 100 行的 conftest 里找到 hook、确认没有别的 fixture 依赖同名变量。

**Q5. 在 `D:\` 下执行 `python -m pytest D:\...\day37_homework.py`，还能读到 `config/env.json` 吗？**

**能。** 因为 `CONFIG_PATH` 由 `os.path.abspath(__file__)` 推导，是绝对路径，与实际工作目录无关。

若沿用原来的 `"config/env.json"`，则会因为工作目录是 `D:\` 而找不到文件 → `FileNotFoundError`。这就是"常量集中 + 绝对路径"的实际收益。

---

## 十、本日结论

| 项 | 结论 |
|---|---|
| 技术目标 | ✅ 达成：conftest 从 ~100 行降到 3 行装配清单 |
| 功能回归 | ✅ 全量 48 passed / 2 skipped / 7 xfailed，与拆分前一致 |
| 最大收获 | 理解"钩子是全局拦截器"——它出错不是一条用例失败，而是整场崩溃 |
| 最大教训 | 拆分不是"写新文件"，是"**搬依赖**"：定义和用它的代码必须同进同出 |
| 遗留待办 | `artifacts` 已累计 22 个文件，需要治理（按日期分目录 / 保留最近 N 个） |

---

## 十一、下一步（Day43 预告）

**主题：`api_client.py` 也要分层——把「HTTP 传输」和「业务接口」分开**

现在 `ApiClient` 一个类里同时做三件事：

1. 发请求（`session.post/get`、超时、重试）
2. 记日志（`_log()`、`last_exchange`）
3. 写业务（`login()`、`get_user()`、`get_order()`）

Day43 会拆成：

```
clients/http.py     → HttpSession：只会发请求 + 记 exchange
clients/api.py      → TestApi：只会写业务（login / get_user / get_order）
```

**为什么这一步重要**：等你以后要测真实流媒体服务时，业务接口会从 5 个涨到 50 个，而 HTTP 传输层基本不变。不拆开，`api_client.py` 会变成第二个 conftest。

**预习问题**（明天开课先答）：

1. `_log()` 现在写在 `ApiClient` 里，它记录的是"传输层信息"还是"业务层信息"？
2. 如果拆成两个类，`client = ApiClient(base_url)` 这行 fixture 要怎么改，才能让 11 个用例文件**一行都不用动**？
