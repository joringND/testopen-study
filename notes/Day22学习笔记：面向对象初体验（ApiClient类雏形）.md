# Day22 学习笔记：面向对象初体验（类 / 对象 / 封装）

> 日期：2026-10-19
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 4 周 · Day22
> 状态：✅ 练习 6 passed
> 主题：为封装 API 客户端打地基——ApiClient 类雏形完成

---

## 一、今日目标

回答一个问题：**为什么接口测试要"封装"？怎么封装？**

不封装的痛：每个用例重复写 `requests.post("http://127.0.0.1:8000/login", ...)`——10 个用例写 10 遍 URL，mock 换端口要改 10 处，漏一处就挂。

**类的目的：把重复的样板收进一张图纸，造出 N 个对象直接用。**

## 二、核心概念：类 = 图纸，对象 = 实物

| 概念 | 含义 | 例子 |
|---|---|---|
| class（类） | 图纸/模板，定义"有什么属性、会什么方法" | `class ApiClient:` |
| 对象（实例） | 按图纸造出来的实物 | `client = ApiClient("http://...")` |
| 属性 | 对象的"数据" | `self.base_url`、`self.session` |
| 方法 | 对象的"行为" | `login()`、`get_user()` |
| `__init__` | 造对象时自动执行的"开工仪式" | 把属性装好 |
| `self` | 对象自己的名字，方法里靠它访问自己的属性 | `self.base_url` |

**口诀**：一个类能造无数对象；一张图纸能造 100 台机器人，每台自带自己的 base_url + session。

## 三、核心代码：ApiClient 类雏形

```python
import requests

class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url          # 属性1：地址（只写一次！）
        self.session = requests.Session() # 属性2：会话（登录态自动带）

    def login(self, user, pwd):
        resp = self.session.post(
            f"{self.base_url}/login",
            json={"user": user, "pwd": pwd},
            timeout=5,
        )
        return resp

    def get_user(self):
        resp = self.session.get(f"{self.base_url}/get_user", timeout=5)
        return resp

    def echo(self, data):                 # 练习3 新增
        resp = self.session.post(f"{self.base_url}/echo", json=data, timeout=5)
        return resp
```

**用法**：

```python
client = ApiClient("http://127.0.0.1:8000")   # 地址只填一次
client.login("test", "123")                    # 登录（session 自动存 cookie）
data = client.get_user().json()                # 查用户（自动带 cookie）
```

## 四、封装回报（自测重点）

| 场景 | 不封装 | 封装后 |
|---|---|---|
| mock 换端口 8001 | 每个用例改 URL（N 处） | 只改 `ApiClient("http://127.0.0.1:8001")` 一处 |
| 加统一超时 | 每个请求都改 | 类里改一次 |
| 登录逻辑变了 | 每个用例改登录代码 | 只改 `login()` 方法 |

## 五、今日 5 个坑（重点复盘）

### 🐛 坑1：调用方法忘了括号

```python
data = client.get_user.json()   # ❌ get_user 是方法，没括号 = 拿到函数对象本身
data = client.get_user().json() # ✅ 执行方法 → resp → 再取 .json()
```

- `client.get_user` = 方法本身（函数对象，没执行）
- `client.get_user()` = 执行方法 → 返回 resp
- **口诀：方法要"叫"它（加括号）才会干活；属性（base_url/session）才不用括号**

### 🐛 坑2：在 client 上找 json（方法返回值没接住）

```python
client.login(user, pwd)     # ❌ 调用结果丢了
data = client.json()        # ❌ client 是 ApiClient 对象，没有 json 方法

resp = client.login(user, pwd)  # ✅ 接住返回值（看类里 return 什么）
data = resp.json()              # ✅ json 是 resp 的方法
```

**记法**：方法返回什么，调用处就接什么——`login` 里 `return resp`，外面就 `resp = client.login(...)`。

### 🐛 坑3：类里方法缺 self

```python
def add(a, b):        # ❌ 没有 self
def add(self, a, b):  # ✅ 第一个参数必须是 self
```

- 调用 `calc.add(1, 2)` 时 Python 自动把 `calc` 塞给 self：`add(self=calc, a=1, b=2)`
- **口诀：类里所有方法第一参数都是 self，调用时不用传**

### 🐛 坑4：`requests.session()` 大小写

- `requests.session()` ❌（不存在）→ `requests.Session()` ✅
- **Python 区分大小写**，Session 是类名，首字母大写

### 🐛 坑5：方法接收了参数但没用（练习2）

```python
def introduce(self, name, age):   # ❌ 又重新收参数，属性白存了
    return f"我叫{name}，今年{age}岁"

def introduce(self):              # ✅ 直接用属性
    return f"我叫{self.name}，今年{self.age}岁"
```

**属性就是给方法用的**——`__init__` 存好的数据，方法里通过 `self.xxx` 取。

## 六、练习批改记录（6 passed）

| 用例 | 判定 |
|---|---|
| test_user_introduce | ✅（修正后用属性） |
| test_api_client_data_name | ✅（get_user().json()） |
| test_api_client_check_code ×3 | ✅（resp.json() 修正） |
| test_calc | ✅（add 补 self） |

## 七、自测批改记录

| 题 | 判定 | 要点 |
|---|---|---|
| 类和对象区别 | ⚠️→✅ | 类是生成对象的模板（图纸），对象是实例（实物），一个类造无数对象 |
| __init__ / self | ✅ | 造对象自动执行；self=对象自己的名字 |
| 无 __init__ 的类 | ✅ | 能用，属性需手动加 |
| Calculator.add | ❌→✅ | 方法第一参数必须 self |
| mock 改端口改几处 | ✅ | 只改 ApiClient(...) 一处（封装的价值） |

## 八、今日新收获

1. 类 = 图纸，对象 = 实物；属性（数据）+ 方法（行为）
2. `__init__` 自动执行装属性；`self` 访问自己的属性
3. **ApiClient 类雏形**：login / get_user / echo —— Day23 接口框架的地基
4. 封装价值：base_url/session 只写一次，改一处全部生效
5. 方法调用要括号、返回值要接住、方法必须带 self

## 九、明日预告（Day23）

**接口框架雏形**：把 ApiClient 升级成真正的测试框架——
- ApiClient 完整化（token 自动刷新、统一处理 401）
- conftest 里提供 `client` fixture（造好对象给所有用例用）
- 数据驱动雏形（用例数据挪到外部文件）
- **第 4 周第 1 个"框架级"产物**

---

*笔记由 AI 根据当日学习内容整理。*
