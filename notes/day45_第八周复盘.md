# Day45 学习笔记：第八周复盘（框架分层验收）

> 日期：2026-11-24
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 8 周 · 第 4 天（复盘日）
> 范围：Day42 装配层拆分 + Day43 客户端分层 + Day44 目录迁移
> 成绩：初考 **79** → 补考 **93** → **通过**

---

## 一、复盘结构

10 题、每题 10 分、70 分及格，闭卷（Q3 允许开 `conftest.py` 现场诊断）。

| 题型 | 题号 | 考什么 |
|---|---|---|
| 概念 | Q1–Q2 | 三插件拆分、hook 崩溃机制 |
| 现场诊断 | Q3 | 读自己的 conftest，找重复定义 |
| 分层 | Q4–Q6 | `super()`、401 归层、签名兼容 |
| 目录与收集 | Q7–Q9 | `pythonpath`、两套收集规则、清单式代价 |
| 综合 | Q10 | 新项目脚手架（从零设计目录与配置） |

---

## 二、成绩单

| 题 | 内容 | 初考 | 补考 |
|---|---|---|---|
| Q1 | 三插件职责 / `pytest_plugins` 必须顶层 | 10 | — |
| Q2 | hook 异常为何整场崩 | 8 | — |
| Q3 | 两处同名 `client` 谁生效 | 8 | — |
| Q4 | `super().__init__` 的两批属性 | 8 | — |
| Q5 | 401 重登为何留业务层 | 10 | — |
| Q6 | 签名兼容清单 | 6 | **10** |
| Q7 | `pythonpath` 的 `.` 相对谁 | 10 | — |
| Q8 | 给文件 vs 给目录 | 10 | — |
| Q9 | 清单式三重代价 + xfail 根因 | 6 | **10** |
| Q10 | 新项目脚手架 | 3 | **6** |
| **合计** | | **79** | **93** |

---

## 三、逐题批改

### 3.1 Q2：差“为什么不能降级”那一层

初考答“异常冒泡到 `wrap_session` → 判定框架自身出错 → 整个 session 中断”，方向对，缺关键机制：

> **用例的失败有“承载者”，hook 的异常没有。**

用例执行时异常被 `call_and_report` 捕获，装进 `TestReport`，变成 `failed`。而 `pytest_runtest_makereport` 本身就是**在造这个 TestReport 的环节**——它在造“报告”，自己却崩了，没有第二个对象能装下这个异常。异常只能一路冒到 `Session.wrap_session`，那里只有 `INTERNALERROR` 一个出口。

一句话对照：**fixture 崩了还能记成“用例 error”，hook 崩了连记录容器都没有。**

### 3.2 Q3：现场诊断题（本题最有价值）

`conftest.py` 与 `support/api_fixtures.py` 里各有一个 `def client(base_url)`。

| 子问 | 答案 |
|---|---|
| 用哪个 | **根 `conftest.py` 里的** |
| 依据 | conftest 的层级高于 `pytest_plugins` 加载的插件 |
| 实际危害 | 改插件的 `client` **静默不生效**，且不报错 |

**具体会踩的场景**：Day43 之后想给 `client` 加超时参数，改的是 `support/api_fixtures.py`，跑一遍发现完全没变——因为根 `conftest.py` 那个同名的盖住了。你会开始怀疑“插件没加载”“`pytest_plugins` 写错了”，查半小时才发现是两处同名。

这与 Day44 的“`pythonpath` 写错段、静默不生效”是同一类问题：**重复定义不会报错，只会让你的修改失效。**

### 3.3 Q4：错误发生点 ≠ 根因点

删掉 `super().__init__(base_url)` 后，`__init__` 本身**不报任何错**：`self.user = user`、`self.pwd = pwd` 照样赋值成功，函数正常返回。Python 不会在赋值阶段检查“你还有没有 `self.token`”。

错误**延迟**到第一次真正使用父类属性时才炸：

```
client.get_user() → _request() → if not self.token → AttributeError
```

根因在 `__init__`，报错在 `_request`，中间隔了两层。这类问题最难查，因为报错位置看起来完全无关。

### 3.4 Q6：签名的兼容判据（补考满分）

| 破坏兼容 | 不影响兼容 |
|---|---|
| 改方法名 | 改函数体逻辑 |
| 改参数个数（增/减） | 改注释、docstring |
| 改参数顺序 | 改局部变量名 |
| 改参数名（关键字调用会断） | 加日志、加断言 |
| 删方法 | 改内部实现 |
| 把有默认值的参数改成必填 | 调整语句顺序（语义不变） |

**判据一句话：调用方看得见的东西不能动，调用方看不见的随便动。**

参数名也算“看得见”——`client.login(user="test")` 这种关键字调用会直接断。

初考失分点：只给了 2 项“不影响兼容”；把“改方法名”写成了“改方法值”。

### 3.5 Q9：清单式回归的三重代价（补考满分）

| # | 代价 | 具体表现 |
|---|---|---|
| 1 | 要手工维护 | 新增用例必须记得加进 `FILES`，忘了就不跑，没有任何提示 |
| 2 | 一个笔误拖死整场 | `file or directory not found` 让 pytest 放弃整个收集，你只看到 `collected 0 items`，错误信息离真相很远 |
| 3 | 覆盖范围受限 | 只跑“我记得的那批”，仓库里其他用例失败了你永远不知道 |

第 3 项才是 4 条 xfail 的成因：**不是清单式会漏，是清单式让你从来不知道它们坏了。**

4 条 xfail 的根因分四类：

| 类型 | 例子 |
|---|---|
| 写死旧 token 值 | `assert data["token"] == "token123"`，mock 已改动态 `token-N` |
| 硬编码认证头 | `Bearer token123` 不是当前 LATEST_TOKEN |
| 依赖 Cookie 认证 | mock 只认 `Authorization: Bearer` |
| 用旧版客户端类 | 文件内自查的旧 `ApiClient` 不保存 token |

### 3.6 Q10：新项目脚手架（初考 3 → 补考 6）

初考把题目当自己的项目答（`tests/` + `day*_homework.py`），属于“没读需求就交方案”。补考修正了两项，仍有三处硬错：

#### 错 1：`pythonpath = shop-api-tests/`

```ini
pythonpath = shop-api-tests/     ← 错
pythonpath = .                   ← 对
```

值相对 **rootdir** 解析，`shop-api-tests/` 拼出来是：

```
rootdir/shop-api-tests/  →  D:\...\shop-api-tests\shop-api-tests\   （不存在）
```

结果：`sys.path` 多一个不存在的路径，`from core.shop_api import ShopApi` 直接 `ModuleNotFoundError`。

更根本的是**可移植性**：把仓库文件夹名焊进配置，别人 clone 成 `shop-tests` 就跑不了。`.` 的意思是“本项目根”，与文件夹叫什么无关。

#### 错 2：`python_files` 带着 `day*_homework.py`

```ini
python_files = test_*.py *_test.py day*_homework.py    ← 错
python_files = test_*.py *_test.py                     ← 对
```

`day*_homework.py` 是现有项目的历史命名，不是新项目需求。新项目从第一天就让用例统一叫 `test_xxx.py`。

理解偏差：**`python_files` 里每一项都是“允许被收集”的名单**，多写一项不是“更宽容”，是“把一个不该进名单的命名永久合法化”。

#### 错 3：`open("data/xxx.json")` —— 题目的禁区

题目要求“从任何目录执行都不出错”，而他写的正是依赖 cwd 的版本。而且这些 `open()` 若放在**模块顶层**，会在**收集阶段**执行——cwd 错了报错出现在 `collected 0 items` 之前，看起来像“没收集到用例”。

正确写法：

```python
# plugins/paths.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG   = os.path.join(BASE_DIR, "conf", "env.json")
```

```python
# cases/test_login.py
import os
from plugins.paths import DATA_DIR

with open(os.path.join(DATA_DIR, "users.json"), encoding="utf-8") as f:
    cases = json.load(f)
```

**判断标准：代码里出现 `"data/xxx.json"` 这种以目录名开头的相对路径，就是隐患。** 相对路径只允许出现在“路径常量文件”里一次。

#### 还有一处：`import` 客户端根本没写

他写的 `def test_001(client)` 是“用 fixture 拿实例”，不是“import 客户端”。如果用例要直接构造客户端（如测错误分支），需要：

```python
from core.shop_api import ShopApi
```

这行能成立，全靠 `pythonpath = .`——**这就是 `pythonpath` 的意义：让项目根下任何包都能被绝对导入。**

---

## 四、Q10 标准答案（新项目脚手架）

### 4.1 目录树

```
shop-api-tests/
├── pytest.ini              ← 留根：决定 rootdir
├── conftest.py             ← 留根：pytest_plugins 只能顶层
├── plugins/                ← 留根：被 import
│   ├── __init__.py
│   ├── paths.py            ← 路径常量唯一出处
│   ├── env_config.py
│   ├── api_fixtures.py
│   └── reporting.py
├── core/                   ← 留根：被 import
│   ├── __init__.py
│   ├── http_session.py
│   └── shop_api.py
├── conf/env.json           ← 留根：被 paths.py 引用
├── data/*.json             ← 留根：被 paths.py 引用
├── artifacts/  logs/       ← 留根：运行时生成
└── cases/                  ← 只放用例
    ├── test_login.py
    └── test_order.py
```

### 4.2 `pytest.ini`

```ini
[pytest]
testpaths = cases
pythonpath = .
python_files = test_*.py *_test.py
addopts = -v
markers =
    smoke: 冒烟用例，验证核心链路
    full: 全量回归用例
```

### 4.3 `conftest.py`

```python
pytest_plugins = (
    "plugins.env_config",
    "plugins.api_fixtures",
    "plugins.reporting",
)
```

（`import pytest` 不需要——`pytest_plugins` 是 pytest 识别的模块级变量，不是装饰器）

### 4.4 用例里的两件事

```python
# cases/test_login.py
import json
import os

from core.shop_api import ShopApi        # 靠 pythonpath = . 提供项目根
from plugins.paths import DATA_DIR       # 靠 paths.py 提供绝对锚点

USERS = os.path.join(DATA_DIR, "users.json")
```

### 4.5 冒烟

```powershell
pytest cases -m smoke
```

前置两步，作用不同：

| 前置 | 作用 | 不做会怎样 |
|---|---|---|
| 给用例打 `@pytest.mark.smoke` | 让过滤有东西可选 | 跑 0 条 |
| 在 `markers` 里注册 | 防拼写错误 | **只警告不阻断**，过滤仍能工作 |

所以“注册”不是必须，但它是**把“拼错标记名”从静默变成可见**的唯一手段。

---

## 五、复盘暴露的五个真实隐患

这五项是复盘时开 `conftest.py` 现场发现的，**不是假想问题**，全部存在于当前仓库（`main` 分支最新提交）。

| # | 隐患 | 后果 | 处置 |
|---|---|---|---|
| 1 | 根 `conftest.py` 里 `def client(base_url)` 与 `support/api_fixtures.py` 重复 | 改插件静默不生效；排查成本极高 | 删根 conftest 里的 `client` |
| 2 | 根 `conftest.py` 顶部 8 个死 import（`os` / `datetime` / `logging` / `json` / `requests` / `extras` / `html_lib` / `ApiClient`） | 全部指向已注释代码，误导读者以为 conftest 仍有实现 | 整段删掉 |
| 3 | 根 `conftest.py` 里 `ARTIFACT_DIR="artifacts"`（相对路径） | 与 `support/paths.py` 的绝对路径重复且值不同，是“第二个出处” | 删掉 |
| 4 | `check_client` / `make_token` 仍留 conftest，`api_fixtures.py` 里注释写着“原样搬过来”但**没搬** | 注释承诺与实际不符；conftest 名义上“只装配”实际还扛 fixture | 搬进 `api_fixtures.py`，或改注释 |
| 5 | `conftest.py` 里有大段注释代码（旧 `pytest_addoption`、旧 `client`、旧 hook） | 注释当备份会干扰 `findstr "def "`、干扰代码阅读 | 靠 git 历史，删掉 |

**一条共同的病**：这五项都不是“语法错”，而是**“看起来还行、实际已经不是你以为的样子”**。它们不报错，只在你想改某处时让你白忙。

---

## 六、第八周总结

| 天 | 主题 | 核心产出 | 验收 |
|---|---|---|---|
| Day42 | 装配层拆分 | `support/` 三插件 + conftest 只装配 | 全量 48 通过 |
| Day43 | 客户端分层 | `HttpSession` + `TestApi` + 薄壳 | 全量 48 通过 |
| Day44 | 目录迁移 | 用例进 `tests/` + `pytest.ini` 三行 + bat 目录化 | 99 条，86 passed |
| Day45 | 第八周复盘 | 93 分通过 + 5 项隐患清单 | — |

### 三条原则在本周的落地

| 原则 | Day42 | Day43 | Day44 |
|---|---|---|---|
| **职责分离** | 六职责拆三插件 | 一个类拆两层 | 用例与基础设施分目录 |
| **依赖单向** | conftest 只装配不实现 | 业务依赖传输，传输不知业务 | 用例依赖框架，框架不依赖用例 |
| **单一出处** | `pytest_plugins` 一份装配清单 | 一个 `self` 两批属性，不重复存 | 路径只由 `paths.py` 出、用例位置只由 `testpaths` 出 |

**“单一出处”这条今年没守住**：`client` 有两个定义、`ARTIFACT_DIR` 有两个来源。这正是第五节的隐患 1 和 3。

### 本周最大收获排序

1. **给文件 ≠ 给目录**（Day44）——一个反直觉但极常见的坑
2. **hook 崩了整场崩**（Day42）——理解了 pytest 的“记录容器”概念
3. **迁移的价值在可见性，不在整齐**（Day44）——4 条历史失败被照亮
4. **错误发生点 ≠ 根因点**（Day43）——`super()` 缺失的延迟报错

---

## 七、下一步

### 第 9 周开班前，先清掉第五节的 5 项隐患

这是 30 分钟以内的清理工作，收益是“conftest 真的只剩装配”：

```python
# 清理后 conftest.py 全文应只剩这几行
pytest_plugins = (
    "support.env_config",
    "support.api_fixtures",
    "support.reporting",
)
```

配套动作：

1. `check_client` / `make_token` 搬进 `support/api_fixtures.py`
2. 删掉 conftest 里的 `client`、`ARTIFACT_DIR`、8 个死 import、所有注释代码
3. 跑 `pytest tests -q` 确认仍是 `86 passed, 2 skipped, 11 xfailed`

> 注意：如果 `check_client` / `make_token` 只被 `tests/day16_homework.py` 这类早期用例使用，搬进插件后行为不变（插件 fixture 全局可用）。唯一要小心的是**不要在两处都留**——那就是隐患 1 的重演。

### 第 9 周主题

按当前进度，第 9 周的两条候选主线：

| 候选 | 内容 | 适合度 |
|---|---|---|
| A. 框架收尾 + 静态检查 | 隐患清理、命名规范、`flake8`/`black`、README 补齐 | 顺手，1~2 天可完成 |
| B. CI 接入 | GitHub Actions 或 Jenkins 跑 `run_tests.bat` 的等价命令、报告归档、失败通知 | 与“外企/大厂测开岗”要求直接相关 |

建议：**先用 1 天做 A（把本周欠的债还掉），再接 B**。框架不干净就上 CI，等于把隐患放大到每次提交。

具体开课内容以你的 18 个月计划表为准；如果计划表里第 9 周另有主题，告诉我，我按计划走。

---

## 附录 A：conftest 清理执行记录（复盘当天完成）

### A.1 清理动作

两个文件，全文替换。

**`support/api_fixtures.py`（新全文）**

```python
"""客户端类 fixture"""
import pytest
import requests

from api_client import ApiClient


@pytest.fixture
def client(base_url):
    return ApiClient(base_url)


@pytest.fixture
def check_client():
    """返回 requests 模块，供早期练习用例使用"""
    return requests


@pytest.fixture
def make_token():
    return "token123"
```

**`conftest.py`（新全文）**

```python
"""根 conftest：只做装配，不承载实现。

职责已拆到 support/ 下三个插件：
  env_config   -> --env 参数 + env_name / base_url
  api_fixtures -> client / check_client / make_token
  reporting    -> 失败落盘 + 报告内嵌 + 终端汇总
"""

pytest_plugins = (
    "support.env_config",
    "support.api_fixtures",
    "support.reporting",
)
```

### A.2 为什么 `check_client` / `make_token` 是搬而不是删

清理前查调用方：

| fixture | `tests/` 内 | `tests/` 外 |
|---|---|---|
| `check_client` | 0 处 | `day18_test.py:40` |
| `make_token` | 0 处 | `day18_test.py:61`、`day20_test.py:27` |

`tests/` 里没人用，但根目录的老练习文件在用。直接删会让 `pytest day18_test.py` 报 `fixture 'check_client' not found`，所以必须搬进插件——插件 fixture 对根目录文件同样生效。

### A.3 验证结果

| 验证 | 命令 | 结果 |
|---|---|---|
| conftest 已无函数定义 | `findstr /n "def " conftest.py` | **无输出** ✅ |
| 插件 fixture 迁移成功 | `pytest day18_test.py -q` | `12 passed` ✅（其中 `test_baidu`、`test_check_token` 分别用到两个搬走的 fixture） |
| `tests/` 全量 | `pytest tests -q` | `86 passed, 2 skipped, 11 xfailed` ✅ |

### A.4 “清理后不必重跑全量”的推理链

清理改变了 `conftest.py`，理论上要重跑全量。但可以推理确认：

1. `tests/` 里**没有任何用例**使用 `check_client` / `make_token`（全仓 grep 只在 `day18_test.py` / `day20_test.py` 命中）
2. `tests/` 唯一依赖的插件 fixture 是 `client`，而 `client` 现在**只有一个定义**
3. 插件侧供给已被 `day18_test.py` 的 12 passed 独立证明

三条成立 → `tests/` 的 86 条不受影响。

**这是“验收推理”而不是“省略验证”**：不是没验证，是用更强的证据（插件 fixture 可用 + 依赖面为空）替代了重复执行。以后做 CI、做回归时，这种推理能帮你判断“哪些改动必须全量、哪些改动可以定向”。

### A.5 清理后 conftest 的五项隐患全部关闭

| # | 隐患 | 状态 |
|---|---|---|
| 1 | `client` 两处重复定义 | ✅ 只剩插件一份 |
| 2 | 8 个死 import | ✅ 整段消失 |
| 3 | `ARTIFACT_DIR="artifacts"` 相对路径残留 | ✅ 整段消失 |
| 4 | `check_client` / `make_token` 承诺搬运未做 | ✅ 已搬 |
| 5 | 大段注释代码当备份 | ✅ 整段消失 |

---

## 附录 B：Anaconda 事故复盘（裸 `pytest` 踩进另一个 Python）

### B.1 现象

```cmd
D:\Desktop\my_python\learn\testopen-study>pytest tests -q
Traceback (most recent call last):
  File "d:\anaconda3\Scripts\pytest-script.py", line 10, in <module>
  ...
  File "d:\anaconda3\lib\site-packages\iniconfig\__init__.py", line 54, in __init__
    tokens = self._parse(iter(f))
  ...
UnicodeDecodeError: 'gbk' codec can't decode byte 0xaf in position 166: illegal multibyte sequence
```

报错栈的第一行就暴露了真相：`d:\anaconda3\Scripts\pytest-script.py` —— **跑的不是 Python39 那套 pytest，是 Anaconda 那套。**

### B.2 两个错误叠加

| # | 错误 | 作用 |
|---|---|---|
| 1 | 用错解释器 | 走 PATH 里的 `pytest.exe`，命中 Anaconda 的 site-packages |
| 2 | `pytest.ini` 含中文 | 旧版 `iniconfig` 按系统 locale（GBK）读文件 → 解码崩 |

**单独任一个都不会崩**：
- 用 Anaconda 跑、但 ini 全英文 → 能跑（只是环境不对）
- 用 Python39 跑、ini 含中文 → 能跑（新版 `iniconfig` 固定 UTF-8）

两个凑一起才炸。

### B.3 为什么会走 Anaconda

```cmd
where pytest
```

输出顺序类似：

```
d:\anaconda3\Scripts\pytest.exe
C:\Users\lenovo\AppData\Local\Programs\Python\Python39\Scripts\pytest.exe
```

第一个就是 Anaconda。`pytest.exe` 是包装脚本，**里面写死了它自己那套 Python 路径**——你以为在调“同一个 pytest”，其实调的是另一个 Python 环境里的另一份实现。

### B.4 处置

**铁律再加一条**：不许出现裸 `pytest` / `pytest.exe`，一律写：

```cmd
"C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pytest tests -q
```

`-m` 的含义是“**用当前这个解释器去找 pytest 模块**”，彻底绕开 `pytest.exe` 的路径选择。这比“记住 PATH 顺序”可靠得多——PATH 随时可能被新装的软件改掉。

**建议加固**：把 `pytest.ini` 里 markers 的中文描述改成英文，让这个文件不再依赖编码：

```ini
markers =
    smoke: core path smoke tests
    full: full regression tests
```

代价只是 `pytest --markers` 输出变英文；收益是上 CI（Linux 容器 locale 不同）时不会重演同类问题。

### B.5 顺带发现：`-q` 被 `addopts = -v` 抵消

`pytest.ini` 里有 `addopts = -v`，命令行再加一个 `-q`：

```
- v（+1 级详细度）  +  -q（-1 级）  =  0 级（默认样式）
```

所以 `pytest tests -q` 看到的是“每行一个用例名 + 百分比”的默认输出，而不是安静模式。

| 命令 | 实际详细度 |
|---|---|
| `pytest tests` | 详细（`-v` 生效） |
| `pytest tests -q` | 默认（被抵消） |
| `pytest tests -q -q` | 安静（只显示点） |

`-v` 对排查有价值（能看到完整 nodeid），建议保留，需要安静时写 `-qq`。
