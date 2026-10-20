# Day24 学习笔记：数据驱动深化

> 日期：2026-10-21
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 4 周 · Day24
> 状态：✅ 4 passed（3 组基础 + 1 组 VIP 进阶场景）
> 里程碑：**数据驱动成为框架标配**——一行动数据 = 一个完整测试场景

---

## 一、今日目标

把 Day23 的数据驱动升级成"场景化"：一行数据里同时放**输入 + 多个接口的期望**，一条用例串起"登录→查用户→查订单→查 vip"一整串接口。

**核心公式**：一行数据 = 一个测试场景 = 输入 + 期望（+ null 驱动的条件断言）

## 二、数据驱动三段式

```
① 数据文件（data/cases.json）  →  ② 参数化注入  →  ③ 用例执行+断言
   输入 + 期望，一行一个场景       每条数据=一条用例     逻辑跟着数据走
```

```json
{"user": "test", "pwd": "123", "expect_code": 0,
 "expect_name": "张三", "expect_order": "ORD-1001", "expect_vip": true}
```

## 三、今日涉及文件（全部记录）

| 操作 | 文件 | 改动 |
|---|---|---|
| 修改 | `mock_server.py` | 加 `/get_order`、`/get_vip` 分支；VIP_USERS + TOKEN_USER（token→用户映射） |
| 新建 | `data/cases.json` | 4 组场景数据（2 成功 + 2 失败） |
| 修改 | `api_client.py` | 加 `get_order()`、`get_vip()` 方法 |
| 新建 | `day24_homework.py` | 参数化 + 条件断言 + ids 命名 |

## 四、今日新知识点

### 1. 场景化测试数据设计

- 一行 = 输入 + 期望；失败场景期望字段用 `null`（读进来 `None`）
- 布尔字段用 JSON 的 `true`/`false`（Python 读进来 `True`/`False`）
- 条件断言：`if case["expect_code"] == 0:` 登录成功才继续查——**逻辑跟着数据走**

### 2. ids 参数（用例中文名）

```python
@pytest.mark.parametrize("case", CASES, ids=[c["user"] + "-" + c["pwd"] for c in CASES])
```

`ids=[...]` 给每条数据起名字 → 报告里显示 `test-123` 而不是 `case0`——**可读性就是可维护性**。

### 3. fixture 默认作用域 = function

每个用例**独立** client（独立 token/session）→ 不串数据。接口测试 client 用 function 是对的；session 作用域会让用例共享登录态、互相污染。

### 4. 懒登录的边界（自测第 2 题核心）

登录失败时 `self.token` 仍是 None → 查用户会触发**懒登录（默认账号）**→ 可能"偷偷成功"。**所以登录失败场景绝不查用户**——条件断言就是这堵墙。

### 5. 场景设计方法论（第 4 组怎么想出来的）

**一组数据 = 一个行为假设**：
1. 列出被测对象全部行为
2. 已测的打勾
3. 没打勾的 = 新场景（先加行为，再加数据，再加断言）

## 五、今日坑记录（4 个，全复盘）

| 坑 | 现象 | 根因 | 修法 |
|---|---|---|---|
| ① | `KeyError: 'order_id'` | mock 加分支**没重启**（老进程旧代码 404）；且分支**嵌错层级**（嵌进 /get_user 内部，elif 链应兄弟平级） | elif 链平级 + 改完必重启 |
| ② | `RemoteDisconnected`（连接被断） | mock 处理 /get_vip 时**抛异常**→ handler 断连（不发响应） | 查 mock 终端 traceback、手动访问接口定位 |
| ③ | `JSONDecodeError` line 8 col 18 | JSON 语法三雷：单引号/漏逗号/尾逗号/大小写值 | 组间 `},`、最后组无逗号、字符串双引号、null/true/false 小写 |
| ④ | `KeyError: 'is_vip'` | 复制断言只改字段名、**没改变量名**（order_data 里找 is_vip） | 变量名和字段名一起核对 |
| ⑤ | `assert 401 == 0`（vip 场景） | 改了 mock 的 /login **没重启** → 老判断不认 vip | 重启 mock 再跑 |

**规律**：今日 5 个坑里，2 个是"mock 改完没重启"，1 个是"elif 层级错"——mock 操作习惯 = 改代码 → **重启** → 验证。

## 五.5 补充专题：JSON 格式小抄（坑③展开版）

JSON = JavaScript Object Notation，**数据交换格式**，纯文本、跨语言。pytest 数据驱动、接口响应、配置文件全是它——写错一个逗号整个解析就崩。

### JSON 语法 4 条铁律

1. **最外层**只能是 `{ }`（对象）或 `[ ]`（数组）
2. **键和字符串必须双引号**：`"user": "test"`（单引号、中文引号、反引号全部非法）
3. **逗号规则**：中间项以 `,` 结尾，**最后一项不带尾逗号**
4. **值类型全小写**：`true` / `false` / `null`（Python 的 `True`/`None` 在 JSON 里非法）

### JSON 值类型 ↔ Python 类型对照

| JSON | Python | 示例 |
|---|---|---|
| 字符串（双引号） | `str` | `"pwd": "123"` |
| 数字（不加引号） | `int` / `float` | `"expect_code": 0` |
| `true` / `false` | `True` / `False` | `"expect_vip": true` |
| `null` | `None` | `"expect_name": null` |
| `[ ... ]` | `list` | 外层数组 |
| `{ ... }` | `dict` | 每个场景对象 |

### 三个最高频错误（今日全踩过）

```json
// ❌ 单引号（JSON 不认）
{'user': 'test'}
// ❌ 尾逗号（最后一项后面不许有逗号）
{"user": "test",}
// ❌ Python 风格值（要小写）
{"expect_vip": True, "expect_name": None}
```

### 快速校验（写 JSON 后先跑这个，不启动 mock）

```powershell
& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -c "import json; d=json.load(open('data/cases.json',encoding='utf-8')); print('OK', len(d), '组')"
```

输出 `OK 4 组` = 语法通过。**报错里的行列号就是定位器**：`line 8 column 18` = 第 8 行第 18 个字符附近——通常是上一行漏逗号、或本行引号写错。

### 为什么 JSON 这么严格？

解析器不允许任何歧义。Python 允许单引号/尾逗号（解释器猜），JSON 一个都不猜——**JSON 就是要"机器读得懂、零歧义"**。所以手写 JSON 要像写正式公文：标点、引号、大小写全部到位。

## 五.7 补充专题：mock_server.py 逐行走读（v4 全量）

> 这是你接口框架的"靶场"，每个接口行为都在这里定义。逐段走读，★=新知识点。

### 第 0 段：模块顶部——全局状态（4 行）

```python
from http.server import HTTPServer, BaseHTTPRequestHandler   # ① 导入标准库 HTTP 服务器
import json                                                   # ② JSON 解析/生成
COUNTER = [0]        # ③ 登录次数计数。★ 为什么用列表？——列表是"可变对象"：
                       #    函数里改 COUNTER[0] 不需要 global 声明（改的是元素不是变量本身）
LATEST_TOKEN = "token-0"   # ④ 当前"最新"token。★ 函数里要给它赋值 → 必须 global 声明
VIP_USERS = {"test", "vip"}    # ⑤ 可登录的账号集合（set 去重）
TOKEN_USER = {}                # ⑥ token → 用户 映射表（dict）。★ 记录"这个 token 是谁发的"
```

**★ 核心机制预演**：`COUNTER`（登录次数）+ `LATEST_TOKEN`（每次登录都换）→ 旧 token 自然失效 → 401 闭环。`TOKEN_USER` → 知道每个 token 属于哪个账号 → 区分 vip。

### 第 1 段：Handler 类 + _send（统一发响应）

```python
class Handler(BaseHTTPRequestHandler):     # 继承标准库处理器。★ 每个请求进来 → 自动调用 do_GET/do_POST
    def _send(self, code, body):           # 自定义"统一发响应"方法（省得每处写 4 行）
        self.send_response(code)           # ① 发状态行（如 200/401/404）
        self.send_header("Content-Type", "application/json")   # ② 声明响应体是 JSON
        self.end_headers()                 # ③ 结束头部（★ 必须调用，否则浏览器/requests 等不到 body）
        self.wfile.write(                  # ④ 写响应体（★ wfile = 输出字节流）
            json.dumps(body, ensure_ascii=False)   #    dict → JSON 字符串；★ ensure_ascii=False = 中文不转义
            .encode("utf-8"))              #    字符串 → 字节（网络只传字节）
```

**★ HTTP 响应四步**：`send_response → send_header → end_headers → wfile.write`——所有响应都这四步，所以抽成 `_send`。

### 第 2 段：do_GET——路径分发（elif 链）+ 每分支认证

```python
    def do_GET(self):                      # ★ 每个 GET 请求进来，自动调用；self.path/self.headers 是该请求的信息
        if self.path.startswith("/status/"):            # ① /status/xxx：按前缀匹配
            code = int(self.path.split("/")[-1])        #    取最后一段转 int（如 /status/200 → 200）
            self._send(code, {"code": code, "msg": "status ok"})
        elif self.path == "/get_user":      # ② 精确匹配路径
            global LATEST_TOKEN             # ★ 本函数要给 LATEST_TOKEN 赋值前，必须声明 global
            auth = self.headers.get("Authorization", "")    # 取请求头 Authorization（没有就给 "")
            if auth == f"Bearer {LATEST_TOKEN}":            # 只认最新 token
                self._send(200, {"code": 0, "name": "张三", "age": 27})
            # ★ 注意：这里没写 else → 认证失败时什么都不返回（下个分支 /get_order 的 elif 也不匹配）→ 落到最外层 else 404
        elif self.path == "/get_order":     # ③ 订单接口（兄弟分支，平级）
            auth = self.headers.get("Authorization", "")
            if auth == f"Bearer {LATEST_TOKEN}":
                self._send(200, {"code": 0, "order_id": "ORD-1001", "amount": 99.9})
            else:
                self._send(401, {"code": 401, "msg": "token 过期或未登录"})   # 有 else → 明确 401
        elif self.path == "/get_vip":       # ④ vip 接口
            auth = self.headers.get("Authorization", "")
            user = TOKEN_USER.get(auth.replace("Bearer ", ""))   # ★ 字符串替换：剥掉 "Bearer " 前缀拿纯 token
                                                                 # ★ dict.get(key) → 查不到返回 None（不会 KeyError）
            if user == "test":
                self._send(200, {"code": 0, "is_vip": True})     # test 是 vip
            elif user == "vip":
                self._send(200, {"code": 0, "is_vip": False})    # vip 账号非 vip（场景区分）
            else:
                self._send(401, {"code": 401, "msg": "token 过期或未登录"})   # token 没记录 → 401
        else:
            self._send(404, {"code": 404, "msg": "not found"})  # ⑤ 兜底：路径都不匹配
```

**★ 结构规律**：do_GET = **elif 链**（路径判断，兄弟平级）→ 每个分支内再**认证判断**（if/else）。今天踩的坑 = 把 /get_order 嵌进了 /get_user 里面（层级错）→ 永不匹配。

### 第 3 段：do_POST——读请求体 + 登录 + 回显

```python
    def do_POST(self):                      # 每个 POST 请求自动调用
        global LATEST_TOKEN, COUNTER        # ★ 函数里要给这俩赋值 → 必须 global
        length = int(self.headers.get("Content-Length", 0))    # ★ Content-Length = 请求体字节数（requests 自动算好）
        body = json.loads(self.rfile.read(length)) if length else {}   # ★ rfile.read(length)：读请求体字节 → json 解析
                                                                       #    没 body 就给空 dict（防 POST 无 body 报错）
        if self.path == "/login":           # ① 登录接口
            if body.get("user") in VIP_USERS and body.get("pwd") == "123":   # 账号在集合 + 密码对 → 成功
                COUNTER[0] += 1                       # 登录次数 +1（★ 改列表元素，不需要 global 也能生效）
                LATEST_TOKEN = f"token-{COUNTER[0]}"  # 发新 token（★ 每次登录都换 → 旧 token 立即过期）
                TOKEN_USER[LATEST_TOKEN] = body.get("user")   # 记下"新 token 属于谁"
                self.send_response(200)               # 手工写响应（没走 _send，因为要加 Set-Cookie）
                self.send_header("Content-Type", "application/json")
                self.send_header("Set-Cookie", f"token={LATEST_TOKEN}")   # ★ 种 cookie（浏览器语义）
                                                                          #    我们的框架用 Authorization 头，cookie 只是保留
                self.end_headers()
                self.wfile.write(json.dumps(
                    {"code": 0, "token": LATEST_TOKEN, "msg": "登录成功"},
                    ensure_ascii=False).encode("utf-8"))
            else:
                self._send(401, {"code": 401, "msg": "账号或密码错误"})
        elif self.path == "/echo":          # ② 回显接口：把收到的 body 原样返回
            self._send(200, {"code": 0, "echo": body})
        else:
            self._send(404, {"code": 404, "msg": "not found"})
```

**★ 请求体读取流程**：`Content-Length`（多少字节）→ `rfile.read(length)`（读字节）→ `json.loads`（字节→dict）——requests 发 POST 时自动算好 Content-Length，mock 侧按长度读，缺一不可。

### 第 4 段：静音 + 启动入口

```python
    def log_message(self, *args):   # ★ 重写日志方法为空 → 不打印每次访问日志（终端干净）
        pass
if __name__ == "__main__":          # ★ 只有"直接运行"才执行下面（被 import 时不执行）——Day14 学的
    print("mock_server v3 已启动: http://127.0.0.1:8000（token 每次登录都换）")
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()   # ★ serve_forever() 死循环：一直监听 8000 端口
```

### ★ 本节新知识点汇总

1. `COUNTER = [0]` 用**可变对象**（列表）改全局，绕开 global
2. 函数内**赋值**全局变量必须 `global`（读取不需要）
3. `self.path` / `self.headers` / `self.rfile` = 每个请求的"现场信息"
4. HTTP 响应四步：send_response → send_header → end_headers → wfile.write
5. `ensure_ascii=False` + `.encode("utf-8")` = 中文 JSON 正常
6. `Content-Length` + `rfile.read(length)` = 读请求体标准流程
7. `str.replace("Bearer ", "")` 剥前缀 + `dict.get(key)` 查不到返 None
8. `log_message` 重写 = 关日志
9. `__name__ == "__main__"` 启动入口 + `serve_forever()` 常驻监听
10. **mock 生命周期**：每来一个请求 → 新建 Handler 实例 → 调对应 do_XXX → 响应 → 实例销毁

**读完这节你应该能回答**：为什么 mock 改代码必须重启？——因为 `serve_forever()` 里跑的是**启动那一刻加载的代码**，改文件不重启，进程里的还是旧代码。这也解释了今天所有"改了没生效"的坑。

## 六、核心规律：加接口 = 改三处

| 操作 | 文件数 | 内容 |
|---|---|---|
| 加测试场景 | 1 | 只改 `data/cases.json`（数据驱动红利） |
| 加接口 | 3 | mock 加分支（行为）+ api_client 加方法（调用）+ 数据/用例加断言（验证） |

**为什么**：接口 = 新被测行为。行为在 mock、调用在 client、验证在用例——三层都要动，逃不掉。

## 七、自测 5 题答案（已批改通过）

见当日对话（1 行=输入+期望；token 仍 None→懒登录；function 作用域；读 json+参数化代码；加场景 1 文件/加接口 3 文件）。

## 八、今日新收获

1. 场景化数据驱动：一行动数据串起一串接口
2. 条件断言（null 期望驱动"测不测"）
3. ids 给用例起名（可读性=可维护性）
4. fixture function 作用域防串数据
5. 行为清单 → 新场景设计方法论
6. 完整实战"加行为→加数据→加断言"三连（VIP 场景）

## 九、明日预告（Day25）

**框架工程化**：把半成品框架补成"能上项目的形状"——
- `pytest.ini` 配置文件（rootdir/超时/禁用警告）
- mark 标记分组（冒烟/全量）+ 跳过机制
- HTML 报告完整版（pytest-html）
- 多环境切换（base_url 从文件读，测试环境/预发环境一键切）

---

*笔记由 AI 根据当日学习内容整理。*
