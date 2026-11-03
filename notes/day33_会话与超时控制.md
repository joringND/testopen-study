# Day33 学习笔记：会话与超时控制（第 6 周 Day2）

> 日期：2026-11-03
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 6 周 · Day33
> 状态：✅ 3 passed（手动重试/Adapter重试/超时）；自测 5/5 满分
> 里程碑：稳定性三件套——Session / timeout / retry

---

## 一、今日目标

接口测试"稳定性三件套"：Session 复用、超时控制、重试机制；并把 api_client.py 里已封装的那一半讲透。

## 二、今日涉及文件

| 操作 | 文件 | 改动 |
|---|---|---|
| 【修改】 | `mock_server.py` | 顶部加 FLAKY_COUNT；do_GET 加 /flaky、/slow |
| 【新建】 | `day33_homework.py` | 手动重试/Adapter重试/超时 3 用例 |

## 三、稳定性三件套

### ① Session 复用

```python
s = requests.Session()   # 连接复用 + cookie 自动管理
s.get(url)               # 同一连接池
```

- 裸 requests.get = 每次独立连接（浪费）
- Session = 框架级，登录态自动维护
- **api_client 里 `self.session` 就是它**

### ② timeout 超时

| 写法 | 含义 |
|---|---|
| 不设 | 永远等（测试卡死，大忌！） |
| `timeout=5` | 连接+读取共 5 秒 |
| `timeout=(5, 10)` | 连接 5 秒 / 读取 10 秒 |

- **api_client 里 `timeout=5` 就是它**——保险丝，防挂死

### ③ retry 重试

```python
# 手动重试（命令式）：for 循环自己写
for i in range(3):
    resp = requests.get(url, timeout=5)
    if resp.status_code == 200:
        break

# HTTPAdapter（声明式）：配一次全局生效
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
s = requests.Session()
retry = Retry(total=3, backoff_factor=0.1, status_forcelist=[500])
s.mount("http://", HTTPAdapter(max_retries=retry))
```

**关键原则**：业务失败（如 401 密码错）**绝不重试**——功能问题重试 100 次还是错；只有网络层问题（超时/500/断连）才值得重试。api_client 的 401 重登是"token 过期"特定场景，不是无脑重试。

## 四、mock 新增接口（模拟不稳定）

```python
FLAKY_COUNT = [0]      # 前 2 次 500，第 3 次 200（只增不减）

# do_GET：
elif self.path == "/flaky":
    FLAKY_COUNT[0] += 1
    if FLAKY_COUNT[0] < 3:
        self._send(500, {"code": 500, "msg": "服务暂时不可用"})
    else:
        self._send(200, {"code": 0, "msg": "ok"})

elif self.path == "/slow":
    time.sleep(2)      # 故意慢 2 秒
    self._send(200, {"code": 0, "msg": "ok"})
```

**FLAKY_COUNT 不需要 global**：改的是列表元素，不是整体重新赋值。

## 五、今日坑

1. **路径拼写错：`/flacky`**（多打个 c）→ mock 注册 /flacky、用例请求 /flaky → 404。**"路径必须一字不差一一对应"坑第 N 次重现**——mock 路径和用例请求路径是接头暗号，错一个字母就 404。
2. **/flaky 第 4 次后永远 200**：FLAKY_COUNT 只增不减，`4 < 3` 为 False → else → 200。

## 六、自测批改记录（5/5 满分 🎉）

| 题 | 判定 | 要点 |
|---|---|---|
| 1 Session | ✅ | 连接复用 + cookie 管理 + `self.session` |
| 2 timeout | ✅ | 不设=卡死；`(5,10)`=连5读10 |
| 3 重试区别 | ✅ | 手动=命令式逐请求写；Adapter=声明式全局生效 |
| 4 该/不该重试 | ✅ | 网络波动重试 / 密码错不重试 |
| 5 Adapter 代码 | ✅ | total/backoff_factor/status_forcelist 全对 |

**进阶对比**：手动重试=命令式（谁用谁写）；HTTPAdapter=声明式（配一次，整个 Session 自动生效）——框架里推荐 Adapter。

## 七、答疑补充：Session "慎用" vs "使用"

> 用户提问：之前说 Session 要慎用，为什么今天每个用例都用 Session？

**答案**：慎用的是"共享"，不是"使用"。

### 两个层面别混

```python
# 层面1：连接层（Session 的好处）——随便用，多多益善
s = requests.Session()      # 连接复用 + cookie 管理 + 挂 Adapter 重试
s.get(url)

# 层面2：状态层（Session 的坑）——共享才危险
shared_session = requests.Session()   # 一个 Session 传给所有用例 ❌
```

### 共享 Session 的坑（串味/假绿假红）

```python
# ❌ 共享同一个 Session → 状态串味
# 用例A：shared_session 登录了 vip → 带上了 vip 的 token
# 用例B：还用 shared_session → 拿到的是 A 留下的 vip 登录态！
#        B 以为自己在测 test 用户，实际带着 vip 的 token —— 假绿/假红

# ✅ 每个用例自己 new 一个 → 互不干扰
def test_a():
    s = requests.Session()   # 独立
def test_b():
    s = requests.Session()   # 全新，干净
```

### 今天为什么每个用例都用 Session（是对的）

`test_adapter_retry` 自己 `s = requests.Session()`——**每用例一个独立实例**：连接复用、重试配置照拿，但登录态/cookie 互不污染。这是标准姿势，不是滥用。

### 和 Day31 错题完全同构

```
共享同一个 Session（跨用例） = session 作用域思维 = 污染源 ❌
每个用例 new 一个 Session    = function 作用域思维 = 干净 ✅
```

项目里 client fixture 默认 function 作用域 → 每用例 new 一个 ApiClient → 每个 ApiClient 有自己的 self.session → **天然每用例一个 Session**，框架没踩共享坑。

### 一句话记忆

> **Session 要"每用例一个"地用，不要"全部用例共一个"地用**——连接复用是白拿的好处，共享状态才是坑。

## 八、明日预告（Day34）

接口框架进阶 Day3：**数据驱动进阶**——把接口测试用例做成"数据 + 用例"分离，一份数据驱动 N 条用例（第 4 周学了雏形，这次上真接口）。

---

*笔记由 AI 根据当日学习内容整理。*
