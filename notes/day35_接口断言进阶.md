# Day35 学习笔记：接口断言进阶（第 6 周 Day4）

> 日期：2026-11-07
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 6 周 · Day35
> 状态：✅ 6 passed（3 条普通 + 3 条 parametrize 展开）；自测 4/5，错题已纠正
> 里程碑：断言从"断值"升级到"断结构"——能抓"200 但结构变了"的隐性 bug

---

## 一、今日目标

把断言从"状态码/业务码/字段值"升级到"响应结构"：key 集合（不多不少）、类型、嵌套。目标是抓住**后端重构导致返回结构变化、但状态码仍 200** 的隐性 bug。

## 二、今日涉及文件

| 操作 | 文件 | 说明 |
|---|---|---|
| 【新建】 | `day35_homework.py` | 含通用 `assert_structure` + 3 条普通用例 + 1 条结构规格数据驱动 |
| 【修改】 | 无 | mock_server.py / api_client.py / conftest.py 均未改动 |

## 三、断言四层升级

| 层级 | 写法 | 能证明什么 | 局限 |
|---|---|---|---|
| ① 状态码 | `assert resp.status_code == 200` | 请求通了 | 结构变了也 200 |
| ② 业务码 | `assert data["code"] == 0` | 业务成功 | 同上 |
| ③ 字段值 | `assert data["name"] == "张三"` | 这一条数据对 | 只盯你写的字段 |
| ④ **结构**（今日新增） | key 集合 / 类型 / 嵌套 | 整张返回的骨架没变 | — |

**为什么需要第 4 层**：后端把 `age` 改名 `user_age`、把 `code` 从 int 改成 str、把 data 挪进嵌套——状态码还是 200、某些字段值还对，前三层全绿，前端却崩了。

## 四、结构断言三件套

### ① key 集合断言（不多不少）

```python
# ❌ 弱：只查存在，多出来的字段查不到
assert "code" in data.keys()

# ✅ 强：集合相等，多一个少一个都失败
assert set(data.keys()) == {"code", "name", "age"}
```

`dict.keys()` 是视图不是集合——必须 `set()` 转一下才能和集合比。

### ② 类型断言

```python
assert isinstance(data["code"], int)
assert isinstance(data["name"], str)
```

**⚠️ bool 陷阱（重点）**：Python 里 `bool` 是 `int` 的子类——

```python
isinstance(True, int)   # → True！（bool 继承自 int）
isinstance(True, bool)  # → True
type(True) is bool      # → True（更严格）
```

所以断 `/get_vip` 的 `is_vip` 如果写 `isinstance(x, int)`，`True` 也能过——必须用 `isinstance(x, bool)` 或 `type(x) is bool`。

### ③ 嵌套断言

```python
data = {"code": 0, "echo": {"user": "test", "level": 3}}
assert isinstance(data["echo"], dict)                 # 先断它是 dict
assert set(data["echo"].keys()) == {"user", "level"}  # 再断内层 key
assert isinstance(data["echo"]["level"], int)         # 内层类型
```

## 五、通用辅助函数 assert_structure（框架级复用）

```python
def assert_structure(data, schema):
    """断言 dict 的 key 集合 + 每个字段类型
    schema 例：{"code": int, "name": str, "age": int}
    """
    assert set(data.keys()) == set(schema.keys()), \
        f"字段不符: 实际={sorted(data.keys())} 期望={sorted(schema.keys())}"
    for k, t in schema.items():
        assert isinstance(data[k], t), \
            f"{k} 类型错: 实际 {type(data[k]).__name__} 期望 {t.__name__}"
```

一次断言，key 少了/多了/类型变了全暴露，报错还带实际值。

### 报错信息里的 `__name__` 是什么

`__name__` 是 Python 的"名字"属性，返回字符串——取"这个对象叫什么"。

```python
int.__name__               # "int"      ← 类对象的名字
str.__name__               # "str"
type(27).__name__          # "int"      ← 实际值的类型名
type("27").__name__        # "str"
type(27) is int            # True       ← type(27) 就是 int 类本身
```

**为什么加 `__name__`**：不加时 `type(x)` 打印是 `<class 'int'>`，带尖括号、报错信息丑；加 `.__name__` 得到干净的 `int`。

```python
age 类型错: 实际 <class 'int'> 期望 <class 'str'>    # ❌ 丑
age 类型错: 实际 int 期望 str                       # ✅ 干净
```

**顺带：模块级 `__name__`**——`if __name__ == "__main__":` 里的 `__name__` 是模块名：
- 直接运行 `python mock_server.py` → `__name__` 是 `"__main__"` → 启动服务器
- 被 `import mock_server` → `__name__` 是 `"mock_server"` → 不启动

一句话：`__name__` 是"对象的名字"——模块叫模块名、类叫类名、`type(x).__name__` 叫"x 的类型名"。

## 六、完整用例（day35_homework.py）

```python
import pytest


def assert_structure(data, schema):
    assert set(data.keys()) == set(schema.keys()), \
        f"字段不符: 实际={sorted(data.keys())} 期望={sorted(schema.keys())}"
    for k, t in schema.items():
        assert isinstance(data[k], t), \
            f"{k} 类型错: 实际 {type(data[k]).__name__} 期望 {t.__name__}"


# client 从 conftest.py 的 fixture 注入（已含 base_url，懒登录）
def test_user_structure(client):
    data = client.get_user().json()
    assert_structure(data, {"code": int, "name": str, "age": int})
    assert data["name"] == "张三"


def test_order_structure(client):
    data = client.get_order().json()
    assert_structure(data, {"code": int, "order_id": str, "amount": float})


def test_echo_nested(client):
    data = client.echo({"user": "test", "level": 3}).json()
    assert data["code"] == 0
    assert isinstance(data["echo"], dict)
    assert set(data["echo"].keys()) == {"user", "level"}
    assert isinstance(data["echo"]["level"], int)


SCHEMAS = [
    ("get_user",  {"code": int, "name": str, "age": int}),
    ("get_order", {"code": int, "order_id": str, "amount": float}),
    ("get_vip",   {"code": int, "is_vip": bool}),
]


# fixture 管环境 + parametrize 管数据——两个一起用
@pytest.mark.parametrize("method,schema", SCHEMAS)
def test_schema_ddt(client, method, schema):
    data = getattr(client, method)().json()
    assert_structure(data, schema)
```

**结果**：6 passed（3 条普通 + 3 条数据驱动展开）。

### getattr：数据驱动里的"方法名 → 方法"

上一行 `data = getattr(client, method)().json()` 里的 `getattr` 是干什么的？

**一句话**：把"字符串属性名"变成"真正的属性/方法"——点语法写死名字，getattr 可以用变量名。

```python
# 点语法：属性名必须写死
client.get_user()

# getattr：属性名可以是变量（字符串）
name = "get_user"
getattr(client, name)            # 等价于 client.get_user

# 两者完全等价：
getattr(client, "get_user")()  ==  client.get_user()
```

**拆解那一行**：

```python
fn = getattr(client, method)   # ① 按字符串名取出"方法对象"（还没调用）
fn()                           # ② 加括号才真正执行 → 返回 Response
```

parametrize 传进来的是**字符串** `"get_user"` / `"get_order"` / `"get_vip"`——数据驱动只能传数据、传不了点语法，**getattr 就是"数据 → 方法"的转换器**。

**第三个参数（默认值）**：

```python
getattr(client, "get_user")              # 存在 → 返回方法
getattr(client, "getuser")               # 不存在 → AttributeError!
getattr(client, "getuser", None)         # 不存在 → 返回 None，不报错
```

拼错方法名 = AttributeError（"一字不差"坑家族的又一成员：这次是方法名）。

**家族三兄弟**：

| 函数 | 作用 | 例子 |
|---|---|---|
| `getattr(obj, "x")` | 读属性 | `getattr(client, "token")` |
| `hasattr(obj, "x")` | 判断是否存在 | `hasattr(client, "get_vip")` → True |
| `setattr(obj, "x", v)` | 写属性 | `setattr(client, "token", "token-9")` |

**关键坑：拿到方法不加 `()` 不执行**——`getattr(client, "get_user")` 只是方法对象，`getattr(client, "get_user")()` 才执行。和 `client.get_user` 不加括号同理。

**小实验**：

```python
class Demo:
    def hello(self):
        return "hi"

d = Demo()
print(getattr(d, "hello"))        # 方法对象
print(getattr(d, "hello")())      # hi（加 () 才执行）
print(getattr(d, "nope", "默认")) # 默认值

name = "hello"
d.name()                          # ❌ AttributeError（点语法不认变量）
getattr(d, name)()                # ✅ hi（getattr 认变量）
```

**记忆**：点语法是"写死门牌号"，getattr 是"按名字查门牌"——**名字可以来自数据**，所以它能配合 parametrize。

## 七、今日三个坑

### 1. `ApiClient()` 缺 base_url（首次 6 条全红）

```
TypeError: __init__() missing 1 required positional argument: 'base_url'
```

`ApiClient(base_url)` 的 base_url 是必填。**正确姿势不是手动传 URL，而是用 conftest 的 `client` fixture**——它已从 config/env.json 读好 base_url、懒登录、401 重登。手动 `ApiClient("http://127.0.0.1:8000")` 会把地址写死进用例，换环境要改代码。

**教训：new 对象前先看 `__init__` 签名；pytest 项目里优先用 fixture。**

### 2. bool 是 int 的子类

`isinstance(True, int)` → True。断 bool 字段必须 `isinstance(x, bool)` 或 `type(x) is bool`，否则 int 断言会让 True 蒙混过关。

### 3. `data["echo", dict]` 是元组索引

方括号内逗号 = 元组当 key：`data["echo", dict]` 等价于 `data[("echo", dict)]` → KeyError。类型检查必须写 `isinstance(data["echo"], dict)`。

## 八、答疑补充：parametrize vs fixture 选型（Day34 遗留，锁入 Day35）

> 来源：Day34 课后用户提问"工作中是用 parametrize 多一点还是 fixture 传用例多一点？"

### 结论：parametrize 是日常主力，fixture 注入是"准备工"，fixture(params=) 是低频特例

| 机制 | 工作里用的频率 | 典型用途 |
|---|---|---|
| `@pytest.mark.parametrize` | 🔥🔥🔥 几乎每个接口测试文件都有 | **数据驱动**：同逻辑 × 不同数据（用户/密码/预期码） |
| fixture 注入（参数） | 🔥🔥 常驻 | **准备环境**：登录好的 client、token、临时文件、清理动作 |
| `fixture(params=...)` | 🔥 低频 | 环境矩阵/账号矩阵（同用例跑 test + pre 两套环境） |

### 为什么 parametrize 是主力

接口测试的本质就是"同一个动作 + 一堆场景数据"——登录测 10 个账号、下单测 5 种金额。parametrize 展开成 N 条独立用例、报告能定位到 `[case3]`、一条挂不影响其他。**数据驱动是接口测试的天生形态**，parametrize 就是它的载体。

### 为什么 fixture(params=) 用得少（重要）

它有个"副作用"：**params 一变化，所有引用这个 fixture 的用例全部翻倍**（笛卡尔积）。

```python
@pytest.fixture(params=["test", "pre"])   # 2 个环境
def env(request): ...

def test_a(env): ...   # 跑 2 次（test + pre）
def test_b(env): ...   # 也跑 2 次！
def test_c(env): ...   # 也跑 2 次！
```

加了 1 个环境，**所有用例都翻倍**——全局爆炸，不可控。所以它只用在"整个套件就该跑环境矩阵"的少数场景。

### 工作中真正的标准姿势：两个一起用

```python
def test_login(client, case):          # ← 同时注入两个来源！
    resp = client.login(...)           #    client 来自 fixture（准备登录环境）
    assert resp.status_code == case["expected"]   # case 来自 parametrize（测试数据）
```

```
fixture    = 准备"怎么测的环境"（登录好的 client、token、清理）
parametrize = 提供"测哪些场景"（账号、密码、预期值）
```

**分工记忆**：**fixture 管环境，parametrize 管数据**——各干各的，组合使用才是企业级接口框架的样子（api_client + conftest + parametrize 这套骨架已经在了）。

**一句话**：parametrize 是剑（主攻数据），fixture 是盾（护住环境），fixture(params=) 是重甲（环境矩阵才穿）。

## 九、自测批改记录（4/5）

| 题 | 判定 | 要点 |
|---|---|---|
| 1 只断状态码+字段值漏什么 | ❌ | **没断的字段 = 没测的字段**；后端改名/少字段/多返回敏感字段全绿但前端崩 |
| 2 key 不多不少 | ✅ | `set(data.keys()) == {...}` |
| 3 isinstance(True,int) | ✅ | True（bool 是 int 子类）；断 bool 用 `isinstance(x, bool)` |
| 4 嵌套断言 | ⚠️ | 思路对；笔误 `data["echo", dict]` 是元组索引，应为 `isinstance(data["echo"], dict)` |
| 5 assert_structure 代码 | ✅ | 完整正确 |

练习 1（集合更严）✅；练习 2（True 会过）✅；练习 3（age 27→"27" 能否抓到）待补——答案：**能，④ 类型层抓到**（`isinstance("27", int)` 为 False）。

## 十、明日预告（Day36）

第 6 周最后一天：周复盘（接口框架进阶综合复盘 + 大考）。

---

*笔记由 AI 根据当日学习内容整理。*
