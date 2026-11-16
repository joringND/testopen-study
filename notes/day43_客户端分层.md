# Day43 学习笔记：客户端分层（传输层与业务层分离）

> 日期：2026-11-16
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 8 周 · 第 2 天
> 主题：把 `ApiClient` 一个类拆成 `HttpSession`（传输）+ `TestApi`（业务）+ 薄壳
> 验收：全量 `48 passed, 2 skipped, 7 xfailed in 2.79s`（与拆分前一致）

---

## 一、今天解决了什么

`ApiClient` 一个类同时做三件事，问题在于**三者变化频率不同**：

| 职责 | 代码 | 以后多久变一次 |
|---|---|---|
| HTTP 传输（超时、重试、代理、换 httpx） | `session.request` / `timeout` | 很少变，一改影响全局 |
| 业务接口 | `get_user` / `get_order` / `get_vip` / `echo` | 经常加，测流媒体服务时要涨到 50 个 |
| 日志与证据 | `_log` / `last_exchange` | 格式会调，逻辑稳定 |

放在一起的后果：加一个业务接口要翻过所有传输代码，换一次 HTTP 库要碰所有业务方法——**这是 conftest 那个问题的放大版**。

拆完后的结构：

```
testopen-study/
├── clients/
│   ├── __init__.py
│   ├── http_session.py      ← HttpSession（传输层）
│   └── test_api.py          ← TestApi(HttpSession)（业务层）
├── api_client.py            ← 薄壳：ApiClient = TestApi
└── support/api_fixtures.py  ← 不动，仍 from api_client import ApiClient
```

依赖方向单向：`requests` ← `http_session` ← `test_api` ← `api_client` ← fixture ← 用例。

---

## 二、一次 `get_user()` 的调用链

```
用例  client.get_user()
  ↓
业务层  TestApi._request("GET", "/get_user")
  ↓      ├─ if not self.token: self.login()
  ↓      └─ 401 → 清 token → 重登 → 重发
传输层  HttpSession.request() → self.session.request(...) → 计时 → _log()
  ↓
证据   self.last_exchange = { method, path, url, req_body, status, resp_text, cost_ms }
```

**关键划分点**：

| 逻辑 | 放在哪层 | 为什么 |
|---|---|---|
| 拼 URL、带 token、计时、记交换 | 传输层 | 全是 HTTP 客观事实 |
| 懒登录、401 重登 | 业务层 | “登录”是业务概念，传输层不该知道 |
| `/get_user` 这种路径 | 业务层 | 路径带业务含义 |

---

## 三、四个文件的完整内容

### 3.1 `clients/__init__.py`

```python
# 客户端分层包：http_session（传输） + test_api（业务）
```

### 3.2 `clients/http_session.py`（传输层）

```python
"""传输层：只负责发请求、记录一次请求/响应交换"""
import logging
import time

import requests

logger = logging.getLogger(__name__)


class HttpSession:
    def __init__(self, base_url, timeout=5):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.token = None
        self.last_exchange = None

    def _log(self, method, path, resp, cost):
        """记录一次交换。字段照原实现抄，不要改字段名"""
        record = {
            "method": method,
            "path": path,
            "url": resp.request.url,
            "req_body": str(resp.request.body)[:500],
            "status": resp.status_code,
            "resp_text": resp.text[:1000],
            "cost_ms": cost,
        }
        self.last_exchange = record
        level = logging.WARNING if cost > 500 else logging.INFO
        logger.log(level, f"{method} {path} -> {resp.status_code} {cost}ms")

    def request(self, method, path, auth=True, **kwargs):
        """纯传输：拼 URL、按需带 token、计时、记交换"""
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        start = time.time()
        resp = self.session.request(method, url, headers=headers,
                                    timeout=self.timeout, **kwargs)
        cost = int((time.time() - start) * 1000)
        self._log(method, path, resp, cost)
        return resp
```

两个设计点：

- `timeout` 变成构造参数（默认 5），以后换环境不用改代码里的字面量
- `auth=True` 是「要不要带 token」的开关。**传输层不判断“这是登录接口”，只认参数**

### 3.3 `clients/test_api.py`（业务层）

```python
"""业务层：只负责具体接口用例需要的语义"""
from clients.http_session import HttpSession


class TestApi(HttpSession):
    def __init__(self, base_url, user="test", pwd="123"):
        super().__init__(base_url)
        self.user = user
        self.pwd = pwd

    # ---------- 会话 ----------
    def login(self, user=None, pwd=None):
        """user/pwd 不传就用构造时的默认值"""
        user = user if user is not None else self.user
        pwd = pwd if pwd is not None else self.pwd
        resp = self.request("POST", "/login", auth=False,
                            json={"user": user, "pwd": pwd})
        self.token = resp.json().get("token")
        return resp

    def _request(self, method, path, **kwargs):
        """带认证的业务请求：懒登录 + 401 重登"""
        if not self.token:
            self.login()

        resp = self.request(method, path, **kwargs)

        if resp.status_code == 401:
            self.token = None
            self.login()
            resp = self.request(method, path, **kwargs)

        return resp

    # ---------- 业务接口 ----------
    def get_user(self):
        return self._request("GET", "/get_user")

    def get_order(self):
        return self._request("GET", "/get_order")

    def get_vip(self):
        return self._request("GET", "/get_vip")

    def echo(self, payload):
        return self._request("POST", "/echo", json=payload)
```

### 3.4 `api_client.py`（薄壳）

```python
"""兼容层（过渡用）：旧名字 ApiClient 指向新的业务类 TestApi。"""
from clients.test_api import TestApi

ApiClient = TestApi


if __name__ == "__main__":
    client = ApiClient("http://127.0.0.1:8000")
    print(client.get_user().status_code)
```

---

## 四、递归陷阱为什么不会再现

Day38 踩过的坑：`_request → login → _request` 死循环，当时解法是“login 直接发请求”。

拆层之后这条线变成了：

```
test_api._request()  →  没有 token  →  self.login()
                                              ↓
                          self.request(..., auth=False)   ← 纯传输，不触发懒登录
                                              ↓
                                    HttpSession.request → session.request
```

**递归的根源是“懒登录写在 `login` 会回流的那个方法里”**。现在：

- `HttpSession.request` 完全不做登录（只按 `auth` 参数决定带不带 token）
- `TestApi._request` 才做懒登录，而 `login` 走的是纯传输 `request`

链路单向，不可能回头，所以不会再递归。**这是分层的额外收益**：把“会不会互相调用”这件事变成结构上不可能。

---

## 五、今天两次翻车：都是“凭印象写代码”

### 5.1 翻车 A：`login` 签名写错

**现象**：

```
FAILED day25_homework.py::test_login_ok - TypeError: login() takes 1 positional argument but 3 were given
ERROR day27_homework.py::test_after_login - TypeError: login() takes 1 positional argument but 3 were given
4 failed, 40 passed, 2 skipped, 7 xfailed, 4 errors
```

**根因**：用例和 fixture 里是 `client.login("test", "123")`，我给的 `TestApi.login(self)` 接不住。`3 were given` = `self + "test" + "123"`。

**修正**：

```python
def login(self, user=None, pwd=None):
    user = user if user is not None else self.user
    pwd = pwd if pwd is not None else self.pwd
```

注意用 `is not None` 而不是 `or`：`or` 会把 `""`、`0`、`False` 都当成“没传”，`is not None` 只排除 `None`。

**连带发现**：`ERROR` 出现在 `day27`，说明是 **fixture 的 setup 阶段**调了 `login`——表明确实存在“fixture 里也调登录”的写法，这类用例最容易在签名变更时被漏掉。

### 5.2 翻车 B：漏了 `echo` 方法

**现象**：修完 `login` 后还有用例在挂。导出旧签名才发现旧类有 8 个方法，新类只写了 7 个。

**旧签名清单（`git show HEAD:api_client.py | findstr /n "def "`）**：

```
7:    def __init__(self,base_url,user="test",pwd="123"):
16:    def login(self,user=None,pwd=None):
30:    def _log(self,method,path,resp,cost):
48:    def _request(self,method,path,**kwargs):
68:    def get_user(self):
70:    def get_order(self):
72:    def get_vip(self):
74:    def echo(self, payload):
```

**新旧对照表**：

| 旧签名 | 新类 | 状态 |
|---|---|---|
| `__init__(self, base_url, user="test", pwd="123")` | 同 | ✅ |
| `login(self, user=None, pwd=None)` | 补参后一致 | ✅（先错） |
| `_log(self, method, path, resp, cost)` | 曾写成 `cost_ms` | 改回 `cost` |
| `_request(self, method, path, **kwargs)` | 同 | ✅ |
| `get_user(self)` / `get_order(self)` / `get_vip(self)` | 同 | ✅ |
| `echo(self, payload)` | **漏了** | ❌ → 补上 |

`echo` 的实现（从旧代码抄）：

```python
def echo(self, payload):
    return self._request("POST", "/echo", json=payload)
```

### 5.3 共性根因与落成规则

两次错误（昨天的虚构 `env_config`、今天的 `login` 签名 + 漏 `echo`）同一个根因：**没先看旧代码就动手**。

正确顺序是固定的两条命令，**顺序不能反**：

```powershell
# ① 先导出“该有什么”——完整公开签名清单
git show HEAD:<文件名> | findstr /n "def "

# ② 再对比“改了什么”——只反映删除/新增的行
git diff <文件名>
```

- `git show` 回答 **“要搬的全部东西”**，是搬运清单
- `git diff` 回答 **“我动了哪些”**，是变更记录

**只有变更记录、没有搬运清单，就等于在赌自己记得对。** 这也是今天 `echo` 被漏掉的直接原因——我以为类里只有 7 个方法。

顺带一条：`Select-Object` 是 PowerShell 命令，cmd 里跑会报 `不是内部或外部命令`。cmd 下要看指定行，用导出文件的方式：

```powershell
git show HEAD:api_client.py > old_api.txt
notepad old_api.txt
```

---

## 六、零改动兼容：三个一致性

用例之所以能一行不动，靠三个“接口一致”：

| 保证 | 具体内容 | 少了的后果 |
|---|---|---|
| **类名** | `ApiClient` 用别名 `ApiClient = TestApi` 保住 | `ImportError` |
| **构造签名** | `(base_url, user="test", pwd="123")` 一致 | `TypeError: __init__() missing ...` |
| **方法名 + 参数签名** | 8 个方法名与参数全部一致 | `TypeError: login() takes 1 positional...` |

**“方法名对”不等于“调用能通”**——参数表是接口的一部分，而且最容易被“看起来一样”骗过去。

### 这个手法：Strangler Fig Pattern（绞杀者模式）

Martin Fowler 命名：新结构像榕树一样慢慢包住旧结构，最终旧结构自然枯萎。

```
第 1 步：新类建好，旧入口用别名指向它      ← 今天做完了
第 2 步：逐步把用例 import 改成新名字      ← 不急，可以一直挂着
第 3 步：没人再用旧名字时，删掉 api_client.py
```

**为什么不能一步到位**：11 个用例文件里有直接 `ApiClient(base_url)` 构造的（Day35 那次 `6 failed` 就是这类用法）。一步删旧类，这些地方集体 `ImportError`，一次面对十几个报错，分不清主次。

**为什么用两行薄壳而不是“新类继承旧类”**：薄壳出问题时排查面只有两行，问题一定在 `TestApi`；继承旧类则新旧逻辑还在一个文件里混着。

### 不要用注释当备份

你这次是把旧类整段注释掉：

```python
+#     def __init__(self,base_url,user="test",pwd="123"):
```

问题：

| 问题 | 说明 |
|---|---|
| Git 里已有完整历史 | `git show HEAD:api_client.py` 随时取回 |
| 干扰搜索 | `findstr "def "` 搜出来一半是注释 |
| 误导后来者 | 看着像还在生效 |

**想留退路就 `git commit`。** 用版本控制做备份，不用注释做备份。

---

## 七、坑预警（今天真正会撞的）

| 坑 | 现象 | 原因 |
|---|---|---|
| `login()` 走 `_request()` | `RecursionError` / 无限重登 | `_request` 懒登录 → login → `_request` 死循环 |
| 401 重登写进 `HttpSession` | 传输层 import 业务类，出现循环依赖 | 传输层不该知道“登录”是什么业务动作 |
| 忘了 `super().__init__()` | `AttributeError: 'TestApi' object has no attribute 'session'` | 父类没初始化 |
| `TestApi` 里重新建 `requests.Session()` | 两套连接池，Cookie 不共享 | 会话对象必须只有一份 |
| 文件保存成 GBK | `UnicodeDecodeError` / 中文注释乱码 | VSCode 右下角确认 UTF-8 |

补充一条语义坑：`user = user or self.user` 看似简洁，实际会把 `""`、`0` 当成“没传”。**判断“有没有传参”永远用 `is not None`**。

---

## 八、验收证据

```
# ① 三个出过问题的文件
16 passed, 2 skipped, 5 xfailed in 0.30s

# ② 全量
48 passed, 2 skipped, 7 xfailed in 2.79s
```

成绩与拆分前完全一致 → 分层没有改变任何行为。**成绩不变就是重构的唯一验收标准。**

`artifacts 目录共 23 个证据文件`：落盘钩子仍然正常（失败时自动新增），说明拆到 `clients` 后 `item.funcargs["client"].last_exchange` 这条链路没断。

---

## 九、自测 5 题与参考答案

**Q1. `_log()` 为什么放传输层而不是业务层？举一个字段说明它“不知道业务含义”。**

`path` 字段只是 `/get_user` 这个字符串，它分不出这是“查用户”还是“下单”。`status` / `cost` / `req_body` 同理——全是 HTTP 层面的客观事实，没有一个是业务语义。**字段里只要出现业务判断，就说明放错了层。**

**Q2. `login()` 为什么必须走 `self.request(..., auth=False)`，不能走 `self._request(...)`？**

循环链是：

```
_request → (if not token) → login → _request → (if not token) → login → ...
```

`_request` 的职责是“没 token 就登录”，如果 `login` 又回 `_request`，就形成自我调用闭环。走 `request`（纯传输层，不做懒登录）链路单向，不可能回头。

**Q3. 401 重登为什么放 `TestApi._request` 而不放 `HttpSession.request`？**

两个理由：

1. **概念归属**：“登录”是业务动作，传输层只知道“有一个 token 字符串”
2. **依赖方向**：传输层要重登就得知道登录接口路径和账号密码，等于业务逻辑下沉，`http_session` 要反向依赖业务 → 循环依赖

如果硬放传输层，只能写成“传入一个 `on_401` 回调”，那也是把业务概念塞进了管道。

**Q4. 保证“用例零改动”的三个一致性是什么？少一条会怎样？**

类名（别名保住）、构造签名、方法名 + 参数签名。

少**方法签名**那条，就是今天实录的 `TypeError: login() takes 1 positional argument but 3 were given`——方法名明明对，参数不对照样全挂。

**Q5. 三年后 `requests` 淘汰要换 `httpx`，改哪里？**

只改 `clients/http_session.py`：

1. `import requests` → `import httpx`
2. `self.session = requests.Session()` → `httpx.Client(...)`
3. `session.request(...)` 的调用方式按 httpx 适配（`timeout`、`headers` 参数基本同构）

**`test_api.py` 一行不动，11 个用例文件一行不动。** 这就是“传输层独立”的实际收益——换一次底层库，只碰一个文件。

---

## 十、本日结论

| 项 | 结论 |
|---|---|
| 技术目标 | ✅ 达成：一个类变两层 + 薄壳，用例零改动 |
| 功能回归 | ✅ 全量 48 passed / 2 skipped / 7 xfailed，与拆分前一致 |
| 最大收获 | 分层的收益不只是“整齐”，还有**结构上排除递归**（`request` 不做登录） |
| 最大教训 | 重构第一步必须是 `git show HEAD:xxx | findstr "def "`——先拿到搬运清单，再动手 |
| 遗留待办 | `api_client.py` 薄壳是过渡物，将来所有 import 切到 `clients.test_api` 后删掉 |

---

## 十一、课后答疑（5 问）

> 本章为 Day43 课后连续提问，按原顺序整理。

### 11.1 `super().__init__(base_url)` 怎么理解

一句话：**把“基础设施那部分初始化”交回父类，让同一个 `self` 上同时具备两批属性。**

```python
class TestApi(HttpSession):
    def __init__(self, base_url, user="test", pwd="123"):
        super().__init__(base_url)     # ← 这句
        self.user = user
        self.pwd = pwd
```

**逐层拆**：

| 片段 | 含义 |
|---|---|
| `super()` | 返回**父类 `HttpSession` 的代理对象**（沿继承链找下一个类），不是父类本身 |
| `.__init__` | 拿到父类的初始化方法 |
| `(base_url)` | 传给父类的参数，**`self` 是隐式传的** |

等价写法：`HttpSession.__init__(self, base_url)`。

**对象只有一个**：

| 由谁写入 | 属性 |
|---|---|
| 父类 `HttpSession.__init__`（第 ① 批） | `base_url` / `timeout` / `session` / `token` / `last_exchange` |
| 子类 `TestApi.__init__`（第 ② 批） | `user` / `pwd` |

两批属性挂在**同一个 `self`**（同一个 `__dict__`）上，所以子类方法里才能直接用 `self.session`、`self.token`。不是什么“父类对象 + 子类对象”，只有一个对象。

**不写会怎样**：

```
client.get_user() → _request 里 if not self.token
→ AttributeError: 'TestApi' object has no attribute 'token'
```

因为 `token` 是父类写进去的，父类没初始化 → 该属性从未被创建。

**MRO（方法解析顺序）**：

```
TestApi        ← 当前类
   ↓ super() 往下找
HttpSession    ← 找到 __init__
   ↓
object
```

以后中间插一个 `RetryHttpSession`，`super()` 会自动穿过它，不用改子类。

**参数对位**：

```python
super().__init__(base_url)              # ✅ timeout 用默认 5
super().__init__(base_url, timeout=10)  # ✅ 显式给超时
super().__init__(self, base_url)        # ❌ self 自动传，多传会 TypeError
```

最后那种写法报 `takes 3 positional arguments but 4 were given`，和今天 `login()` 那个错是同一类。

**`super()` 与显式父类名的对比**：

| | `super().__init__(...)` | `HttpSession.__init__(self, ...)` |
|---|---|---|
| 继承链变化 | 自动找下一个，不用改 | 父类名换了要改代码 |
| 多重继承 | 按 MRO 正确执行 | 容易重复或漏调 |
| 可读性 | 明确表达“交给上一层” | 硬编码，看不出意图 |

**8 行验证代码**：

```python
class A:
    def __init__(self, x):
        print("A 收到:", x)
        self.x = x

class B(A):
    def __init__(self, x, y):
        super().__init__(x)
        self.y = y

b = B(1, 2)
print(b.__dict__)     # {'x': 1, 'y': 2}
print(type(b))        # <class '__main__.B'>
```

三行输出证明三件事：父类真的执行了、属性在同一个 `__dict__`、只有一个对象。

**一句话总结**：`super().__init__(base_url)` = “我是 `TestApi`，但我只负责业务那部分初始化；session、token 那些基础设施请父类来建，建在同一个 `self` 上。”

### 11.2 “签名”是什么

**函数签名（signature）= 函数的对外承诺：叫什么名字、几个参数、什么顺序、有没有默认值。**

以今天的真实签名为例：

```python
def login(self, user=None, pwd=None):
```

| 部分 | 内容 | 属于签名 |
|---|---|---|
| 函数名 | `login` | ✅ |
| 参数个数 | 3（含 `self`） | ✅ |
| 参数顺序 | `self → user → pwd` | ✅ |
| 默认值 | `user=None`、`pwd=None` | ✅ |
| 函数体 | 里面的 5 行代码 | ❌ |
| 注释 / docstring | `"""..."""` | ❌ |
| 返回值 | `return resp` | ⚠️ 约定算，Python 不强制 |

**签名是合同，函数体是履约方式。**

重构规矩：**函数体随便改，签名不能动**——因为调用方只认签名。调用方看不见里面怎么发请求，只知道“能这么写”。

**改动各部分的后果**：

| 改动 | 后果 |
|---|---|
| 改方法名 | `AttributeError: no attribute 'login'` |
| 少参 / 多参 | `TypeError: takes 1 but 3 were given` |
| 改参数顺序 | 不报错，值传错位（**最危险**） |
| 改参数名（关键字调用时） | `TypeError: unexpected keyword argument` |
| 整个方法漏掉 | `AttributeError`（今天的 `echo` 就是这种） |

**参数名什么时候真的重要**：

| 调用方式 | 长这样 | 参数名参与兼容吗 |
|---|---|---|
| 位置调用 | `client.login("test", "123")` | ❌ 只看顺序和个数 |
| 关键字调用 | `client.login(user="test")` | ✅ 名字必须对 |

所以把 `_log` 的 `cost_ms` 改回 `cost`，**严格说不改也能跑**（因为是按位置调用的）。改的唯一理由是**减少 `git diff` 噪音**：搬运阶段除了位置什么都不该变，名字一变，以后看 diff 会以为逻辑动过，多一次不必要的核对。

而 `login` 那次是真炸，因为用例是位置调用、**个数对不上**：

```
client.login("test", "123")   ← 2 个位置参数
def login(self):              ← 只能接 0 个
→ TypeError: takes 1 positional argument but 3 were given
```

（`3` = `self` + `"test"` + `"123"`；`1` = 只有 `self`。）

**重构的对外接口三项**：

```
① 类名             → ApiClient（用别名保住）
② 构造签名         → (base_url, user="test", pwd="123")
③ 方法名 + 方法签名 → 8 个方法全部对齐
```

今天前两项守住了，第三项没守住（`login` 少参、`echo` 漏掉）。**准确归类：不是“写错代码”，是“改动了签名”。**

拿签名清单的固定命令：

```powershell
git show HEAD:api_client.py | findstr /n "def "
```

**一句话记**：签名是给外人看的门面，函数体是屋里怎么装修。装修可以随便翻新，门面动一寸，外面排队的人全撞墙。

### 11.3 `request` 从哪来

**`request` 不是 import 的，也不是自己定义的**，它是 pytest 的**内置特殊对象**：fixture 参数名写 `request`，pytest 就注入一个 `FixtureRequest` 实例。

```python
@pytest.fixture(scope="session")
def env_name(request):        # ← 参数名写 request，pytest 自动注入
    return request.config.getoption("--env")
```

**先澄清名字撞车**：

| 名字 | 是什么 | 干什么 |
|---|---|---|
| `request`（fixture 参数） | pytest 的 `FixtureRequest` 对象 | 访问“当前测试上下文”：配置、节点、参数化数据 |
| `requests`（第三方库） | HTTP 客户端库 | 发 HTTP 请求（`http_session.py` 里用的那个） |

两者除了名字相似，毫无关系。`request` 不发网络请求，它代表的是“**这次 pytest 运行的上下文**”。

**`request.config.getoption("--env")` 的三层**：

| 层 | 是什么 | 职责 |
|---|---|---|
| `request` | 当前测试的上下文对象 | 知道“我现在为哪条用例服务” |
| `request.config` | `Config` 对象 = 整场运行的配置中心 | 所有命令行参数、ini 配置都在这里 |
| `.getoption("--env")` | 按选项名从配置中心取值 | 拿不到就抛异常（除非给 default） |

**一个 `--env` 的完整链路**：

```
① 注册选项（必须在解析之前）
   pytest_addoption(parser): parser.addoption("--env", default="test")
   → 告诉 pytest：“有个 --env 参数，默认 test”

② 命令行给值
   pytest day37_homework.py --env pre
   → 不给就用默认 test

③ pytest 解析后存进 Config
   config.option.env = "pre"        ← 全 session 唯一一份

④ fixture 里读出来
   request.config.getoption("--env") → "pre"
```

**四个易错点**：

1. **名字必须叫 `request`**，写成 `req` → `fixture 'req' not found`。pytest 靠参数名识别要注入什么
2. **`getoption("--env")` 和 `getoption("env")` 都行**（后者是 dest 名，去掉横线），但带横线更直观，和 `parser.addoption("--env", ...)` 对得上
3. **用 `scope="session"`** 是因为 `--env` 一次运行只有一个值，读一次就够，所有用例共享同一个 `base_url`，不会每条用例重读一遍 json
4. **不要用 `request` 传业务数据**。它是“上下文访问器”，不是数据容器；要共享数据用 fixture 返回值（`base_url` 就是这么做的）

**`request` 的其他能力（以后会用到）**：

| 用法 | 作用 | 场景 |
|---|---|---|
| `request.config.getoption("--env")` | 读命令行参数 | 现在用的这个 |
| `request.param` | 读 `@pytest.mark.parametrize` 传进来的那一组值 | 做数据驱动 fixture |
| `request.node` | 当前用例节点，可取 `name` / `nodeid` | 给日志加“当前用例名”前缀 |
| `request.getfixturevalue("client")` | fixture 内部临时取另一个 fixture | 有依赖但不想写进参数列表 |
| `request.addfinalizer(fn)` | 注册 teardown 回调 | 手工清理（替代 `yield`） |

对应关系：**hook 拿 `item`，fixture 拿 `request`**，都是“当前上下文句柄”。

**`getoption` 与 `getini` 的区别（Day44 会用到）**：

```python
request.config.getoption("--env")      # 读命令行选项
request.config.getini("testpaths")     # 读 pytest.ini 里的配置项
```

同一个 `config`，两种取法：`getoption` 管命令行，`getini` 管 pytest.ini。

**类型验证**：

```python
print(type(request))   # <class '_pytest.fixtures.FixtureRequest'>
```

看到这个类名，`request` 的来历就彻底清楚：**它是 pytest 提供的对象，不是你写的变量**。

**一句话记**：`request` 是 pytest 递给 fixture 的“当前运行上下文遥控器”，`.config` 是配置中心，`.getoption("--env")` 是按参数名取命令行里给的值。

### 11.4 hook 是什么

**hook（钩子）= pytest 在生命周期某个固定时刻“广播”的事件点；写一个同名函数，就能在那个时刻插进去执行。**

可以想成：pytest 每到一个关键节点就喊一声“我现在到 XX 阶段了，谁要处理？”——函数名对上了就会被叫到。

**命名规律**：`pytest_<阶段>_<动作>`

| hook 名 | 什么时候被调用 |
|---|---|
| `pytest_addoption` | pytest 启动**最早期**，注册命令行参数 |
| `pytest_runtest_makereport` | **每条用例的每个阶段结束后**，生成 report 时 |
| `pytest_terminal_summary` | 全部跑完，终端汇总之前 |
| `pytest_sessionstart` / `pytest_sessionfinish` | session 开始 / 结束 |
| `pytest_collection_modifyitems` | 用例收集完成，可调整顺序 |

**两条硬规则**：

1. **函数名必须一字不差**

```python
def pytest_terminal_summary(...)     # ✅ 会被调用
def terminal_summary(...)            # ❌ 名字不匹配，静默忽略，不报错
```

Day40 讲过的点：hook 写错名字**不报错，只是永远不执行**，最难排查。

2. **参数名必须和 pytest 定义的一致**

```python
def pytest_runtest_makereport(item, call)          # ✅ 规范签名
def pytest_runtest_makereport(test_item, call)     # ❌ 参数名不对，注册失败
```

pytest 用 pluggy 实现这套机制：每个 hook 有一个**规格（spec）**规定参数名；你写的函数叫**实现（impl）**，参数必须和 spec 对上。

**hook 与 fixture 的根本区别**：

| | hook | fixture |
|---|---|---|
| 触发时机 | 框架事件（固定阶段） | 用例**声明要**才执行 |
| 作用范围 | 全局，影响所有用例 | 只给声明的用例 |
| 谁调用 | pytest 主动调用 | pytest 按依赖解析 |
| 常见用途 | 参数注册、报告、收集、生命周期 | 提供数据 / 对象 |
| 出错影响 | 可能整个 session 崩 | 只影响相关用例 |

一句话：**fixture 是“按需供应”，hook 是“全局监听”**。这解释了为什么 Day42 那个 `NameError` 能摧毁整场 session——hook 不是单条用例的私有逻辑。

**项目里正在用的 3 个 hook**：

| hook | 文件 | 干什么 |
|---|---|---|
| `pytest_addoption` | `support/env_config.py` | 注册 `--env` |
| `pytest_runtest_makereport` | `support/reporting.py` | 失败落盘 + extras 内嵌 |
| `pytest_terminal_summary` | `support/reporting.py` | 末尾打印证据文件数 |

三个都在插件里，通过 `pytest_plugins` 注册——这就是 Day42 拆分的意义：**hook 必须住在被 pytest 认识的模块里**。

**`hookwrapper` 为什么特殊**：

```python
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield                 # ← 先把控制权交出去，让原有逻辑跑完
    report = outcome.get_result()   # ← 再拿回结果
```

普通 hook 是“插入执行”，`hookwrapper` 是“**包住**执行”：可以在原逻辑前面做事、后面读结果。`report` 在 `yield` 之后才被造出来，所以**必须 yield 之后才能读**。

### 11.5 同时跑多个文件，几个 session？session 级 fixture 几次？

**session 的边界是「pytest 进程启动 → 退出」，不是文件数。**

一条命令给 11 个文件，仍然是 **1 个 session**，session 级 fixture 全程**只创建 1 次**。

**session 内的时间轴**：

```
session 开始   pytest_sessionstart（pytest_addoption 更早）
   ↓
收集           11 个文件全被 import，用例收集完
   ↓
首次用到 base_url → session fixture 创建（此后全程复用同一实例）
              48 条用例共用同一个 base_url / session / token
              function 级 fixture（client）每条用例新建一个
   ↓
每条用例：setup → call → teardown
              每个阶段结束都调一次 pytest_runtest_makereport
              （这就是 Day39 学的 report.when 三值的由来）
   ↓
收尾           pytest_terminal_summary（只 1 次）→ pytest_sessionfinish
```

**四种跑法对比**：

| 跑法 | session 数 | session fixture 次数 |
|---|---|---|
| `pytest a.py b.py c.py` | 1 | 1 |
| `pytest a.py` 然后 `pytest b.py` | 2 | 2 |
| 循环里 `pytest.main([f])` | 每调一次算 1 | 同左 |
| `pytest -n 3`（xdist） | 1 主控 + 3 worker | 每个 worker 各 1 次 |

**你的 `run_tests.bat` 属于第一种**：

```bat
set FILES=day25_homework.py ... day39_homework.py
%PYTHON% -m pytest %FILES% ...
```

一条命令、多个文件名参数 → **1 个 session → `env_name` / `base_url` 只执行 1 次**；`client` 是 function 级，48 条用例各一个。

**验证方法**（临时加 print，跑完删掉）：

```python
@pytest.fixture(scope="session")
def base_url(env_name):
    print(f"\n[base_url] 被创建，env={env_name}")     # 临时加
    ...
```

```powershell
& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pytest day25_homework.py day27_homework.py day28_homework.py -v -s
```

`-s` 关掉输出捕获，否则 print 看不见。**只打印一次**才对；打印三次说明实际跑了三次 pytest。

反过来验证 function 级：在 `client` fixture 里 print，同一条命令下会打印**每条用例一次**。两个 fixture 的差别一眼可见：**session 一个、function 一堆**。

**三个连带结论**：

1. **`--env` 是 session 级，做不到“半场换环境”**——想一条命令里一半跑 test、一半跑 pre 不行，必须跑两次命令（2 个 session）。这正是 bat 里 `if not "%ENV%"=="test"` 分流存在的根本原因。
2. **`pytest_terminal_summary` 每 session 打印一次**——如果哪天看到 `artifacts 目录共 N 个证据文件` 出现两次，说明脚本调了两次 pytest。它本身就是“session 数量”的探针。
3. **上 xdist 并行后，session fixture 变成每 worker 一次**——`pytest -n 3` 会创建 3 次 `base_url`，`last_exchange` 也不再全局唯一。做并发测试要提前想到这一点。

**一句话记**：hook 是“生命周期广播站”，fixture 是“按需供应商”；session 是“一次进程启动到退出”，多文件仍在同一个 session 里，session 级 fixture 全程只算一次。

---

## 十二、下一步（Day44 预告）

**主题：目录迁移——把 11 个用例文件搬进 `tests/`**

Day42 之所以没动目录，是因为一次改六个变量风险太高。现在两个前提已经就位：

| 前提 | 状态 |
|---|---|
| 路径都已绝对化（`paths.py` 的 `BASE_DIR` 不依赖工作目录） | ✅ Day42 完成 |
| 客户端与 fixture 已经不依赖“文件放在根目录” | ✅ Day43 完成 |

Day44 要解决的三件事：

1. `import api_client` 在 `tests/` 下还能用 → `pytest.ini` 加 `pythonpath = .`
2. `testpaths` 从单个文件改成 `tests`
3. bat 里的 11 个文件路径全加 `tests/` 前缀

**预习问题**：

1. 搬进 `tests/` 后，`support/` 该留在根目录还是也搬进去？`paths.py` 的 `BASE_DIR` 会不会因此算错？
2. `pytest.ini` 的 `pythonpath = .` 里的 `.` 指的是哪个目录？是执行命令的当前目录，还是 `rootdir`？
