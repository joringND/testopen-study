# Day40 学习笔记：报告装配与一键全量——让证据跟着报告走（第 7 周 Day4）

> 日期：2026-11-11
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 7 周 · Day40
> 状态：✅ 全量 `48 passed, 2 skipped, 7 xfailed in 2.78s`；产出 `report_test_20261111_212801.html`；extras 内嵌经 `--runxfail` 单独验证通过
> 里程碑：Day37~39 三个零件（配置、日志、证据）第一次装配成一份**能直接发给别人的单文件报告**

---

## 一、今日目标

前三天各造了一个零件：Day37 环境可切、Day38 日志可见、Day39 失败能留证。但它们散在三处——配置在 conftest、日志在 `logs/run.log`、证据在 `artifacts/`。今天做装配：

1. **一条命令跑全量**（`run_tests.bat`，11 个测试文件 + 环境参数 + 时间戳报告名）
2. **证据嵌进报告正文**（pytest-html 的 `extras`，失败用例附近直接看得到请求/响应）
3. **报告单文件可交付**（`--self-contained-html`，双击即开，发给谁都不怕路径断）

## 二、今日涉及文件

| 操作 | 文件 | 说明 |
|---|---|---|
| 【修改】 | `conftest.py` | 顶部加 `import html as html_lib`；hook 里用 `extras.html()` 把证据内嵌进报告；删除多余的 `pytest_plugins` 声明 |
| 【重写】 | `run_tests.bat` | 从 4 个文件扩到 11 个；支持 `run_tests.bat pre` 传环境；**非 test 环境自动收窄到 day37**；报告名带环境+时间戳；跑完自动打开 |
| 【只读】 | `pytest.ini` | `testpaths=day25_homework.py` 是坑源，bat 必须显式列文件 |

## 三、机制链

```
run_tests.bat（一键入口：11 个文件 + --env + --html + --self-contained-html）
        ↓
pytest 逐条执行 → 失败用例走到 pytest_runtest_makereport（hookwrapper）
        ↓
      ┌────────────┬────────────┐
      ↓            ↓            ↓
json.dump      日志一行      report.extras
落盘 artifacts  失败现场已保存  append(extras.html(...))
      ↓            ↓            ↓
  本地存证      控制台/run.log   HTML 报告正文
                                    ↓
                        单文件报告，双击即开，发给别人
```

**一句话**：同一份证据，一次拦截，三个去处——文件、日志、报告。

## 四、代码改动

### 4.1 conftest.py 顶部

```python
import html as html_lib          # 新增：JSON 里的 < > & 必须转义
from pytest_html import extras   # 新增：extras.html / extras.text / extras.url
```

**删掉了原来第 2 行**：

```python
pytest_plugins = ("pytest_html",)     # ← Day40 初版加的，验证后确认多余，已删
```

官方文档的 extras 示例里**没有**这一步：pytest-html 通过 entry point 自动加载，手动声明等于重复注册插件，反而容易踩坑。

### 4.2 conftest.py 的 hook（最终版）

Day39 的落盘逻辑一字未动，只在末尾追加「嵌进报告」：

```python
ARTIFACT_DIR = "artifacts"


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
    path = f"{ARTIFACT_DIR}/{safe}_{ts}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "test": item.nodeid,
            "error": str(report.longrepr)[:1000],
            "last_exchange": exchange,
        }, f, ensure_ascii=False, indent=2)

    logger.info(f"失败现场已保存: {path}")

    # ↓ Day40 新增：把证据直接内嵌进报告（self-contained 模式也可见）
    extra_list = getattr(report, "extras", [])
    escaped = html_lib.escape(json.dumps(exchange, ensure_ascii=False, indent=2))
    extra_list.append(extras.html(
        "<div style='font-size:12px;'>"
        "<strong>失败现场</strong>"
        f"<pre style='white-space:pre-wrap;margin:6px 0 0 0;'>{escaped}</pre>"
        "</div>"
    ))
    report.extras = extra_list
```

**四个要点：**

| 代码 | 为什么 |
|---|---|
| `getattr(report, "extras", [])` | `report` 上默认没有 `extras` 属性，直接 `.append` 会 `AttributeError` |
| 用 `extra_list` 这个中间变量 | `extras` 已经是 pytest_html 的命名空间，再写 `extras = [...]` 会把它遮蔽，后面 `extras.html` 就调不动了 |
| `extras.html(...)` 而不是 `extras.text(...)` | 4.0 起 text / json / image 类 extras 被**存成 assets 目录下的独立文件**，报告里只放链接；`--self-contained-html` 下这些外部文件不内联 → 看不到。html 类型是 Raw HTML，直接内嵌 |
| `html_lib.escape(...)` | JSON 里含 `<` `>` `&`（响应体可能是 HTML/XML）时会破坏报告结构，必须转义 |
| 末尾 `report.extras = extra_list` | 官方示例的标准写法：取出 → append → 赋回 |

### 4.3 run_tests.bat（重写，全英文）

```bat
@echo off
setlocal

set PYTHON=C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe
set ENV=%1
if "%ENV%"=="" set ENV=test

set FILES=day25_homework.py day27_homework.py day28_homework.py day30_homework.py day32_homework.py day33_homework.py day34_homework.py day35_homework.py day37_homework.py day38_homework.py day39_homework.py
if not "%ENV%"=="test" set FILES=day37_homework.py

for /f %%i in ('powershell -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i
set REPORT=report_%ENV%_%TS%.html

if not exist logs mkdir logs
if not exist artifacts mkdir artifacts

echo === Running tests, env: %ENV% ===
%PYTHON% -m pytest %FILES% --env %ENV% -v --tb=short --html=%REPORT% --self-contained-html

echo === Report: %REPORT% ===
start "" %REPORT%
pause
```

## 五、实测结果

### 5.1 全量（11 个文件）

```
====================================== 48 passed, 2 skipped, 7 xfailed in 2.78s =======================================
=== Report: report_test_20261111_212801.html ===
```

报告自动打开。2 skipped 是 Day28 的挂起用例 + Day37 的环境跳过用例；7 xfailed 是历次演示用例（按约定挂起不删）。

### 5.2 单跑验证 extras（关键）

全量报告里**看不到「失败现场」块**，因为 day39 的演示用例是 xfail——它的 report 是 `skipped`，第一道判断 `not report.failed` 就 return 了，落盘与 extras 都没触发。`artifacts/` 里唯一的 json 时间戳 `20261110_232518` 还是 Day39 那天手工留的。

改用单独跑 + `--runxfail` 强制真失败：

```powershell
& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pytest day39_homework.py --runxfail -v --html=report_debug.html --self-contained-html
start "" report_debug.html
```

报告里 `test_fail_dump` 展开后出现四块，来源各不相同：

| 报告里的内容 | 来源 |
|---|---|
| **失败现场**（JSON 全文） | 我们的 hook + `extras.html` |
| `AssertionError: 实际年龄是 27` | pytest 原生 longrepr |
| `Captured log call`（login/get_user 两行） | pytest 日志捕获（Day38 配的 `log_cli`） |
| 整份 HTML | pytest-html + `--self-contained-html` |

实际显示：

```
失败现场
{ "method": "GET", "path": "/get_user", "url": "...", "req_body": "None",
  "status": 200, "resp_text": "{\"code\": 0, \"name\": \"张三\", \"age\": 27}", "cost_ms": 1 }
day39_homework.py:15: assert data["age"] == 28
E   AssertionError: 实际年龄是 27
E   assert 27 == 28
--- Captured log call ---
21:50:21 INFO api_client: POST /login -> 200 2ms
21:50:21 INFO api_client: GET /get_user -> 200 1ms
```

**看懂这份报告只需三秒**：接口 200、返回 age=27、断言写的是 28 → 用例写错，不是接口坏。

### 5.3 换环境跑（一次有价值的翻车）

第一次执行 `.\run_tests.bat pre`（当时 bat 还没做分流，11 个文件全跑）：

```
16 failed, 31 passed, 3 skipped, 7 xfailed in 8.21s
```

**原因**：`--env pre` 把 `base_url` 换成了 `http://pre.api.example.com`，这是 `config/env.json` 里的**占位假域名**，DNS 解析不了。所有真发请求的用例全部 `ConnectionError`：

```
requests.exceptions.ConnectionError: HTTPConnectionPool(host='pre.api.example.com', port=80):
Max retries exceeded (Caused by NameResolutionError ...)
```

**这恰恰是配置切换生效的证据**：

| 现象 | 含义 |
|---|---|
| `--env pre` 后仍 48 passed | ❌ `--env` 没生效，base_url 压根没换 |
| `--env pre` 后大量 ConnectionError | ✅ base_url 确实换成 pre，只是该环境不存在 |

**修法**：bat 里按环境收窄文件范围，非 test 环境只跑配置类用例：

```bat
if not "%ENV%"=="test" set FILES=day37_homework.py
```

改后实测：

```
======================================= 2 passed, 1 skipped in 0.04s =======================================
=== Report: report_pre_20261111_221026.html ===
```

3 条全对：`test_env_config` / `test_env_name_valid` 读配置不发请求 → pass；`test_real_api_only_in_test` 主动 skip。

**后续提醒**：等以后有了真实 pre 环境（能解析的域名），把这行收窄逻辑删掉即可恢复全量；现阶段它的作用是**防止拿假域名去打业务用例，制造 16 条假红**。

## 六、关键设计决策

| 决策 | 理由 |
|---|---|
| 证据内嵌而不是给 artifacts 链接 | 报告要发给别人；`extras.url` 指向本地相对路径，跨机器就断链。内容嵌进去，报告才是真正自包含的 |
| `extras.html` 而非 `extras.text` | text/json/image 类型在 4.0 起落成 assets 外部文件，`--self-contained-html` 不内联 → 报告里看不到。html 类型直接写进正文 |
| bat 里逐条列文件名 | `pytest.ini` 的 `testpaths=day25_homework.py` 会把收集范围锁死在一个文件，直接 `pytest` 只跑 4 条 |
| `set ENV=%1` + 空值兜底 | 让同一个 bat 支持 test/pre；双击无参数时默认 test，不会跑空 |
| 报告名带 `%ENV%_%TS%` | 历史报告不覆盖；文件名就能看出跑的是哪个环境、什么时候跑的 |
| 全量跑前重启 mock | `/flaky` 的 `FLAKY_COUNT`、`/login` 的 token 计数都是模块级全局状态，跑过多轮后旧用例预期失真。重启 = 状态复位 |
| bat 全英文 | 中文进 bat 走 GBK，控制台乱码（Day30 老坑） |

## 七、今日坑

### 1. 文件名拼错：`run_test.bat` → `not recognized`

```
'.\run_test.bat' is not recognized as an internal or external command
```

实际文件是 `run_tests.bat`（复数）。**这类报错第一反应永远是 `dir /b *.bat` 看真实文件名**，不要怀疑环境。类似的还有 `mock_server.py` 路径拼错（`/flacky`）、端口抄错（8080 vs 8000）——都属于「输入层错误」，改一个字就好，别去改代码。

### 2. `extras.text` 在 `--self-contained-html` 下不可见

这是今天最值钱的坑。pytest-html 4.0 的 changelog 写明：*Save images, text, and JSON extras as files in an assets directory*。也就是说 `text` 类型被存成 `assets/xxx.txt`，报告里只留一个链接；而 self-contained 模式不会把外部文件内联，所以打开报告啥也看不到（也没有报错、没有警告）。

**判据**：报告里该出现的位置空白，但 artifacts 有文件、控制台日志正常 → 优先怀疑 extras 类型选错，换 `extras.html`。

### 3. `pytest_plugins = ("pytest_html",)` 是多余的

一开始以为 extras 需要显式声明插件，加了这行。查官方文档后发现示例里根本没有——pytest-html 通过 entry point 自动加载，手动声明属于重复注册。删掉后 extras 照常工作。

**教训**：能用官方示例验证的，就别靠记忆补配置。多一行配置 = 多一个潜在故障点。

### 4. xfail 的 report 是 skipped，不是 failed

```python
if report.when != "call" or not report.failed:
    return
```

带 `@pytest.mark.xfail` 的用例在真失败时，report 是 `skipped` + `wasxfail` 属性，`failed` 为 False → hook 直接 return，**不落盘、不加 extras**。所以全量报告里看不到证据块是**正确行为**，不是没修好。

验证 extras 必须让用例真失败：`--runxfail`（让 xfail 失效）或临时摘掉标记。

如果以后想让 xfail 也留证（复盘时想看到当时回了什么），条件是：

```python
    if report.when != "call":
        return
    if not (report.failed or getattr(report, "wasxfail", False)):
        return
```

### 5. `extras.html` 不支持 `name=` 参数

文档明确：*You can also specify the name argument for all types other than html*。`extras.text(..., name="失败现场")` 有标题，`extras.html(...)` 没有，所以标题要自己写在 HTML 里（`<strong>失败现场</strong>`）。

### 6. `extras` 命名遮蔽

```python
extras = getattr(report, "extras", [])       # ← 错：把 pytest_html 的 extras 遮蔽了
extras.append(extras.text("x"))              # AttributeError
```

正确做法是用另一个名字（`extra_list`），或者全程写 `report.extras`。

### 7. `--env pre` 等于用假域名打全部用例

`--env pre` 只负责换地址，不负责地址能通。`config/env.json` 里 pre 是占位域名，全量跑就是 16 条 `ConnectionError`。这类失败**长得像用例全红，实质是环境不存在**——`--tb=short` 里看到 `ConnectionPool(host='pre.api.example.com')` 就该立刻反应过来。

结论：**test 跑全量，其他环境只跑配置类用例**（bat 里靠一行 `if not "%ENV%"=="test"` 分流）。

### 8. xfail 会掩盖环境故障

`@pytest.mark.xfail` 标记的用例，不管抛断言错还是连接错，结果都是 `xfailed`（预期失败）。所以 pre 环境连不上时，day39 那条仍然显示 xfailed，看起来“一切正常”。**排查环境问题时，先 `--runxfail` 让真实异常暴露出来**。

## 八、练习答案

### 1. 再加一条「请求摘要」

```python
    summary = f"{exchange['method']} {exchange['path']} -> {exchange['status']} {exchange['cost_ms']}ms"
    extra_list.append(extras.html(
        "<div style='font-size:12px;'><strong>请求摘要</strong>"
        f"<pre style='white-space:pre-wrap;margin:6px 0 0 0;'>{html_lib.escape(summary)}</pre></div>"
    ))
    report.extras = extra_list     # 一次赋回即可，两次 append 后再统一赋值
```

注意：多个 extras 时**只在最后赋回一次** `report.extras`，中间都往 `extra_list` 里 append，避免反复改写同一属性。

### 2. `run_tests.bat pre` 会发生什么

**（本条首次给出的答案是错的，实测后已更正）**

原始 bat 跑 `.\run_tests.bat pre` → **16 failed, 31 passed, 3 skipped, 7 xfailed**：

- `base_url` 换成假域名 `http://pre.api.example.com`，DNS 解析失败
- 所有依赖 `client` 真发请求的用例全部 `ConnectionError`
- day37 三条中：2 条只读配置 → pass，1 条主动 skip
- 7 xfailed 里含 day39 那条——**xfail 吞掉任何异常（包括 ConnectionError）**，把“环境连不上”伪装成了“预期失败”

**正确做法是不让 pre 跑业务用例**，在 bat 里加分流：

```bat
set FILES=day25_homework.py ... day39_homework.py
if not "%ENV%"=="test" set FILES=day37_homework.py
```

改后 `.\run_tests.bat pre` → **2 passed, 1 skipped**，报告 `report_pre_20261111_221026.html`。

**关键理解**：`--env` 只改 base_url 的**取值**，既不保证环境可用，也不会让用例自动适配新环境。真正区分环境的用例要自己写 skip 条件（day37 那条就是示例），而系统层面的隔离靠 bat 收窄范围。

### 3. 统计 artifacts 数量

```python
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """跑完在末尾打印证据数量"""
    if os.path.isdir(ARTIFACT_DIR):
        files = [f for f in os.listdir(ARTIFACT_DIR) if f.endswith(".json")]
        terminalreporter.write_line(f"artifacts 目录共 {len(files)} 个证据文件")
```

`pytest_terminal_summary` 是 pytest 原生钩子，在测试全部结束、报告落盘前调用；`terminalreporter.write_line` 往控制台写一行。注意是**累计数量**，不是本次新增——想知道本次新增，得在 `pytest_sessionstart` 先记一份文件列表再对比。

## 九、自测答案

### 1. pytest-html 加额外内容用哪个 API？为什么不能直接 append？

`report.extras` 列表 + `pytest_html.extras` 提供的类型（`html` / `text` / `url` / `json` / `image`）。

不能直接 `report.extras.append(...)`：`TestReport` 对象默认**没有** `extras` 属性（只有插件渲染时才可能带），直接访问会 `AttributeError: 'TestReport' object has no attribute 'extras'`。标准写法是 `extras = getattr(report, "extras", [])` → append → `report.extras = extras` 赋回。

### 2. `pytest_plugins = ("pytest_html",)` 干什么？不放会怎样？

作用是显式声明提前加载插件。**但 extras 并不需要它**——pytest-html 通过 entry point 自动加载（`pytest --version` 里能看到 `html-4.2.0`），不写这行 extras 照样工作；写了属于重复注册，是多余配置。

### 3. bat 里为什么逐条列文件名？

`pytest.ini` 有 `testpaths=day25_homework.py`，直接执行 `pytest` 只收集这一个文件（4 条用例），其余 10 个文件全被忽略，而且**不会报错**——你会误以为在跑全量。命令行显式列文件时，参数优先级高于 ini 的 testpaths，才是真正的全量。

### 4. `set ENV=%1` 里的 `%1` 是什么？

bat 的第一个命令行参数。`run_tests.bat pre` → `%1` = `pre` → `ENV=pre`；不传参数时 `%1` 为空串，下一行 `if "%ENV%"=="" set ENV=test` 兜底成 test。所以同一个脚本既能双击跑默认环境，也能带参切换。

### 5. 全量跑前为什么重启 mock？

mock 里有三处**模块级全局状态**：

- `FLAKY_COUNT`：`/flaky` 前 2 次返 500、第 3 次返 200，跑过一轮后计数已耗尽，后面永远 200
- `COUNTER`：每次 login 自增，token 序号一路累积
- `LATEST_TOKEN`：只认最新签发的那个 token

不重启就跑，Day33 的「flaky 重试」用例会从"第 3 次成功"变成"第 1 次就成功"，断言预期失真；`/login` 相关用例也可能因为 token 对不上而 401。**重启 mock = 状态复位**，这是全量跑的标准前置动作（和"改了 mock 必须重启"是同一条规矩的两个理由）。

## 十、课后答疑（extras 三连问）

### 10.1 `exchange` 是从哪里来的

它是**我们自己挂在 client 对象上的属性**，不是 pytest 提供的。完整链路分三步：

**① 初始化**（`api_client.py` 的 `__init__`）：

```python
        self.last_exchange = None      # 先占位，区分"从未请求"与"属性不存在"
```

**② 写入**（`api_client.py` 的 `_log()`，每次请求结束都整体覆盖）：

```python
        req = resp.request
        self.last_exchange = {
            "method": method, "path": path, "url": req.url,
            "req_body": str(req.body)[:500],
            "status": resp.status_code,
            "resp_text": resp.text[:2000],
            "cost_ms": cost,
        }
```

`login()` 和 `_request()` 都会调 `_log()`，所以任何一次请求都会刷新它。

**③ 读取**（`conftest.py` 的 hook）：

```python
    client = item.funcargs.get("client")
    exchange = getattr(client, "last_exchange", None) if client else None
```

**为什么 hook 拿得到用例内部的那个 client**：

| 概念 | 含义 |
|---|---|
| `item` | 当前正在跑的这条用例（`Function` 对象） |
| `item.funcargs` | pytest 为这条用例**已解析好的 fixture 字典**，键是参数名、值是 fixture 返回值 |
| `item.funcargs["client"]` | 就是用例签名里 `client` 拿到的**同一个对象引用**，不是复制 |

| 常见疑问 | 解答 |
|---|---|
| 为什么叫 `last` 不是 `exchanges` | 覆盖式记录，只留最近一次；失败定位只需最后一次请求 |
| 什么时候是 `None` | 用例在发请求前就挂了（fixture 报错、参数错）→ hook 直接 return，不写文件不加 extras |
| 用例没写 `client` 参数 | `item.funcargs.get("client")` 返回 `None`，同样跳过，天然安全 |

**反证**：去掉 `_log()` 里那段赋值，`exchange` 永远为 `None`，Day39 的落盘和 Day40 的 extras 都不会有内容——证明这个属性是我们自己造的。

### 10.2 `extra_list = getattr(report, "extras", [])` 是什么意思

Python 内置 `getattr` 的**三参数形式**：取属性，取不到就给默认值，不抛异常。

| 位置 | 值 | 含义 |
|---|---|---|
| 1 | `report` | 目标对象（`TestReport`） |
| 2 | `"extras"` | 属性名 |
| 3 | `[]` | 默认值：属性不存在时返回它 |

**三种写法对比**：

| 写法 | 结果 |
|---|---|
| `report.extras.append(x)` | 💥 `AttributeError: 'TestReport' object has no attribute 'extras'` |
| `report.extras = []` 再 append | ⚠️ 能跑，但会**清空**别人（插件或其他 hook）已加的 extras |
| `getattr(report, "extras", [])` 再 append | ✅ 有就沿用原列表，没有就新建空列表 |

等价写法：

```python
extra_list = report.extras if hasattr(report, "extras") else []
```

**为什么末尾必须赋回**：

```python
extra_list = getattr(report, "extras", [])
extra_list.append(...)
report.extras = extra_list      # 不能省
```

- 属性**原本存在**：`extra_list` 是同一个列表的引用，append 已生效，赋回是再确认
- 属性**原本不存在**：`extra_list` 是新建的空列表，与 `report` 无关；不赋回，报告里就什么都没有

官方示例统一用"取出 → append → 赋回"，两种情况都覆盖。

### 10.3 `escaped = html_lib.escape(json.dumps(exchange, ensure_ascii=False, indent=2))`

两层：**字典 → JSON 文本**，**JSON 文本 → HTML 安全文本**。

**第一层 `json.dumps(obj, ensure_ascii=False, indent=2)`**（序列化，把 Python 对象变成字符串）：

| 参数 | 传的值 | 含义 |
|---|---|---|
| 第 1 位置参数 | `exchange` | 要序列化的字典 |
| `ensure_ascii` | `False` | 默认 True 会把中文转成 `\u5f20\u4e09`；设 False 才保留中文 |
| `indent` | `2` | 默认 None（挤成一行）；设 2 表示缩进换行，报告里可读 |
| `sort_keys` | 未传（False） | 设 True 则键按字母排序，字段位置固定便于比对 |
| `default` | 未传 | 遇到 datetime/bytes 等类型时的转换函数；我们已用 `str()` 提前处理 body |

**第二层 `html_lib.escape(s, quote=True)`**（`import html as html_lib` 起的别名）：

| 原字符 | 替换成 | 不转义的后果 |
|---|---|---|
| `&` | `&amp;` | 被当成实体引用 |
| `<` | `&lt;` | 被当标签开头，`<script>` 直接执行 |
| `>` | `&gt;` | 标签结尾，结构错乱 |
| `"` | `&quot;` | 提前闭合属性值 |
| `'` | `&#x27;` | 同理 |

| 参数 | 传的值 | 含义 |
|---|---|---|
| 第 1 位置参数 | `json.dumps(...)` 的结果 | 待转义字符串 |
| `quote` | 未传（True） | 连 `"` `'` 一起转；设 False 只转 `& < >` |

**为什么先 dumps 再 escape**：`escape` 只接受字符串，不认 dict，所以必须先 dumps；而转义只对"最终要插入 HTML 的那份文本"做一次，最省事。

**对比例子**：

```python
exchange = {"status": 200, "resp_text": '<b>"error"</b>'}
json.dumps(exchange, ensure_ascii=False, indent=2)
# '{\n  "status": 200,\n  "resp_text": "<b>\\"error\\"</b>"\n}'
```

塞进 `<pre>` 后，`<b>` 会被浏览器当标签执行（报告布局被搅乱甚至 XSS）。转义后显示效果不变，但浏览器只当普通文字。

**一句话**：`json.dumps` 解决"字典怎么变成能写进文件的文本"，`html.escape` 解决"这段文本怎么塞进 HTML 才不炸"。

### 10.4 `pytest_terminal_summary` 写在哪、要不要装饰器

- **写在 `conftest.py` 末尾**（和 `pytest_runtest_makereport` 并列）
- **不需要任何装饰器**——pytest 靠函数名（`pytest_` 开头）+ 参数名匹配 hookspec 自动绑定

装饰器只在三种情况需要：

| 需求 | 写法 |
|---|---|
| 要在其他插件**之前**执行 | `@pytest.hookimpl(tryfirst=True)` |
| 要在其他插件**之后**执行 | `@pytest.hookimpl(trylast=True)` |
| 要包裹钩子、读返回结果 | `@pytest.hookimpl(hookwrapper=True)` |

```python
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """跑完在控制台末尾打印证据文件数量"""
    if os.path.isdir(ARTIFACT_DIR):
        files = [f for f in os.listdir(ARTIFACT_DIR) if f.endswith(".json")]
        terminalreporter.write_line(f"artifacts 目录共 {len(files)} 个证据文件")
```

| 参数 | 用途 |
|---|---|
| `terminalreporter` | 往控制台写内容，`write_line()` 就是它 |
| `exitstatus` | 退出码：0 全通过、1 有失败、2 中断、5 无用例 |
| `config` | 本次运行的全局配置，可取 `config.getoption(...)` |

**要命的细节**：用不到的参数可以省略，但**名字必须对**。写成 `reporter` 就绑不上，函数永远不执行，而且**不报错**——这是 hook 实现最常见的静默失败。

### 10.5 artifacts 会无限增长

实测某次全量跑后打印 `artifacts 目录共 19 个证据文件`——每跑一次 `--runxfail`（或任何真失败）就新增一个，文件名精确到秒不覆盖，越攒越多。CI 每天跑几百次，一个月上千个，目录难看且拖慢 `os.listdir`。

| 治理方案 | 做法 | 适用 |
|---|---|---|
| 按批次建子目录 | `artifacts/20261111_221949/test_fail_dump.json` | 推荐：一次运行一个目录，报告能精确对应批次 |
| 保留最近 N 天 | 启动时删 7 天前的文件 | 简单，但历史证据会丢 |
| 只保留失败用例 | 通过用例不落盘（现状）+ 按批次归档 | 已有基础 |

配合 `.gitignore` 忽略 `artifacts/`、`report_*.html`、`logs/`，产物不进仓库。此项留到第 8 周"框架分层"时正式落地。

## 十一、今日战绩与明日预告

第 7 周累计（截至 Day40）：

| 项 | 数量 |
|---|---|
| 全量用例 | 48 passed |
| 环境挂起 | 2 skipped |
| 复习挂起 | 7 xfailed |
| 交付物 | 1 份单文件 HTML 报告（含内嵌证据能力） |

**Day41~42：第 7 周复盘大考**，考点覆盖 Day37 配置分离（三层模型 / `--env` / 白名单）、Day38 日志（三层分工 / `caplog` / 两道过滤）、Day39 落盘（`hookwrapper` / `when` 三值 / 文件名安全化）、Day40 报告（extras 类型 / xfail 语义 / bat 装配）。

---

*笔记由 AI 根据当日学习内容整理。*
