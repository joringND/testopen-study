# Day34 学习笔记：数据驱动进阶（第 6 周 Day3）

> 日期：2026-11-04
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 6 周 · Day34
> 状态：✅ 4 passed（1 用例 × 4 组数据）；自测 4.5/5，练习 3 已纠正
> 里程碑：用例逻辑与测试数据彻底分离——一份用例 + N 组数据 = N 条用例

---

## 一、今日目标

把"用例逻辑"和"测试数据"彻底分离：数据文件只存场景，用例只写逻辑；加场景不改代码。

## 二、今日涉及文件

| 操作 | 文件 | 说明 |
|---|---|---|
| 【新建】 | `data/login_cases.json` | 登录场景数据（Day25 的 cases.json 不动，按用途分文件） |
| 【新建】 | `day34_homework.py` | 读 json + parametrize 驱动登录用例 |

> 注意：Day25 已存在 `data/cases.json`（顶层数组 + expect_code 业务码语义），与 Day34 的结构（{"login_cases": [...]} + expected 状态码）不同——**不覆盖、不改名，新建 login_cases.json**。数据文件按用途命名：login_cases.json / order_cases.json / user_cases.json。

## 三、数据驱动核心

```json
{
  "login_cases": [
    {"user": "test",  "pwd": "123",   "expected": 200},
    {"user": "vip",   "pwd": "123",   "expected": 200},
    {"user": "admin", "pwd": "123",   "expected": 401},
    {"user": "test",  "pwd": "wrong", "expected": 401}
  ]
}
```

```python
import json
import requests
import pytest

BASE = "http://127.0.0.1:8000"

def load_cases():
    with open("data/login_cases.json", "r", encoding="utf-8") as f:
        return json.load(f)["login_cases"]

@pytest.mark.parametrize("case", load_cases())
def test_login_ddt(case):
    resp = requests.post(f"{BASE}/login",
                         json={"user": case["user"], "pwd": case["pwd"]},
                         timeout=5)
    assert resp.status_code == case["expected"], f"{case}"
```

**结果**：1 条用例 × 4 组数据 → 4 条独立用例 `[case0]~[case3]`。

## 四、parametrize 与 fixture 参数化（两兄弟）

| | fixture 参数化 | 用例参数化 |
|---|---|---|
| 装饰器 | `@pytest.fixture(params=[...])` | `@pytest.mark.parametrize("参数名", 数据列表)` |
| 参数怎么进 | `request.param` | 直接作为函数参数 |
| 作用对象 | fixture（准备阶段） | 用例（执行阶段） |
| 跑几次 | params 长度 | 数据列表长度 |

## 五、核心坑

### 1. load_cases() 在收集阶段执行

parametrize 的第二个参数（数据）在**收集阶段**执行（import 时）——要先把用例展开才能收集。所以：
- data 文件必须存在，否则**收集就报错**（不是运行报错）
- 文件里是纯数据（JSON），不能写 Python 代码

### 2. 为什么不能用 for 循环替代 parametrize（今日重点）

```python
# ❌ 函数内 for 循环：还是 1 条用例！
def test_login_loop():
    for case in load_cases():
        resp = requests.post(...)
        assert resp.status_code == case["expected"]
```

问题：pytest 里"一条用例 = 一个函数"：
1. **先挂先停**：第 1 组失败 → 整个函数终止 → 后面测不到
2. **报告无法定位**：失败显示一行，看不出哪组数据挂的
3. **隔离性差**：状态互相污染

```python
# ✅ parametrize：N 组数据 = N 条独立用例，隔离、逐条报告
```

**一句话**：for 循环 = 1 条用例跑 N 遍（失败即停、无法定位）；parametrize = N 条独立用例（隔离、逐条报告）。

### 3. 地址/路径"一字不差"坑（第 N 次）

BASE 写成 `http://127.0.0.1:8080` → mock 在 8000 → 连接被拒绝，4 条全挂。**端口也是接头暗号**：`127.0.0.1:8000`，改一个数字就是拒连。

## 六、自测批改记录（4.5/5）

| 题 | 判定 | 要点 |
|---|---|---|
| 1 两兄弟区别 | ✅ | request.param vs 函数参数；fixture vs 用例 |
| 2 收集阶段 | ✅ | 收集时展开；文件不存在收集报错 |
| 3 数据驱动好处 | ✅ | 数据与代码分离；非技术同学加数据就能加用例 |
| 4 代码 | ✅ | 多参数解包 (user,pwd,expected) 正确 |
| 5 加数据自动多跑 | ⚠️ | 要明确答"**会自动**"：数据组数 = 用例条数，加一组→自动多一条，不改代码 |

## 七、明日预告（Day35）

接口框架进阶 Day4：**接口测试断言进阶**——三层断言升级为"响应结构断言"（key 存在性/类型/嵌套），从"断状态码"到"断数据结构"。

---

*笔记由 AI 根据当日学习内容整理。*
