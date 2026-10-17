# Day19 学习笔记：接口测试小项目（综合练习日）

> 日期：2026-10-18
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第3周 · Day19
> 状态：✅ 项目验收通过（4 passed + 1 failed，通过率 80%）
> 里程碑：**第一个"简历级"测试项目完成**

---

## 一、项目目标与验收

**目标**：把 Day12~18 全部技能整合成一个接口自动化测试小项目。

**验收标准**：5 个接口参数化批量跑，报告里 4 passed + 1 failed（故意失败那条），通过率 80%。

**项目文件**：
```
testopen-study/
├─ conftest.py               ← base_url fixture（Day18）
├─ my_tools.py               ← check_status / cal_pass_rate（Day12）
├─ mock_server.py            ← 本地靶场（Day17）
├─ test_api_project.py       ← 项目用例（Day19）
└─ report.html               ← HTML 报告（不提交 Git）
```

## 二、项目实现（最终版）

```python
import pytest
import requests
from my_tools import check_status

@pytest.mark.parametrize("path, expect", [
    ("/status/200", 200),
    ("/status/201", 201),
    ("/status/404", 404),
    ("/status/500", 500),
    ("/status/404", 200),   # 故意失败：模拟"期望和实际不符"的 bug
])
def test_check_status(base_url, path, expect):
    resp = requests.get(base_url + path, timeout=5)
    print(f"{path} → {resp.status_code}")        # 想看输出加 -s
    assert resp.status_code == expect            # pytest 自动判定通过/失败
```

**涉及技能全景**：

| 技能 | 用在哪 | 来源 |
|---|---|---|
| 参数化 | 5 组数据批量跑 | Day16 |
| fixture | base_url 注入（conftest） | Day16/18 |
| requests | 发真实请求 | Day11/17 |
| assert 断言 | 自动判定 | Day15 |
| mock 靶场 | 稳定测试环境 | Day17 |
| HTML 报告 | 结果可视化 | Day18 |
| 失败排查 | 读 pytest 失败报告 | Day15/16/19 |

## 三、今日 3 个坑（重点复盘）

### 🐛 坑1：f-string 内外引号冲突（Python 3.9 限制）

```python
print(f"共检测 {pass_count["pass"]} 个")   # ❌ SyntaxError: f-string: unmatched '['
print(f"共检测 {pass_count['pass']} 个")   # ✅ 内部改单引号
```

- **原因**：Python 3.9 的 f-string 表达式里**不允许和外层相同的引号**（3.12 才放宽）
- **口诀**：外层双引号 → 表达式里用单引号；外层单引号 → 表达式里用双引号

### 🐛 坑2：模块顶层代码在"收集阶段"执行（重点！见第五节）

```python
total = pass_count["pass"] + pass_count["failed"]   # ❌ 顶层 → 收集时执行 → KeyError
print(failure_case)                                  # ❌ 顶层 → 收集时执行 → 打印空列表 []
```

### 🐛 坑3：assert 失败会中断用例，后面的统计是死代码

```python
assert resp.status_code == expect   # ❌ 断言失败 → 抛异常，用例立即中断
if resp.status_code == expect:      #   以下代码永远不执行
    pass_count["pass"] += 1
else:
    pass_count["failed"] += 1       #   死代码
```

## 四、本质认知：pytest 的报告就是统计，别重复造轮子

"通过几个、失败几个、通过率多少"——pytest 和 HTML 报告**自带**（summary: `4 passed, 1 failed`）。自己用全局字典数 pass/fail 是重复劳动，还必然踩坑2和坑3。

**分工原则**：
- **断言** → 交给 pytest（assert 决定用例红绿）
- **统计** → 交给报告（打开就看通过率）
- **代码里自己统计** → 只在"非 pytest 场景"需要（比如 Day12 那种独立脚本）

## 五、pytest 顶层代码知识点（专项详解）

### 1. pytest 跑一个测试文件的三个"时间点"

```
pytest test_x.py
│
├─ ① 收集阶段（collection）
│   ├─ 找到 test_x.py
│   └─ import 这个文件 ← 顶层代码在这里执行！
│
├─ ② 执行阶段（run）
│   └─ 逐个跑 test_ 开头的函数 ← 用例里的代码在这里执行
│
└─ ③ 汇总报告（summary）
    └─ 4 passed / 1 failed
```

**关键**：pytest 是**先 import 文件，再跑用例**。import 时，模块**顶层代码**（不在任何函数/类里的代码）会**立即执行一遍**。

### 2. 顶层代码 = import 文件时就会跑

```python
import pytest          # ① import 时执行 ✅
import requests        # ① import 时执行 ✅

BASE_URL = "http://127.0.0.1:8000"   # ① import 时执行 ✅（常量没问题）

@pytest.fixture
def base_url(): ...    # ① 定义（不执行函数体）✅

@pytest.mark.parametrize(...)
def test_x(...): ...   # ① 定义（不执行函数体）✅

print(failure_case)    # ① import 时执行 ❌ 此时用例还没跑，failure_case 是空！
total = pass_count["pass"] + pass_count["failed"]   # ① import 时执行 ❌ pass_count 是空字典 → KeyError！
```

### 3. 哪些能放顶层，哪些不能（判定标准）

| 能放顶层（收集时执行没问题） | 不能放顶层（依赖用例结果） |
|---|---|
| import 语句 | print 用例统计结果 |
| 常量定义（BASE_URL、路径） | 读取/计算用例产生的变量 |
| fixture / 函数 / 类定义 | 依赖全局计数器结果的代码 |
| @pytest.mark.parametrize 装饰器 | 任何"要等用例跑完才有数据"的代码 |

**判定标准一句话**：**这段代码在"一条用例都没跑"的时候执行，会不会报错/结果对不对？** 会 → 不能放顶层。

### 4. 正确做法

**方案A（推荐）**：打印/统计放进**用例内部**——失败时 pytest 自动显示（Captured stdout call）：

```python
@pytest.mark.parametrize("path, expect", [("/status/404", 200)])
def test_check_status(base_url, path, expect):
    resp = requests.get(base_url + path, timeout=5)
    if resp.status_code != expect:
        print(f"异常接口：{path}，期望 {expect}，实际 {resp.status_code}")  # ✅ 在用例内
    assert resp.status_code == expect
```

**方案B（fixture teardown）**：用 yield 后置做"统计/清理"（更高级，框架阶段会用）：

```python
@pytest.fixture
def report():
    passed = {"n": 0}
    yield passed
    print(f"共通过 {passed['n']} 个")   # yield 之后 = 所有用例跑完 → 这里统计 ✅
```

## 六、学会读 pytest 失败报告（排查口诀）

```python
test_check_status[/status/404-200]        # ① 哪组数据：path=/status/404, expect=200
base_url = 'http://127.0.0.1:8000'        # ② 用例参数值（环境）
path = '/status/404', expect = 200

>       assert resp.status_code == expect
E       assert 404 == 200                  # ③ 期望 200，实际 404
E        +  where 404 = <Response [404]>.status_code   # ④ 实际值来源：resp 状态码
------------------------------------------------ Captured stdout call --------
/status/404 → 404                          # ⑤ 用例的 print 输出
```

**口诀**：`assert X == Y` → X 是实际、Y 是期望 → `where` 告诉实际值哪来的 → `Captured stdout` 是过程 print。一条失败 10 秒定位。

## 七、自测批改记录

| 题 | 判定 |
|---|---|
| ① 接口清单用 fixture 提供 | ✅ 数据集中、改一处全局生效 |
| ② 参数化 vs fixture 数据 | ✅ 批量传参 vs 通用环境 |
| ③ failed 排查步骤 | ✅ 看实际输出 → 判断错误类型 → 整改 |
| ④ 找出期望≠实际的接口 | ⚠️→✅（顶层 print 坑修正：打印放用例内） |
| ⑤ CI 自动化思考 | ✅ 触发/执行/报告/通知/定时 |

## 八、今日新收获

1. **独立交付第一个完整测试项目**（需求 → 设计 → 编码 → 报告）
2. **pytest 执行机制**：收集（import）→ 执行 → 汇总，顶层代码在收集阶段跑
3. **f-string 引号规则**（3.9 限制）
4. **assert 中断语义**：断言失败 = 用例立即结束，后面代码不执行
5. **报告优先读失败**：pytest-html 失败用例高亮排序

## 九、明日预告（Day20）

**第 3 周复盘日**（Day15~19 综合测试）
- 知识地图：pytest 全链路（断言/参数化/fixture/接口/mock/conftest/报告）
- 第 3 周综合测试（10 题）
- 错题回顾：顶层代码、假通过、f-string 引号、协议不匹配、str+int
- 第 3 周毕业 → 第 4 周进入接口框架深化

---

*笔记由 AI 根据当日学习内容整理。*
