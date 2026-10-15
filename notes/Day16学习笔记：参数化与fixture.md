# Day16 学习笔记：参数化与 fixture

> 日期：2026-10-15
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第3周 · Day16
> 状态：✅ 全部完成（9 passed、自测 5 题全对）

---

## 一、参数化 @pytest.mark.parametrize

**作用**：一条用例定义，N 组数据，自动生成 N 条用例。不用复制粘贴。

```python
import pytest
from my_tools import check_status

@pytest.mark.parametrize("status, expect", [
    (200, "通过"),
    (404, "接口不存在"),
    (500, "服务器错误"),
    (403, "其他异常"),
])
def test_status(status, expect):
    assert check_status(status) == expect
```

**规则**：
- 第一个参数 `"status, expect"`：变量名列表（逗号分隔），**函数参数必须同名接收**
- 第二个参数：数据列表，每个元组是一组数据
- 4 组数据 = 4 条用例（`collected 4 items`）

**运行输出**（每组数据生成一条用例）：
```
test_status[200-通过] PASSED
test_status[404-接口不存在] PASSED
```

## 二、fixture @pytest.fixture

**作用**：测试前的**准备**（连环境/造数据）、测试后的**清理**（关连接/删数据）。

```python
@pytest.fixture
def make_cases():
    print("[准备] 构造测试数据")
    data = [
        {"name": "登录", "status": 200},
        {"name": "下单", "status": 200},
        {"name": "支付", "status": 500},
    ]
    yield data              # yield 前 = 准备；把数据交给用例
    print("[清理] 删除测试数据")  # 用例跑完后执行

def test_count_200(make_cases):   # 参数名 = fixture 名 → 自动注入
    count = 0
    for case in make_cases:
        if case["status"] == 200:
            count += 1
    assert count >= 1
```

**机制**：用例函数参数名 → pytest 自动找同名 fixture → 执行（yield 前）→ 值注入参数 → 用例跑完 → 执行 yield 后（清理）。

## 三、今日错误复盘（重点）

### 🐛 坑1：函数参数"凭空出现" → fixture not found

```python
def test_count_200(make_cases, name, status):   # ❌ name/status 没定义
```

pytest 规则：**用例函数的每个参数名**都会去自动查找同名 fixture 或 parametrize 变量，找不到就报错 `fixture 'name' not found`。

修法：删掉多余参数，遍历时取字段 `case["status"]`。

### 🐛 坑2：print 看不到？→ pytest 输出捕获机制

- 现象：fixture 里的 print 不显示
- 原因：pytest **默认捕获 stdout**，测试通过时不显示（保持输出干净）；**失败时才自动显示**该用例的 print 辅助排查
- 修法：加 `-s` 参数（disable capture）看输出：`pytest 文件 -v -s`

### ⚠️ 坑3：yield 列表包字典 vs 直接 yield 字典

- 造多条数据 → yield 列表，用例遍历
- 造单个对象 → 直接 yield 对象，用例直接用
- 注意不要"多包一层"冗余

## 四、练习批改记录

| 项目 | 判定 |
|---|---|
| 练习1 参数化 check_status×4 | ✅ 4 passed |
| 练习2 参数化加法×3 | ✅ |
| 练习3 fixture 造数据×2 | ⚠️→✅（删 name/status 参数、遍历取 case["status"]） |
| 自测 5 题 | ✅（第5题优化：直接 yield 字典） |

## 五、明日预告（Day17）

**pytest + requests：接口自动化测试初体验**
- 把 Day12 的接口检测工具改造成 pytest 参数化版本
- fixture 提供接口基础 URL / 请求客户端
- 参数化 + requests 组合：5 个接口一条用例跑完
- 企业接口自动化测试的第一块基石

---

*笔记由 AI 根据当日学习内容整理。*
