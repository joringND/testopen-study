# Day38 学习笔记：日志体系——让失败的用例有迹可循（第 7 周 Day2）

> 日期：2026-11-09
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 7 周 · Day38
> 状态：✅ 2 passed, 1 xfailed；logs/run.log 六条日志成对输出，中文正常
> 课后答疑已补入第十二节：caplog 来源、set_level 语义、日志落点（内存 vs run.log）

---

## 一、今日目标

失败报告只告诉你"断言没通过"，看不出**请求发去了哪、带了什么、回了什么、耗时多少、有没有重试**。日志就是补上这块证据。

## 二、今日涉及文件

| 操作 | 文件 | 说明 |
|---|---|---|
| 【修改】 | `api_client.py` | 加 `import logging/time`、模块级 logger、`_log()` 公共方法；`login` 与 `_request` 都调它 |
| 【修改】 | `pytest.ini` | 加 `log_cli` / `log_cli_level` / `log_file` / `log_file_level` / `log_format` / `log_date_format`（`log_file_encoding` 在 pytest 8 不支持，见第六节更正） |
| 【新建】 | `day38_homework.py` | 3 条用例：logger 名字、请求日志可见（caplog）、失败现场（xfail） |
| 【新建目录】 | `logs/` | pytest 不会自动建，`mkdir logs` |
| 【产物】 | `logs/run.log` | 每次运行累积的应用日志 |

## 三、三层日志分工

| 层 | 在哪写 | 说明什么 | 怎么看 |
|---|---|---|---|
| ① 用例执行日志 | 用例内 `logger.info(...)` | 我准备做什么、拿到了什么 | pytest 捕获 / `-s` / `caplog` |
| ② 请求响应日志 | `api_client._log()` | 实际发了什么、回了什么 | 控制台 + `logs/run.log` |
| ③ 失败现场 | 不用写代码 | 挂的那一刻变量是什么 | `-l` / `--tb` / `--runxfail` |

**分工原则**：越靠框架层，覆盖越广（所有用例自动受益）；越靠用例层，信息越具体。

## 四、为什么要 logging 不用 print

| | print | logging |
|---|---|---|
| 级别 | 无 | DEBUG/INFO/WARNING/ERROR/CRITICAL 可过滤 |
| 时间与出处 | 没有 | 自动带 `asctime` + `name`（模块名） |
| 关闭 | 只能删代码 | 改级别或配置即可 |
| 落文件 | 要自己重定向 | `log_file` 一行配置 |
| 断言 | 无法断言 | `caplog` 可断言"日志里出现过什么" |

## 五、代码改动

### 5.1 api_client.py 顶部

```python
import logging
import time

logger = logging.getLogger(__name__)   # 模块级 logger，__name__ = "api_client"
```

### 5.2 新增 `_log()` 公共方法（放在 `_request` 之前）

```python
    def _log(self, method, path, resp, cost):
        """统一请求日志格式——所有发请求的地方都调它"""
        logger.info(f"{method} {path} -> {resp.status_code} {cost}ms")
        logger.debug(f"resp={resp.text[:200]}")
```

### 5.3 `login()` 里调用

```python
        t0 = time.time()
        resp = self.session.post(
            f"{self.base_url}/login",
            json={"user": user, "pwd": pwd},
        )
        cost = int((time.time() - t0) * 1000)
        self._log("POST", "/login", resp, cost)      # ← 新增
```

### 5.4 `_request()` 里调用

```python
        self._log(method, path, resp, cost)
```

**为什么要抽 `_log`**：日志格式只定义一次。复制一份到 `login` 里，两处格式迟早漂移——今天就是漂移导致的（少个空格就出现 `2001ms`）。

### 5.5 ⚠️ 不要踩的递归陷阱

`_request` 里有懒登录：

```python
if not self.token:
    self.login()
```

如果反过来把 `login` 改成调 `self._request("POST", "/login", ...)`，就形成：

```
_request → login → _request（还没 token）→ login → ...
```

**RecursionError 无限递归**。所以 `login` 直接发请求 + 调 `_log`，不经过 `_request`。真要走 `_request`，必须加 `_skip_login=True` 参数跳过懒登录。

## 六、pytest.ini 日志配置

```ini
log_cli = true
log_cli_level = INFO
log_file = logs/run.log
log_file_level = INFO
log_format = %(asctime)s %(levelname)s %(name)s: %(message)s
log_date_format = %Y-%m-%d %H:%M:%S
```

| 选项 | 作用 |
|---|---|
| `log_cli` | 实时输出到控制台（默认 false） |
| `log_cli_level` | 控制台显示的最低级别 |
| `log_file` | 落盘路径，**目录必须已存在** |
| `log_file_level` | 文件记录的最低级别 |
| `log_format` / `log_date_format` | 每行格式与时间格式 |

> ⚠️ **更正（Day39 实测发现）**：`log_file_encoding` **不是 pytest 8.4.2 支持的选项**，写上会报
> `PytestConfigWarning: Unknown config option: log_file_encoding`。
> pytest 8 的日志文件默认就是 UTF-8，**不需要也无法通过 ini 指定编码**，直接删掉这一行即可。
> 若必须自定义编码，只能自己挂 `logging.FileHandler(path, encoding="...")`。

命令行等价写法：`--log-cli-level=DEBUG`、`--log-file=logs/run.log`、`--log-level=INFO`。

## 七、失败现场

```bash
# 显示每个失败用例的局部变量（resp / data / logger 的值）
pytest day38_homework.py -l

# 让 xfail 用例真的失败一次，才能看到失败现场
pytest day38_homework.py --runxfail -l

# 控制堆栈长度
pytest day38_homework.py --tb=short
```

## 八、今日五个坑

### 1. 日志字段没有分隔符 → 数值粘连产生歧义

```
f"{method}{path}->{resp.status_code}{cost}ms"   →  GET/get_user->2001ms
f"{method} {path} -> {resp.status_code} {cost}ms"  →  GET /get_user -> 200 1ms
```

`2001ms` 到底是"状态码 200 + 1ms"还是"耗时 2001ms"？**日志字段之间必须有分隔符**。

### 2. `log_file` 配了但没建 logs 目录

pytest 不会自动创建父目录，路径不存在会报错/写不进。先 `mkdir logs`。

### 3. `type logs\run.log` 中文乱码

`鎷垮埌鐢ㄽ户鏁版嵁` = UTF-8 文件被 GBK 终端解释。文件没坏，是**显示问题**：

```powershell
chcp 65001
type logs\run.log
# 或
Get-Content logs\run.log -Encoding UTF8
```

同类历史坑：bat 中文 echo 乱码、GBK 读 UTF-8 的 ini。

### 4. 日志缺口：`login` 不走 `_request`

初始只有 `GET /get_user`，没有 `POST /login`——登录是独立 `session.post`，日志断了。修法：抽 `_log` 两边共用（注意上面的递归陷阱）。

### 5. `resp.status_info` 不存在 + 顶层 `client.get_user()` 惹祸

- requests 的 `Response` 只有 `status_code`（数字）与 `reason`（短语），**没有 `status_info`**
- `api_client.py` 顶层写 `client.get_user()` 会在 **import 时真发请求**，pytest 加载 conftest 时就炸，报错被包装成 `ImportError while loading conftest`，真实原因埋在深栈里

修法：

```python
if __name__ == "__main__":
    client = ApiClient("http://127.0.0.1:8000")
    client.get_user()
```

**import 只加载定义，不执行动作**——与 Day37 练习的顶层 `print` 同一类问题，只是这次带上了真实网络请求。

## 九、最终日志样子

```
2026-11-09 23:44:23 INFO api_client: POST /login -> 200 4ms
2026-11-09 23:44:23 INFO api_client: GET /get_user -> 200 2ms
2026-11-09 23:44:23 INFO api_client: POST /login -> 200 3ms
2026-11-09 23:44:23 INFO api_client: GET /get_user -> 200 2ms
2026-11-09 23:44:23 INFO day38_homework: 拿到用户数据：{'code': 0, 'name': '张三', 'age': 27}
```

读日志的正确顺序：**先看 POST /login 成不成功，再看 GET**——调用链清楚暴露。第三条来自用例自身 logger（`day38_homework`），说明 `getLogger(__name__)` 的模块名机制生效。

## 十、练习答案

**1. 慢请求 WARNING**（写在 `_log` 里）：

```python
    def _log(self, method, path, resp, cost):
        logger.info(f"{method} {path} -> {resp.status_code} {cost}ms")
        if cost > 500:
            logger.warning(f"{method} {path} -> {resp.status_code} {cost}ms 慢请求")
        logger.debug(f"resp={resp.text[:200]}")
```

**2. `--log-cli-level=DEBUG` 比 INFO 多了什么**

- 我们自己的 `resp={resp.text[:200]}`（响应体）
- 第三方库的 DEBUG：urllib3 / requests 打连接建立、header、socket 细节——输出量暴增

**3. `caplog.set_level(logging.INFO, logger="api_client")` 不写 `logger=` 会怎样**

抓取**所有 logger** 的 INFO 及以上，包括 pytest 自身与 urllib3 的日志 → `caplog.records` 混入噪声。`any(...)` 型断言仍可能过，但 `len(texts) == 1` 这类精确断言会挂。**指定 logger 名 = 精准捕获**。

## 十一、自测答案

**1. print vs logging 两个核心区别**
① logging 有级别可过滤，print 没有；② logging 自带时间/模块出处，还能一行配置落文件，print 都不能。

**2. 级别由低到高**
`DEBUG < INFO < WARNING < ERROR < CRITICAL`。日常每条请求用 **INFO**。

**3. 日志实时上控制台的两种做法**
- ini：`log_cli = true` + `log_cli_level = INFO`
- 命令行：`--log-cli-level=INFO`

**4. `resp.text[:200]` 为什么截断**
上传/下载等接口响应可能几十 KB，全量打日志会撑爆磁盘、拖慢运行；200 字符足够定位问题。

**5. `_request` 里加快日志**

```python
        t0 = time.time()
        resp = self.session.request(method, f"{self.base_url}{path}", timeout=5, **kwargs)
        cost = int((time.time() - t0) * 1000)
        self._log(method, path, resp, cost)     # 或直接 logger.info(...)
```

`logger` 来自模块级 `logger = logging.getLogger(__name__)`（`__name__` = `"api_client"`）。

## 十二、答疑补充：caplog 机制三问

### 12.1 `caplog` 是从哪个模块引入的？

**不是 import 来的，是 pytest 内置的 fixture**，用例参数里写个 `caplog` 就自动注入：

```python
def test_request_log_visible(client, caplog):   # ← 写参数名就行
```

| 名字 | 来源 | 要不要 import |
|---|---|---|
| `caplog` | pytest 内置 fixture（源码定义在 `_pytest/logging.py` 的 `LogCaptureFixture`） | **不要** |
| `logging.INFO` | Python 标准库 `logging` | **要** `import logging` |
| `pytest` | 第三方包 | 要 `import pytest`（用 `pytest.mark.xfail` 时） |

所以 `day38_homework.py` 顶部的 `import logging` 是为了 `logging.INFO` 这个常量，**和 `caplog` 本身无关**。

同类内置 fixture（都不用 import）：`capsys` / `capfd` / `tmp_path` / `monkeypatch` / `request` / `pytestconfig`。

确认清单：

```powershell
& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pytest --fixtures | findstr caplog
```

**别 import 它的类型**：

```python
from _pytest.logging import LogCaptureFixture   # ⚠️ 内部 API，不推荐
```

`_pytest` 是内部实现模块，路径和接口不保证跨版本稳定。项目代码直接写 `caplog` 即可。

`caplog` 常用成员：`set_level()` / `records`（原始 LogRecord 列表）/ `text`（全部日志文本）/ `messages`（消息列表）。

### 12.2 `caplog.set_level(logging.INFO, logger="api_client")` 是什么意思？

**临时把 `api_client` 这个 logger 的级别降到 INFO，让 INFO 日志能被捕获。**

```python
caplog.set_level(logging.INFO, logger="api_client")
                 ↑              ↑
            捕获阈值         只作用于哪个 logger
```

| 参数 | 含义 |
|---|---|
| `logging.INFO` | 阈值，不是"只抓 INFO"，而是**INFO 及以上全抓**（INFO/WARNING/ERROR/CRITICAL），DEBUG 不要 |
| `logger="api_client"` | 只改名为 `api_client` 的 logger；不写则改 root logger（波及所有 logger） |

**为什么必须调这一行**：logging 的级别是在**源头**过滤的，不是捕获时过滤。

```
logger.info(...) → logger 的 effective level 是 WARNING？
                    ├─ 是 → 记录根本不创建，直接丢弃
                    └─ 否 → 创建 LogRecord → 传给 handler → caplog 收下
```

root logger 默认 **WARNING**，`api_client` 继承它，所以 `logger.info(...)` 在源头就被丢掉，`caplog.records` 里空空如也。`set_level` 就是临时把这个 logger 的级别调到 INFO。

**不写 `logger=` 的后果**：

```python
caplog.set_level(logging.INFO)     # root 变 INFO → 所有 logger 的 INFO 都进来了
```

`caplog.records` 会混进 urllib3、pytest 自身的 INFO；`any(...)` 型断言能过，但 `len(texts) == 1` 这类精确断言立刻挂。**指定 `logger=` = 精准捕获**。

**作用范围**：`caplog` 是 function 作用域 fixture，每个用例开始前重置、结束后恢复，互不污染。

**常用变体**：

```python
caplog.set_level(logging.INFO, logger="api_client")        # 抓 INFO 及以上（日常）
caplog.set_level(logging.DEBUG, logger="api_client")       # 连 req/resp 明细也抓
caplog.set_level(logging.ERROR)                            # 不指定 → root，只抓 ERROR
caplog.set_level(logging.INFO, logger=logging.getLogger("api_client"))  # 传对象，等价
```

一句话记法：`caplog` 是**捕鱼网**，`set_level` 决定**网眼多大**，`logger=` 决定**在哪片水域下网**。

### 12.3 抓到的日志存在哪里，是 `run.log` 吗？

**不是。`caplog` 抓的日志存在内存**，只在当前用例执行期间存在，用例结束即消失。

三个内存位置：

```python
caplog.records    # LogRecord 对象列表（最原始，可取 .getMessage() / .levelname）
caplog.text       # 全部日志拼成一段字符串
caplog.messages   # 只取消息文本的列表
```

`caplog` 与 `run.log` 是**两条独立通道**：

| | caplog | logs/run.log |
|---|---|---|
| 存哪 | 内存 | 磁盘 |
| 存多久 | 只在当前用例内 | 整个会话，跨运行累积 |
| 谁配 | 用例里 `set_level` | pytest.ini 的 `log_file` |
| 干什么用 | **给断言用**（"日志里出现过什么"） | **给人查**（事后排障） |

**同一条日志，同时有三条去向**：

```
logger.info("GET /get_user -> 200 2ms")
   │
   ├─→ 控制台         （log_cli=true 决定）
   ├─→ logs/run.log   （log_file 决定，持久）
   └─→ caplog.records （用例有 caplog 参数时才挂这个 handler，内存）
```

`caplog` 是"额外挂一个钩子"，不是"替换输出方式"——所以 run.log 里照样有那条日志，两者互不干扰。

**⚠️ 一个副作用**：`caplog.set_level()` 改的是 **logger 本身的级别**（源头那道关），不只影响 caplog：

```python
caplog.set_level(logging.DEBUG, logger="api_client")
```

- `caplog.records` 多出 DEBUG 记录 ✅
- 这些 DEBUG 也会流向 `run.log`，但还要过 `log_file_level` 这道关（`log_file_level = INFO` 时在 handler 层再被滤掉）

完整的过滤是**两道**：

```
logger 级别（源头）  →  handler 级别（出口：控制台 / 文件 / caplog 各一道）
```

`caplog.set_level` 动第一道，`log_cli_level` / `log_file_level` 动第二道。理解这两道，才明白"我明明 set_level 到 DEBUG 了，run.log 里却没有 DEBUG"。

**验证代码**（可加进 day38_homework.py）：

```python
def test_where_logs_go(client, caplog):
    caplog.set_level(logging.INFO, logger="api_client")
    client.get_user()
    logger.info("用例自己的日志")
    assert len(caplog.records) >= 3      # login + get_user + 自己这条
```

跑完再 `type logs\run.log`：文件里同样有这些行。**一个在内存里张网，一个往磁盘上刻字，两件事。**

## 十三、明日预告（Day39）

日志有了，接着做**失败现场落盘**：用例失败时自动保存响应 body / 截图 / 请求参数到 `artifacts/`，并把日志嵌进 HTML 报告——别人拿着报告就能复现。

---

*笔记由 AI 根据当日学习内容整理。*
