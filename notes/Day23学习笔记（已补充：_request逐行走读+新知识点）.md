# Day23 学习笔记：接口框架雏形

> 日期：2026-10-20
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 4 周 · Day23
> 状态：✅ pytest 4 passed + 401 自动重试验证通过
> 里程碑：**第 4 周第 1 个"框架级"产物**——自动认证 + 401 重试 + fixture + 数据驱动

---

## 一、今日目标

把 ApiClient 从"类的雏形"升级成"框架级客户端"：**自动登录、自动带 token、401 自动重试**；conftest 提供 client；用例数据挪到外部文件。

**框架 vs 脚本的分界线**：脚本把每一步写进用例；框架把通用逻辑收进类，用例只关心业务。

## 二、框架核心：ApiClient 完整版（api_client.py）

```python
import requests

class ApiClient:
    def __init__(self, base_url, user="test", pwd="123"):
        self.base_url = base_url
        self.session = requests.Session()
        self.user = user
        self.pwd = pwd
        self.token = None          # 缓存的 token（初始没有）

    # 登录（user/pwd 可选：不传用对象默认的）
    def login(self, user=None, pwd=None):
        user = user if user else self.user
        pwd = pwd if pwd else self.pwd
        resp = self.session.post(
            f"{self.base_url}/login",
            json={"user": user, "pwd": pwd},
            timeout=5,
        )
        if resp.status_code == 200:
            self.token = resp.json()["token"]     # 存 token
        return resp

    # 核心方法：所有请求走这里（自动带 token + 401 重试）
    def _request(self, method, path, **kwargs):
        if self.token is None:                    # ① 没 token → 先登录（懒登录）
            self.login()
        headers = kwargs.pop("headers", {})       # ② 取调用方可能传的 headers
        headers["Authorization"] = f"Bearer {self.token}"   # 自动带 token

        resp = self.session.request(method, f"{self.base_url}{path}",
                                    headers=headers, **kwargs)

        if resp.status_code == 401:               # ③ token 过期？
            self.login()                          #    重新登录（换新 token）
            headers["Authorization"] = f"Bearer {self.token}"
            resp = self.session.request(method, f"{self.base_url}{path}",
                                        headers=headers, **kwargs)   # 重试一次
        return resp                               # ④ 返回最终结果

    # 业务方法：只描述"要调哪个接口"
    def get_user(self):
        return self._request("GET", "/get_user")
```

### _request 逐行走读（当日答疑完整版，★=新知识点）

**整体旅程**（以第一次调用 `client.get_user()` 为例）：

```
① 懒登录 → ② 装 headers → ③ 发请求 → ④ 401？→ ⑤ 返回 resp
```

**逐行拆解**：

| 代码 | 含义 | 知识点 |
|---|---|---|
| `def _request(self, method, path, **kwargs):` | 内部方法，接收请求方式/路径/任意参数 | ★ **方法名下划线前缀** = "内部方法"约定（类自己用，外部别直接调）<br>★ `**kwargs` 实战：把调用时多余的关键字参数（如 `timeout=5`）打包成字典 |
| `if self.token is None:` | 第一次调用时 token 还是 None（__init__ 初值）→ 说明没登录 | ★ **懒登录**：第一次要请求时才登录；第二次 token 有值就跳过<br>★ `is None` 而非 `== None`：None 是唯一单例，用 is 判断身份是规范写法 |
| `self.login()` | 登录并让 `self.token` 拿到新 token | — |
| `headers = kwargs.pop("headers", {})` | 取出调用方可能传的 headers；没传给空字典 | ★ **`dict.pop(key, default)`**：取出并**删除**该键（Day8 学的 get 只取不删）<br>★ 为什么用 pop 不用 get：不删的话 headers 会留在 kwargs，等下 `**kwargs` 展开时重复传 `headers=` 报错 |
| `headers["Authorization"] = f"Bearer {self.token}"` | 往 headers 加认证头，拼出 `"Bearer token-1"` | 这就是你手动写过的 Authorization，现在框架自动做 |
| `resp = self.session.request(method, f"{self.base_url}{path}", headers=headers, **kwargs)` | 统一入口发请求 | ★ `session.request(method, url, ...)` = `get()`/`post()` 的底层统一入口<br>★ `f"{self.base_url}{path}"` URL 拼接<br>★ `**kwargs` 展开传剩余参数（timeout 等） |
| `if resp.status_code == 401:` | 服务器说"凭证无效/过期" | ★ **401 = 未认证/凭证失效**（HTTP 语义） |
| `self.login()` | 重新登录 → `self.token` 更新成新 token | mock v3 每次登录发新 token，所以 token 一定换了 |
| `headers["Authorization"] = f"Bearer {self.token}"` | 用新 token 重写 headers | — |
| `resp = self.session.request(...)`（重发） | 重试一次，结果覆盖 resp | 重试还 401 = 真问题，交给断言 |
| `return resp` | 返回最终结果（重试后 200 或仍失败） | 业务方法拿到它 `.json()` 取数据 |

**一句话串**：第一次请求 → 没 token 先登录 → 带上 token 发出去 → 若 401 说明 token 过时 → 重新登录换新 token → 重发一次 → 把最终结果交给你。

**★ 本节新知识点汇总**（之前没系统讲过）：
1. 方法名下划线前缀 = 内部方法约定
2. `**kwargs` 打包/展开任意关键字参数（实战用法）
3. `dict.pop(key, default)` = 取出并删除
4. `is None` vs `== None`（None 单例身份判断）
5. `session.request(method, url, **kwargs)` = get/post 统一入口
6. 懒登录模式（Lazy Login）
7. 401 的 HTTP 语义（未认证/凭证失效）
8. URL 拼接 `f"{base_url}{path}"` + 重试覆盖 resp 模式

## 三、mock v3：token 会"过期"

**机制**（复习清单已记录，学到 mock 时回看）：
- `COUNTER[0] += 1` → `LATEST_TOKEN = f"token-{COUNTER[0]}"`：**每次登录发新 token**
- `/get_user` 只认 `Authorization: Bearer {LATEST_TOKEN}`（最新 token）→ 旧 token 一律 401
- 这样才"逼"出 401 自动重试的完整闭环

**验证**：登录两次打印 token（token-1、token-2 不同）；手动带旧 token → 401；`client.get_user()` → 自动重试 → 200。

## 四、client fixture（conftest.py）

```python
import pytest
from api_client import ApiClient

@pytest.fixture
def base_url():
    return "http://127.0.0.1:8000"

@pytest.fixture
def client(base_url):
    return ApiClient(base_url)
```

用例直接要参数：`def test_get_user_with_client(client): ...`——**参数名必须和 fixture 函数名一致**（pytest 按名字注入）。

## 五、数据驱动（data/users.json）

```json
[
  {"user": "test", "pwd": "123", "expect_code": 0},
  {"user": "test", "pwd": "wrong", "expect_code": 401},
  {"user": "admin", "pwd": "123", "expect_code": 401}
]
```

```python
import json
with open("data/users.json", "r", encoding="utf-8") as f:
    USERS = json.load(f)

@pytest.mark.parametrize("case", USERS)
def test_login_cases(client, case):
    assert client.login(case["user"], case["pwd"]).json()["code"] == case["expect_code"]
```

**数据驱动意义**：加测试账号只改 users.json，不动代码。

## 六、今日坑与教学衔接说明

### 🐛 坑1：login 签名不匹配（TypeError）

```
TypeError: login() takes 1 positional argument but 3 were given
```

- 原因：核心代码 `login(self)` 无参，数据驱动用例 `client.login(case["user"], case["pwd"])` 传参 → 不匹配
- **教学衔接疏忽**（已向用户坦诚）：给的 ApiClient 和练习要求没对齐
- 修法：**默认参数** `def login(self, user=None, pwd=None)`——无参用默认（_request 重试）、传参用传入（数据驱动）

### 💡 顺带学到的设计决策："谁负责账号？"

| 设计 | 适用 |
|---|---|
| `login(user, pwd)` 可传参 | 测登录接口本身对不同账号的响应 |
| `ApiClient(base_url, user=..., pwd=...)` 按账号建对象 | 测某类用户身份的后续操作 |

两种都对，真实框架都有。

### 📌 复习清单新增

Day23 `_request` + mock v3 token 机制 → 已记入 `notes/复习清单.md`（学到 mock 深入时回看 + 练习5 验证）。

## 七、练习批改记录

| 练习 | 结果 |
|---|---|
| 1 mock v3 + 两次登录 token 不同 | ✅ token-1 / token-2 |
| 2 api_client.py 完整版 + get_user | ✅ |
| 3 conftest client fixture + 用例改参数 | ✅ test_get_user_with_client PASSED |
| 4 数据驱动 3 组 | ✅ case0/1/2 全过 |
| 5 401 自动重试验证 | ✅ 旧 token 401 → 自动重试 → 200 张三 |

## 八、自测批改记录

| 题 | 判定 | 要点 |
|---|---|---|
| self.token 缓存什么/为什么 | ✅ | 凭证字符串；一次登录多次用，避免每请求现登录 |
| 401 重试逻辑 | ✅ | 401 → 重新 login → 新 token 重写 header → 重发 |
| client fixture 好处 | ✅ | 自动注入、不重复造、改环境只改 conftest |
| 数据驱动代码 | ✅ | json 读取 + 参数化 |
| 框架还能自动什么 | ✅ | 报告/日志/重跑/环境切换/数据准备/通知 |

## 九、今日新收获

1. **框架核心 _request**：懒登录 + 自动带 token + 401 自动重试（Day21 思考题正式实现）
2. **mock v3 token 机制**：每次登录换 token、最新 token 才有效
3. **client fixture**：pytest 注入客户端，用例只关心业务
4. **数据驱动**：加用例不改代码（users.json）
5. **默认参数让方法更灵活**（login 可选参数）
6. **设计决策**："谁负责账号"两种方案

## 十、明日预告（Day24）

**数据驱动深化**：把数据驱动做成"框架标配"——
- 测试数据统一管理（json/yaml）
- 接口用例与数据分离（写用例的人不用碰代码）
- 数据驱动 + fixture + ApiClient 三件套组合实战

---

*笔记由 AI 根据当日学习内容整理。*
