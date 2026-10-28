# Day30 学习笔记：框架工程化整合（第 5 周收尾）

> 日期：2026-10-29
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 5 周 · Day30
> 状态：✅ run_tests.bat 一键跑通（0 failed）；自测 5/5 满分
> 里程碑：5 周所学组装成"标准跑法"——一条命令跑全量+出报告

---

## 一、今日目标

把数据驱动、fixture、标记、报告组装成一套标准跑法：
1. 项目分层思维（什么放哪）
2. 一键运行脚本 run_tests.bat + 报告归档
3. 冒烟 vs 全量标记体系

## 二、今日涉及文件

| 操作 | 文件 | 改动 |
|---|---|---|
| 【新建】 | `run_tests.bat` | 一键运行（全量+报告+打开） |
| 【新建】 | `day30_homework.py` | 冒烟/全量标记练习 |
| 【修改】 | `day28_homework.py` | 3 个演示用例加 xfail |
| 【生成】 | `report_时间戳.html` | 报告归档 |

## 三、知识点 1：项目分层思维

| | 学习期（扁平） | 真实项目（分层） |
|---|---|---|
| 用例 | 根目录 dayXX.py | `tests/` |
| 框架 | api_client.py（根目录） | `core/` |
| fixture | conftest.py | 根目录 conftest.py |
| 配置 | config/ | config/ |
| 数据 | data/ | data/ |
| 报告 | （无） | `report/` |
| 运行 | （手敲） | `run_tests.bat` |

**核心心法**：改数据不动用例、改框架不动用例、改用例不动配置——**一处改动只影响一类文件**。

## 四、知识点 2：标准跑法（三种场景三条命令）

```
① 日常回归：python -m pytest tests/ -v --tb=short
② 冒烟测试：python -m pytest tests/ -m smoke -q
③ 全量交付：run_tests.bat（一键 + 报告）
```

**冒烟测试（smoke）**：核心功能"过一遍就跑"（登录→主流程通=系统活着），改动后先冒烟再全量。

## 五、知识点 3：run_tests.bat 一键脚本（完整版）

```bat
@echo off
REM ============================================
REM testopen-study one-click: full tests + HTML report
REM Usage: double-click or type run_tests.bat
REM Prereq: mock_server.py running on port 8000
REM ============================================
set PYTHON=C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe

for /f %%i in ('powershell -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i

echo [1/2] Running all tests...
%PYTHON% -m pytest day25_homework.py day27_homework.py day28_homework.py day30_homework.py -v --tb=short --html=report_%TS%.html --self-contained-html

echo [2/2] Done. Report: report_%TS%.html
start report_%TS%.html
pause
```

- `set PYTHON=...`：统一解释器（防 Anaconda 雷）
- `for /f ... Get-Date`：生成时间戳（报告留痕不覆盖）
- `--tb=short`：简洁报错；`--self-contained-html`：单文件可分享
- **bat 一律英文**（中文进 bat = GBK 乱码雷）

## 六、今日实战坑记录

### ① pytest 全 404 排查链（定案方法比答案重要）

现象：pytest 里所有接口 404，pytest 外验证脚本 200/401 正常。
排查三步：netstat 看端口谁在听 → 验证脚本直接看返回体 → 确认 mock 启动。
**核心认知：404 = 有服务在响应但不是你的 mock**（连接错误才是没人听）；"以为 mock 开着" ≠ mock 真在服务。

### ② Session cookie ≠ Bearer 认证（认证错位）

```python
s = requests.Session()
s.post("/login")        # ✅ Set-Cookie 自动进 session
s.get("/get_user")      # ❌ session 带 Cookie，但 mock 只看 Authorization: Bearer 头 → 401
```

KeyError 'name' 的真相：返回的是 401 body（无业务字段）。
**规律**：登录拿 token → 手动 `headers={"Authorization": f"Bearer {token}"}` → 再请求业务接口。
（真实项目 JWT/Bearer 认证同理；api_client.py 封装了这一切所以好用。）

### ③ 演示用例污染报告 → xfail 挂起

Day28 的"故意失败"用例跑进全量 → 3 failed 假失败。用户选择保留供复习：
**解法 = 标 xfail(reason="...")**——用例保留 + 报告不红（19 passed 2 skipped 5 xfailed 0 failed）。
**真实铁律**：正式用例集不允许"故意失败"的裸用例；保留用 xfail，不要裸 FAILED。

### ④ bat 中文乱码

bat 文件 UTF-8 保存 + cmd 按 GBK 读 → echo 中文变乱码。修法：bat 一律英文。

## 七、自测批改记录（5/5 满分）

| 题 | 判定 | 要点 |
|---|---|---|
| 1 分层核心 | ✅ | 一处改动只影响一类文件 |
| 2 冒烟 + -m smoke | ✅ | 核心链路过一遍；跑标记 smoke 的用例 |
| 3 set PYTHON | ✅ | 统一解释器（防 Anaconda 雷）；for/f 生成时间戳 |
| 4 时间戳报告 | ✅ | 留痕；不带会覆盖 |
| 5 run_tests.bat | ✅ | 完整（英文注释+时间戳+start+pause） |

## 八、明日预告（Day31）

**第 5 周复盘（周日大考 10 题）**：fixture 三件套 / xfail·skip·fail / 断言技巧 / 报告与运行控制 / 框架整合——答完开启第 6 周。

---

*笔记由 AI 根据当日学习内容整理。*
#（注：内容由AI生成）
