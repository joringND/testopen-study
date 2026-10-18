# Day21 学习笔记：requests 进阶（POST / headers / session / JSON 断言）

> 日期：2026-10-19
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 4 周 · Day21
> 状态：✅ 练习 9 passed（6 用例 + 3 参数化）
> 主题：从"测状态码"升级到"测真实业务接口"

---

## 一、今日目标

真实业务接口 = **带数据的请求 + 登录态 + 响应体断言**。今天把 mock 升级成业务靶场，学 requests 四件套。

## 二、四件套知识点

| 技能 | 用途 | 关键写法 |
|---|---|---|
| POST 请求 | 登录/下单/提交 | `requests.post(url, json={...})` |
| headers | 认证/内容类型 | `headers={"Authorization": "Bearer token123"}` |
| session | 保持登录态 | `s = requests.Session()` |
| JSON 断言 | 测业务字段 | `data = resp.json()` → `assert data["code"] == 0` |

### ① POST + json= 参数

```python
resp = requests.post(
    "http://127.0.0.1:8000/login",
    json={"user": "test", "pwd": "123"},   # json= 自动转 JSON + Content-Type
    timeout=5,
)
print(resp.json())   # {'code': 0, 'token': 'token123', 'msg': '登录成功'}
```

**data= vs json=**：

| 参数 | 传什么 | Content-Type | 适用 |
|---|---|---|---|
| `data=` | 表单字符串/字典 | application/x-www-form-urlencoded | HTML 表单 |
| `json=` | 字典/列表 | application/json | **接口测试 90% 用这个** |

### ② headers：手动带认证

```python
resp = requests.get(
    "http://127.0.0.1:8000/get_user",
    headers={"Authorization": "Bearer token123"},
    timeout=5,
)
```

- headers 一般传：**token（认证）、Content-Type、User-Agent、Cookie**
- 不带 header → 服务器返回 401（未登录）

### ③ session：登录一次，自动带 cookie

```python
s = requests.Session()
s.post("http://127.0.0.1:8000/login", json={"user": "test", "pwd": "123"})
# 后续请求不用手动带 token —— session 自动带上服务器种的 cookie
resp2 = s.get("http://127.0.0.1:8000/get_user")
```

| | 裸 requests.get | session |
|---|---|---|
| cookie | 每次手动带 | 登录一次自动带 |
| 连接 | 每次新建 | 复用（更快） |
| 适合 | 一次性请求 | 同一用户多步操作（登录→查询→下单） |

### ④ 三层断言

```python
assert resp.status_code == 200      # 1. HTTP 层
assert data["code"] == 0            # 2. 业务码
assert data["token"] == "token123"  # 3. 关键字段
```

**三层断言 = 接口测试真的在测业务**。

## 三、mock_server.py 升级（v2 业务靶场）

新增能力（代码见当日教程）：
- `POST /login`：正确账密 → 200 + `{code:0, token:"token123"}` + **Set-Cookie**；错误 → 401
- `GET /get_user`：校验 `Authorization: Bearer token123` **或** `Cookie: token=token123` → 返回张三；否则 401
- `GET /status/<code>`：保留旧功能
- `POST /echo`：回显收到的 JSON

## 四、今日踩的坑（2 个命令坑 + 1 个协议坑）

### 🐛 坑1：把 shell 命令打进了 Python 交互环境

```
PS D:\...> & python.exe            ← 不带参数 → 进了 Python REPL
>>> & python.exe day21_lesson.py   ← 在 >>> 里敲 shell 命令 → SyntaxError
```

**认准提示符**：
- `PS>` / `C:\>` = shell，跑命令（& python.exe、cd、git、pip）
- `>>>` = Python 交互环境，只能写 Python 代码 → 退出用 `exit()`

### 🐛 坑2：python.exe 后面漏了 -m

```
python.exe pytest day21_homework.py -v   ❌ Python 把 pytest 当文件名 → can't open file 'pytest'
python.exe -m pytest day21_homework.py -v  ✅
```

**记法**：`-m pytest` 是一组，紧跟 python.exe；`-v`/`--html` 才是 pytest 的参数。

### 🐛 坑3：https:// 连明文 HTTP（Day18 坑9 复发）

```
HTTPSConnectionPool(host='127.0.0.1', port=8000) ... WRONG_VERSION_NUMBER
```

- 报错关键词：**HTTPSConnectionPool** = 你写了 https://
- mock 是明文 HTTP → 统一用 `http://127.0.0.1:8000`

## 五、练习批改记录（9 passed）

| 用例 | 判定 |
|---|---|
| test_login_ok（3 层断言） | ✅ |
| test_login_fail（401 + code + msg） | ✅ |
| test_login_headers（正例） | ✅ |
| test_login_headers_fail（反例 401） | ✅ |
| test_session（不手动带 token） | ✅ |
| test_check_code×3（参数化：0/401/401） | ✅ |
| test_login_code（自测4） | ✅ |

**改进点**：练习统一写成 pytest 函数（顶层裸 assert 会在收集阶段执行，失败会拖垮整个文件）。

## 六、自测批改记录

| 题 | 判定 | 要点 |
|---|---|---|
| data= vs json= | ✅ | 表单 vs JSON + Content-Type |
| headers 传什么 | ✅ | token + Content-Type（+User-Agent/Cookie） |
| session vs requests.get | ✅ | 自动带 cookie + 复用连接 |
| POST 断言 code==0 | ✅ | |
| token 过期怎么办 | ✅ | 重新获取/脚本自动拿 token；进阶=401 自动重试机制 |

## 七、答疑补充：HTTP 凭证三连问（用户追问）

### Q1：什么时候用 GET，什么时候用 POST？

**一句话：这个操作是"查"还是"改"？**

| | GET | POST |
|---|---|---|
| 语义 | 查数据（读） | 提交/创建（写） |
| 副作用 | 无（不改服务器状态） | 有（服务器要干活/存数据） |
| 数据放哪 | URL 里（query string） | 请求体里（body） |
| 例子 | 查用户、搜索、看订单 | 登录、下单、提交表单 |
| 类比 | "菜单上有啥？" | "我要点这个菜" |

**口诀：不改变服务器数据 → GET；要服务器干活 → POST。** 登录为什么是 POST？因为登录会"改变服务器状态"（生成 session、记录登录态）。

### Q2：session 登录时没输入 token，它从哪来？

**token 不是"输入"的，是登录时服务器"发"给你的，session 替你存着、替你带上。**

4 步流程：
1. `s.post("/login", json={...})` → 客户端把账号密码发给服务器
2. 服务器验证通过 → 响应头 `Set-Cookie: token=token123`（把登录凭证塞进 cookie 下发）
3. **session 自动把 cookie 存进 `s.cookies`**（你什么都没做，session 替你保管）
4. `s.get("/get_user")` → session **自动带上** `Cookie: token=token123` → 服务器认你 → 返回数据

> 验证方法：登录后打印 `s.cookies`，能看到 session 替你存了 `token=token123`。
>
> 对比裸 `requests.get`：它没有"存"的能力 → 每次必须手动 `headers={"Authorization": "Bearer token123"}`。

### Q3：token 和 cookie 是一个东西吗？

**不是，但常常"装在一起"传。**

| | Cookie | Token |
|---|---|---|
| 是什么 | HTTP 协议的一种**机制**：服务器下发、客户端保存并自动回传的一小段数据 | 一段**身份凭证字符串**（mock 里是 "token123"，真实项目是 JWT——带加密签名和有效期的字符串） |
| 回答的问题 | "怎么带凭证"（快递盒） | "凭证是什么"（盒子里的身份证） |
| 怎么传 | 登录响应 Set-Cookie 下发，之后浏览器/session **自动**带上 | 可放 cookie 里传，也可放 **header** 里传（`Authorization: Bearer token`） |
| 谁能自动带 | 浏览器/session 自动带 | 不会自动带，需程序放 header（除非装进 cookie） |

**三种常见形态**：

```python
# 形态1：token 装进 cookie 带（session 自动带）
#   登录 → Set-Cookie: token=token123 → session 自动带上

# 形态2：token 放 header 带（手动）
headers = {"Authorization": "Bearer token123"}

# 形态3：token 在响应体返回，程序自己存、自己带
data = resp.json()
my_token = data["token"]        # 从响应体拿
headers = {"Authorization": f"Bearer {my_token}"}
```

**一句话**：token 是"身份证"，cookie 是"自动送身份证的快递机制"——token 常被装进 cookie 或 header 里传递。真实项目里 JWT（token）越来越主流：能加密、能跨域、服务端不用存状态。

## 八、进阶预告：token 自动刷新机制（Day23 实现）

```
请求 → 返回 401（token 过期）
   → 自动重新登录拿新 token
   → 用新 token 重发刚才失败的请求
   → 用例依然通过（用户无感）
```

## 九、今日新收获

1. POST + json= 传数据、data= vs json= 区别
2. headers 认证（Bearer token）
3. session 自动带 cookie / 复用连接
4. 三层断言（HTTP 状态码 → 业务 code → 关键字段）
5. mock 业务靶场：登录态 + JSON 接口
6. 认终端提示符（PS> / C:\> / >>>）、python -m pytest 格式

## 十、明日预告（Day22）

**面向对象初体验**：类 / 对象——为封装 API 客户端打地基。
- 什么是类、什么是对象
- 属性（数据）和方法（行为）
- 为什么接口测试要封装（重复代码 → 一个类搞定）

---

*笔记由 AI 根据当日学习内容整理。*
