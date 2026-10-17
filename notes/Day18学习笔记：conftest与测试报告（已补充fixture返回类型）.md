# Day18 学习笔记：conftest 与测试报告

> 日期：2026-10-17
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第3周 · Day18
> 状态：✅ 全部完成（conftest 全局共享、HTML 报告生成）

---

## 一、conftest.py：fixture 的"中央仓库"

**作用**：pytest 启动时**自动加载**（不需要 import），里面定义的 fixture **全局共享**——所有测试文件直接用。

**项目结构**：
```
testopen-study/
├─ conftest.py      ← fixture 中央仓库（放根目录）
├─ my_tools.py
├─ mock_server.py
├─ test_day17.py    ← 直接用 base_url
└─ test_day18.py    ← 直接用 base_url
```

**conftest.py**：
```python
import pytest

@pytest.fixture
def base_url():
    """测试环境基础地址——换环境只改这里"""
    return "http://127.0.0.1:8000"
```

**test 文件直接用**（不 import）：
```python
def test_status(base_url, path, expect):
    resp = requests.get(base_url + path, timeout=5)
    assert resp.status_code == expect
```

**为什么需要**：项目大了（几十个测试文件），fixture 写 conftest 一次，改环境地址只改一个地方。

## 附：fixture 能 return 任意类型

fixture 的 `yield` / `return` 可以交出**任何 Python 对象**，不只是字符串：

| 类型 | 例子 | 用途 |
|---|---|---|
| 基本类型 | `return "http://127.0.0.1:8000"`（str） | 配置项：base_url、token |
| 容器 | `return [{"name": "登录"}, ...]`（list）<br>`return {"age": 27}`（dict） | 测试数据批量 / 单条 |
| 模块/对象 | `return requests` | 测试客户端（Day18 练习2） |
| 函数对象 | `return check_status` | 注入工具函数 |
| 不 return | 只做准备/清理（yield 不给值） | 前后置动作 |

**已学例子盘点**：base_url→str、make_cases→list、make_user→dict、check_client→requests 模块、make_token→str。

**规则**：**return 交什么，用例参数就收到什么**——交 list 就遍历，交 dict 就用键取值，交模块就调它的方法。

## 二、pytest-html：HTML 测试报告

安装：
```powershell
& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pip install pytest-html
```

生成报告：
```powershell
& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pytest test_day18.py --html=report.html --self-contained-html
```

| 参数 | 作用 |
|---|---|
| `--html=report.html` | 生成 HTML 报告文件 |
| `--self-contained-html` | 样式打包进单文件（发别人也能打开） |

报告特点：**失败用例优先高亮展示**，点开看 Error/Failed 详情——打开先看红的，不看绿的。

## 三、今日错误复盘（重点）

### 🐛 坑1：WinError 10061 目标计算机积极拒绝

- 现象：连接 127.0.0.1:8000 被拒绝
- 原因：**mock 服务器没启动**（或端口写错）
- 修法：先 `python mock_server.py` 看到"mock 服务器启动"；确认 conftest 端口和 mock 一致

### 🐛 坑2：SSLError WRONG_VERSION_NUMBER（协议不匹配）

- 现象：连接报 SSL 握手错误
- 原因：base_url 写了 `https://127.0.0.1:8000`，但 mock 是**明文 HTTP**
- 修法：`http://127.0.0.1:8000`（去掉 s）
- **记忆**：http.server 是明文服务器 → 客户端用 http://；协议必须和服务端一致

### ⚠️ 坑3：fixture 返回"对象" vs 返回"字符串"

练习2 意图：fixture 注入**任意对象**（requests 模块=测试客户端），用例里 `check_client.get(...)` 不用 import。
理解偏差：把 fixture 写成返回 URL 字符串，用例里 `requests.get(check_client)`——能跑通但没练到点。
**fixture 能注入任何东西：数据、工具对象、配置。**

### ⚠️ 坑4：str + int 拼接 TypeError

```python
"/status/" + status   # ❌ status 是 int → TypeError: can only concatenate str (not "int") to str
"/status/" + str(status)   # ✅ 数字先 str()
```

**记忆：字符串拼接只能拼字符串。URL 拼路径参数是高频场景，`str()` 转一下。**

## 四、练习批改记录

| 项目 | 判定 |
|---|---|
| 练习1 base_url 迁 conftest | ✅ |
| 练习2 fixture 注入客户端 | ⚠️→✅（返回 requests 模块，不是 URL） |
| 练习3 故意写错断言 + 报告 | ✅（失败用例高亮观察正确） |
| 自测 5 题 | ✅（第5题 str(int) 修正） |

## 五、明日预告（Day19）

**接口测试综合练习日**：把 Day12~18 全部能力整合成一个小项目
- pytest + conftest + 参数化 + fixture + 报告
- 把 Day12 的接口检测工具完整框架化（5 个接口批量检测 + HTML 报告）
- 实战第一个"简历级"测试项目雏形

---

*笔记由 AI 根据当日学习内容整理。*
