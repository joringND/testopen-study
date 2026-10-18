# Day20 学习笔记：第 3 周复盘日（pytest 全链路）

> 日期：2026-10-18（周日 · 复盘日）
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 3 周收官
> 状态：✅ 第 3 周毕业（10 题综合测试 10/10）
> 里程碑：pytest 测试框架全链路打通，产出第一个简历级测试项目

---

## 一、第 3 周回顾（Day15~19）

### 知识地图

| 天 | 主题 | 核心技能 |
|---|---|---|
| Day15 | pytest 入门 | 命名规则 / assert 断言 / pytest.raises / -v、-q |
| Day16 | 参数化 + fixture | parametrize 批量 / fixture 准备清理 / yield 前后 / -s |
| Day17 | 接口自动化 | requests + 断言 / status_code / params / mock 服务器 |
| Day18 | conftest + 报告 | fixture 中央仓库 / 全局共享 / pytest-html |
| Day19 | 综合项目 | 独立交付 5 接口项目 / 读失败报告 / 顶层代码机制 |

**主线**：断言（D15）→ 批量/环境（D16）→ 真实请求（D17）→ 工程化（D18）→ 项目（D19）——这就是企业接口自动化测试的最小完整链路。

### 第 3 周产出清单（GitHub 仓库 testopen-study）

```
test_first.py / test_day15.py        ← Day15 入门
day16_test.py                        ← 参数化 + fixture
mock_server.py                       ← 本地靶场（标准库 http.server）
conftest.py                          ← base_url 全局 fixture
day17_request.py                     ← 接口用例
day18_test.py                        ← conftest + 报告
test_api_project.py                  ← ⭐ 简历级接口测试项目
my_tools.py                          ← 工具箱（check_status / cal_pass_rate）
notes/  day15~day20 笔记             ← 20 份学习笔记
```

## 二、第 3 周 12 个坑（必须会认）

1. **目录不对**：不先 cd 项目目录跑 pytest → file or directory not found
2. **假通过**：用例没有 assert → pytest 给 warning，用例白跑
3. **-q 理解**：-v 全量展示、-q 只显示摘要
4. **参数凭空出现**：用例参数必须有来源（同名 parametrize 或 fixture）→ 否则 fixture not found
5. **装饰器只管紧贴函数**：parametrize 只作用于下面第一个函数
6. **URL 多拼 /get**：base_url + path 拼接路径别重复
7. **httpbin 网络不稳**：ReadTimeout / SSLError = 网络层问题，非代码错
8. **WinError 10061**：mock 服务器没启动 / 端口写错
9. **https vs http**：https:// 连明文 http.server → WRONG_VERSION_NUMBER
10. **f-string 引号冲突**：Python 3.9 不允许 f-string 表达式里用外层相同引号
11. **str + int 拼接**：URL 拼路径先 str()
12. **顶层代码收集阶段执行**：pytest 先 import 文件再跑用例（×3 复发）

## 三、综合测试批改记录

| 题 | 判定 | 要点 |
|---|---|---|
| 1 假通过 | ✅ | 没断言 = 用例白跑 + warning |
| 2 参数化 | ✅ | 3 组 = 3 条；只管紧贴函数 |
| 3 -s | ✅ | 关捕获实时显示；默认失败时显示 Captured stdout |
| 4 conftest | ✅ | 自动加载、全局共享、无需 import |
| 5 fixture | ⚠️→✅ | **return 任意类型**：字符串/数字/字典/列表/对象/None |
| 6 参数化断言 | ✅ | check_status 3 组 |
| 7 fixture 定义 | ⚠️→✅ | **只写用例没写 fixture 定义 → not found**（补 @pytest.fixture） |
| 8 pytest.raises | ❌→✅ | **核心错题**（见下节） |
| 9 mock 接口 | ✅ | 4 组参数化 + base_url |
| 10 顶层代码 | ⚠️→✅ | 机制一句话：收集阶段 import 时顶层代码先执行 |

## 四、核心错题复盘：pytest.raises（第 8 题）

### 错误写法（直接 raise = 用例被判 Fail）

```python
@pytest.mark.parametrize("a,b",[(10,5),(2,-1),(3,0)])
def test_safe_divide(a,b):
    if b==0:
        raise ZeroDivisionError("除数不能为0")   # ❌ 直接 raise → 用例 Fail
    return a/b                                  # ❌ 没有 assert → 假通过
```

### pytest.raises 的本质

```
with pytest.raises(ZeroDivisionError):
    safe_divide(10, 0)
```

- **语义**："我预期这里会抛 ZeroDivisionError"
- 异常真的抛了 → 与预期一致 → 用例**通过** ✅（说明除零保护生效）
- 异常没抛 → 该崩的没崩 → 用例**失败** ❌（保护失效 = bug）
- 对比：直接 raise = 用例自己崩 = Fail；pytest.raises 捕获预期异常 = Pass

### 正确写法

```python
def safe_divide(a, b):
    if b == 0:
        raise ZeroDivisionError("除数不能为0")
    return a / b

# 正常除法：参数化批量断言（同一逻辑）
@pytest.mark.parametrize("a, b, expect", [
    (10, 2, 5),
    (9, 3, 3),
    (-6, 2, -3),
])
def test_safe_divide_ok(a, b, expect):
    assert safe_divide(a, b) == expect

# 除零异常：单独一条（不同断言逻辑）
def test_safe_divide_error():
    with pytest.raises(ZeroDivisionError):
        safe_divide(10, 0)
```

### 追问："参数化能写异常用例吗？"

- **能**，但原则是：**参数化 = 同一种断言逻辑的批量数据**
- 正常除法（assert 结果）和除零（pytest.raises）是两种断言逻辑 → **拆开写**
- 进阶写法（带 raises 标志的一锅端参数化）能跑，但测试代码有分支、可读性差，不推荐

## 五、pytest 顶层代码机制（Day19 巩固版）

### 执行三阶段

```
pytest test_x.py
│
├─ ① 收集阶段（collection）→ import 文件 ← 顶层代码在这里执行！
├─ ② 执行阶段（run）→ 逐个跑 test_ 函数 ← 用例代码在这里执行
└─ ③ 汇总报告 → 4 passed / 1 failed
```

### 判定标准

> **这段代码在"一条用例都没跑"的时候执行，会不会报错 / 结果对不对？** 会 → 不能放顶层。

| 能放顶层 | 不能放顶层 |
|---|---|
| import / 常量 / 函数定义 / fixture 定义 / 装饰器 | 打印用例统计结果 / 读取用例产生的变量 / 依赖全局计数的代码 |

## 六、今日新收获

1. **pytest.raises 语义**：预期异常断言，"崩了 = 通过"
2. **参数化适用范围**：同一断言逻辑批量数据；异常逻辑拆开单独写
3. **fixture return 任意类型**
4. **顶层代码机制**一句话：pytest 先 import 再跑用例，依赖用例结果的代码不能放顶层
5. **第 3 周毕业**：pytest 全链路（断言→参数化→fixture→接口→mock→conftest→报告→项目）✅

## 七、第 4 周预告（Day21 起：接口自动化框架深化）

- **Day21**：requests 进阶——POST 请求 / headers / session 会话 / JSON 断言
- **Day22**：面向对象初体验（类/对象，为封装做铺垫）
- **Day23**：接口框架雏形（封装 API 客户端）
- **Day24**：数据驱动（用例数据放外部文件）
- **Day25**：框架练习
- **Day26**：第 4 周复盘

---

*笔记由 AI 根据当日学习内容整理。*
