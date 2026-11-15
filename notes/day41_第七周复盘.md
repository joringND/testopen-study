# Day41 学习笔记：第 7 周复盘大考（配置 · 日志 · 证据 · 报告）

> 日期：2026-11-15
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 7 周 · 复盘日
> 成绩：**83 / 100**（及格线 80）→ 初考 79 + 补考 4 → **通过，进入第 8 周**
> 本周战绩：全量 `48 passed, 2 skipped, 7 xfailed`；11 个测试文件；一条命令出单文件报告

---

## 一、考试概况

| 项 | 内容 |
|---|---|
| 范围 | Day37 配置分离 / Day38 日志 / Day39 落盘 / Day40 报告装配 |
| 题量 | 10 题（9 道问答 + 1 道综合代码） |
| 方式 | 闭卷、限时 60 分钟 |
| 得分 | 83 / 100（初考 79 + 补考 4） |
| 判定 | ✅ 通过，进入第 8 周 |

**得分分布**

| 题 | 考点 | 得分 | 扣分原因 |
|---|---|---|---|
| Q1 | 三层配置模型 | 7 | "环境感知该收在哪层"回答不准 |
| Q2 | FAILED vs ERROR、白名单 | 8 | 白名单理由笼统 |
| Q3 | 三层日志分工 | 8 | 缺"隐藏请求"与"格式统一可断言" |
| Q4 | caplog 来源与 set_level | **8**（补 +3） | 初考错在"需要 import"；补考已纠正，仅"提高门槛"用词不准 |
| Q5 | 两道过滤 | 9 | 表述可更精确 |
| Q6 | hookwrapper / when | 9 | "直接 return 会被覆盖"表述含糊 |
| Q7 | 文件名安全化 / bytes | 9 | 漏了 `/` 的来历 |
| Q8 | extras.text vs html | 10 | 满分 |
| Q9 | xfail 与 failed | 10 | 满分（条件改法写得完全对） |
| Q10 | 综合代码 | **5**（补 +1） | 补考补上了判断段，验收点仍未写 |

**结构性问题**：概念题 8 道平均 8.75 分（扎实），综合题 4 分。**"知道"没问题，"落成完整代码"还差一截**——这是第 8 周要专门练的。

---

## 二、第七周知识地图

```
        ┌─────────────── 一条链的四段 ───────────────┐
        
  [Day37 配置]        [Day38 日志]        [Day39 证据]        [Day40 报告]
  决定打哪里           记录过程            回答为什么挂        讲给别人听
       │                   │                   │                  │
  --env + env.json    logger + caplog    hook + last_exchange   extras + bat
       │                   │                   │                  │
       └───────────────────┴─────────┬─────────┴──────────────────┘
                                     ↓
                        一份可交付的单文件报告
                    （地址正确 + 日志完整 + 证据在旁）
```

| 模块 | 核心机制 | 最容易错的地方 |
|---|---|---|
| 配置分离 | `pytest_addoption` 注册 `--env` → `env_name` fixture → `base_url` 从 json 取址 | 白名单写死环境名，与 json 脱节 |
| 日志体系 | 三层分工 + 两道过滤（logger 源头 / handler 出口） | 以为 caplog 要 import；以为改 handler 级别能救 INFO |
| 失败落盘 | `hookwrapper` + `when == "call"` + `item.funcargs` + `last_exchange` | 在 setup/teardown 也落盘；filename 不转义 |
| 报告装配 | `report.extras` + `extras.html` + `run_tests.bat` 分流 | 用 `extras.text`，self-contained 下不可见 |

---

## 三、三个失分点详解

### 3.1 Q1：环境感知应该收在哪一层（扣 3 分）

**你的答案**：三层描述全对，但"应该在配置层做区分"。

**问题**：`config/env.json` 的职责只有一件事——**存地址**。它不该承担"哪些用例能跑"的决策，塞进去就变成"配置层管业务"，是职责越界。

**正确做法**：用例体里**不写任何 if**，把环境感知收敛到两个允许的位置：

```python
# 位置一：模块/函数级 marker（声明式，最干净）
pytestmark = pytest.mark.skipif(
    os.getenv("PYTEST_ENV", "test") != "test",
    reason="只在 test 环境跑真实请求",
)
```

```python
# 位置二：fixture 里主动 skip（用例完全不知道环境存在）
@pytest.fixture
def real_client(base_url, env_name):
    if env_name != "test":
        pytest.skip(f"{env_name} 是占位环境，不发真实请求")
    return ApiClient(base_url)
```

**记住一句话**：用例层"不知道环境存在"是对的；但**跳过决策也不是配置层的活**——它在 fixture / marker 层。

### 3.2 Q4：caplog 根本不需要 import（扣 5 分）

三个小问逐个纠正：

| 小问 | 你的答案 | 正确 |
|---|---|---|
| 从哪 import | "pytest 模块导入的" | **不需要 import**。`caplog` 是 pytest 内置 fixture，类型 `_pytest.logging.LogCaptureFixture`，写成用例参数就自动注入。`pytest.caplog` 这个属性不存在，`from pytest import caplog` 会 `ImportError` |
| 为什么 set_level | "指定文件和日志等级，消除噪声" | 只对了一半：不是"文件"，是**指定 logger 名称**；核心原因是**日志在源头就被级别过滤**——root 默认 WARNING，`logger.info(...)` 根本不会生成 record，caplog 的 handler 什么都收不到。必须先把 `api_client` 这个 logger 的级别降到 INFO。<br>**补考时的表述"从源头提高日志门槛"方向对了，但用词反了**：这里是**降低**级别门槛（WARNING → INFO），让 INFO 的 record 能被生成；说"提高门槛"听起来像是过滤更严，恰好会把 INFO 挡在外面 |
| 存在哪 | "内存中，不是 run.log" | ✅ 完全正确 |

一句话：

> `set_level(logging.INFO, logger="api_client")` 是在**源头开闸**，不是"设个过滤减少噪声"。不开闸，下游（控制台/文件/caplog）全都是空的。

### 3.3 Q10：综合题只交了 1.5 个片段（扣 6 分）

题目要三片段 + 验收点，实际交付：

| 要求 | 你交的 | 判 |
|---|---|---|
| bat 分流行 | `if not "%ENV%"=="test" set FILES=day37_homework.py` | ✅ 完整 |
| hook 失败判断段 | 空白 | ❌ 未交 |
| extras 内嵌三行 | 写了，但**漏 `report.extras = extra_list`** | ⚠️ 半对 |
| 验收点（≥3 条） | 空白 | ❌ 未交 |

**正确的 hook 判断段**（含 xfail 兼容的可选写法）：

```python
    # 必须只在 call 阶段
    if report.when != "call":
        return

    # 基础版：只处理真失败
    if not report.failed:
        return

    # 可选增强版（想连 xfail 也留证时，替换上面两行为下面这段）
    # if not (report.failed or getattr(report, "wasxfail", False)):
    #     return
```

**extras 三行必须补上赋回**：

```python
    extra_list = getattr(report, "extras", [])
    escaped = html_lib.escape(json.dumps(exchange, ensure_ascii=False, indent=2))
    extra_list.append(extras.html(...))
    report.extras = extra_list        # ← 漏了这行，报告里不会有内容
```

**原因**：`TestReport` 默认没有 `extras` 属性，`getattr` 返回的是新建的空列表，它与 `report` 毫无关系。不赋回，append 的内容全丢，**而且不报错**——报告里静悄悄什么都没有。

**验收点该写什么**（至少要能落到命令/现象）：

1. 跑 `.\run_tests.bat` → 控制台 `48 passed, 2 skipped, 7 xfailed`，且末尾出现 `artifacts 目录共 N 个证据文件`
2. 单独跑 `day39_homework.py --runxfail --html=report_debug.html --self-contained-html` → 控制台有 `失败现场已保存: ...`，`dir artifacts` 出现**新时间戳**的 json
3. 打开报告 Ctrl+F 搜「失败现场」→ 命中，且下方紧跟 `AssertionError` 与 `Captured log call`
4. 跑 `.\run_tests.bat pre` → `2 passed, 1 skipped`（分流生效），报告名含 `pre`
5. 反向验证：把 `extras.html` 换回 `extras.text` → 报告里该位置变空白（证明类型选择是关键）

---

## 四、本周踩坑总账（12 条）

### Day37 配置分离

1. **`fixture 'env_name' not found`**：只改了 `base_url` 内部，忘了定义 `env_name`；`available fixtures` 列表能直接看出缺哪个
2. **白名单写死环境名**：`("test","pre","prod")` 与 env.json（只有 test/pre）脱节 → `--env prod` 时 1 failed 2 errors，自相矛盾；改为 `assert env_name in cfg`

### Day38 日志体系

3. **`GET/get_user->2001ms`**：日志字段无分隔符，`200` 与 `1ms` 粘连；断言 `"-> 200 "`（带空格）才匹配
4. **`type logs\run.log` 中文乱码**：UTF-8 文件被 GBK 终端解释；用 `chcp 65001` 或 `Get-Content -Encoding UTF8`
5. **`resp.status_info` 不存在**：应为 `status_code`；且顶层 `client.get_user()` 让加载 conftest 时真发请求，报错被包装成 `ImportError while loading conftest` → 收进 `if __name__ == "__main__":`
6. **`log_file` 必须先 `mkdir logs`**，否则文件写不进去

### Day39 失败落盘

7. **`log_file_encoding` 不是 pytest 8 选项**：静默忽略 + warning；pytest 8 日志默认 UTF-8
8. **`item.name` 含 `[` `]`**：Windows 文件名非法，必须安全化
9. **`req.body` 可能是 bytes**：`json.dump` 抛 `TypeError`，用 `str()` 包一层

### Day40 报告装配

10. **`run_test.bat` 拼错** → `not recognized`：文件名即路径，先 `dir /b *.bat` 看真实名字
11. **`extras.text` 在 self-contained 下不可见**：4.0 起 text/json/image 落成 assets 外部文件，报告只放链接且不内联；必须用 `extras.html`
12. **`--env pre` 全红（16 failed）**：假域名 DNS 解析失败，是把"换地址"当成了"地址可用"；且 **xfail 会吞掉 ConnectionError**，把环境故障伪装成预期失败

---

## 五、本周战绩

| 项 | 数量/说明 |
|---|---|
| 测试文件 | 11 个（day25/27/28/30/32/33/34/35/37/38/39） |
| 全量结果 | **48 passed, 2 skipped, 7 xfailed** |
| 交付物 | 单文件 HTML 报告（内嵌失败证据） |
| 一键入口 | `run_tests.bat`（test/pre 双环境分流） |
| 新增能力 | 配置可切 / 日志可见 / 证据可留 / 报告可交付 |

**第 7 周的核心收获不是四个知识点，而是一个判断力**：出问题时先问"这是哪一层的问题"——配置层（地址不对）、日志层（没打出来）、证据层（没留）、报告层（没渲染）。四层定位法比背 API 有用。

---

## 六、补考记录（题目 · 作答 · 批改 · 标准答案）

### 6.1 补考题目（原题）

**Q4（10 分）**：`caplog` 是从哪个模块 import 的？为什么必须写 `caplog.set_level(logging.INFO, logger="api_client")`？抓到的日志存在哪里，是不是 `logs/run.log`？

**Q10（10 分）**：写出 `conftest.py` 里 hook 的失败判断段（call 阶段 + 只处理失败，含 xfail 兼容的可选写法）；再给 3 条验收点，每条要能落到具体命令或具体现象。

### 6.2 我的作答（原话）

**Q4 原答**：

> 不需要 import，caplog 是 pytest 内置 fixture，写成用例参数就会自动注入。`caplog.set_level(INFO, logger="api_client")` 真正解决的问题是从源头提高日志门槛。

**Q10 原答**：

```python
if report.when != "call":
    return
if not report.failed:
    return
```

（验收点未写。）

### 6.3 批改结果

| 项 | 结果 |
|---|---|
| 得分变化 | Q4：5 → 8（+3）；Q10：4 → 5（+1） |
| 总分 | 79 → **83**，通过 |
| 结论 | 概念错已纠正（caplog 不用 import）；判断段写对；**验收点仍缺** |

**逐条评价**：

- ✅ **Q4 两个关键点全对**：caplog 是内置 fixture、写成参数自动注入；set_level 是"从源头"解决，不是在下游设过滤
- ⚠️ **一处用词反了**：说"提高日志门槛"，实际是**降低**级别门槛（WARNING → INFO）——"提高门槛"会把 INFO 挡死
- ✅ **Q10 判断段完全正确**：`when != "call"` 先挡，再挡 `not report.failed`，顺序和条件都对
- ❌ **Q10 验收点仍空白**：本周唯一没落地的要求，也是第 8 周第一课的前置

### 6.4 Q4 标准答案（三小问逐一）

**① 要不要 import：不要。**

`caplog` 是 pytest 的**内置 fixture**，把它写成用例参数名，pytest 就会自动注入，不需要任何 import 语句。它的类型是 `_pytest.logging.LogCaptureFixture`（写用例时用不到这个类型名）。

`from pytest import caplog` 会直接 `ImportError`——`caplog` 不是 `pytest` 模块的属性，只是一个"按名字注册的 fixture"。

**② set_level 真正解决什么：让 record 能被生成。**

日志过滤是**两道串联**的：

```
logger.info(...) 调用
      ↓  第一道：logger 对象自己的 level（isEnabledFor）
  生成 LogRecord ？──否──→ 到此为止，什么都不发生
      ↓ 是
   交给 handler 们
      ↓  第二道：handler.level
  输出到 控制台 / 文件 / caplog
```

关键在于**第一道在源头**：root logger 默认 `WARNING`，`api_client` 继承它，于是 `logger.info(...)` 在**创建 record 之前**就被丢弃——后面所有 handler（包括 caplog 的）都收不到任何东西。

所以 `caplog.set_level(logging.INFO, logger="api_client")` 做的事是：**只把这个 logger 的级别降到 INFO，放行 INFO 级日志**。有效级别 ≈ `max(logger.level, handler.level)`，caplog 自己的 handler 默认是 NOTSET(0)，瓶颈始终在源头。

> 用词纠正：这是**降低**级别门槛（放行更多），不是"提高门槛"（过滤更严）。

**③ 日志存哪：内存。**

- `caplog.records` —— `LogRecord` 对象列表（可取 `.levelname` / `.message` / `.name`）
- `caplog.text` —— 拼好的整段文本
- `caplog.messages` —— 每条日志的 message 字符串列表

与 `logs/run.log` **毫无关系**：那是 `pytest.ini` 里 `log_file` 配的 `FileHandler` 写到磁盘的另一条路。两者都能有，但互不影响。

### 6.5 Q10 标准答案

**判断段**：

```python
    # 必须只在 call 阶段
    if report.when != "call":
        return

    # 基础版：只处理真失败（xfail 的 report 是 skipped，不会进来）
    if not report.failed:
        return

    # 可选增强版：想连 xfail 也留证时，用下面这段替换上面两行
    # if not (report.failed or getattr(report, "wasxfail", False)):
    #     return
```

**内嵌报告时不能漏的一行**：

```python
    extra_list = getattr(report, "extras", [])
    escaped = html_lib.escape(json.dumps(exchange, ensure_ascii=False, indent=2))
    extra_list.append(extras.html(...))
    report.extras = extra_list        # ← 漏了这行，报告里静默无内容
```

原因：`TestReport` 默认没有 `extras` 属性，`getattr` 拿到的是**新建的空列表**，与 `report` 无关；不赋回，append 的内容全丢且不报错。

**3 条验收点（参考答案）**：

| 验收点 | 具体命令 / 现象 |
|---|---|
| ① 全量跑通 | `.\run_tests.bat` → 控制台 `48 passed, 2 skipped, 7 xfailed`，末尾出现 `artifacts 目录共 N 个证据文件` |
| ② 证据真生成 | `day39_homework.py --runxfail --html=report_debug.html --self-contained-html` → 控制台 `失败现场已保存: ...`，`dir artifacts` 出现**新时间戳** json |
| ③ 报告真渲染 | 打开 `report_debug.html`，Ctrl+F「失败现场」命中，且下方紧跟 `AssertionError` 与 `Captured log call` |

加分项（有则更强）：

| 验收点 | 具体命令 / 现象 |
|---|---|
| ④ 分流生效 | `.\run_tests.bat pre` → `2 passed, 1 skipped`，报告名含 `pre` |
| ⑤ 反向证明 | 把 `extras.html` 改回 `extras.text` → 该位置变空白，证明类型选择是根因 |

---

## 七、第 8 周预告：框架分层重构

第 7 周做的是"让框架可运维"，第 8 周要把散在各处的代码**拆成有职责边界的层**：

| 层 | 目录 | 职责 |
|---|---|---|
| 配置层 | `config/` | env.json、pytest.ini |
| 客户端层 | `api_client.py` → `clients/` | 请求封装、认证、日志 |
| 数据层 | `data/` | 用例数据 json |
| 用例层 | `tests/` | 只写业务断言 |
| 支撑层 | `utils/` | 断言工具、日志工具、hook |
| 产物层 | `reports/ artifacts/ logs/` | 按批次归档 |

**Day42 第一件事**：把 `conftest.py` 里混在一起的六件事（addoption、fixture、hook、常量、日志、路径）拆成"插件式"结构，让根 conftest 只留 3 行 import。

---

*笔记由 AI 根据当日考试与批改结果整理。*
