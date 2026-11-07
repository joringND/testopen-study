# Day37 学习笔记：配置分离——一份代码跑多环境（第 7 周 Day1）

> 日期：2026-11-09
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 7 周 · Day37
> 状态：✅ 3 passed（--env test）；2 passed 1 skipped（--env pre）；1 failed + 2 errors（--env prod，符合预期）
> 里程碑：环境地址从用例里彻底赶出去，命令行 --env 一键切换
> 课后修复：白名单改为从 env.json 动态读取，三环境报告行为统一（见 4.3 ①）

---

## 一、今日目标

把写死在用例里的 `BASE = "http://127.0.0.1:8000"` 赶出去：环境地址集中到 `config/env.json`，用 `--env` 命令行参数切换，用例零感知。

## 二、今日涉及文件

| 操作 | 文件 | 说明 |
|---|---|---|
| 【修改】 | `conftest.py` | 新增 `pytest_addoption` + `env_name`；旧 `base_url` 注释保留，新 `base_url` 改 session 作用域 |
| 【新建】 | `day37_homework.py` | 3 条验证用例 + 练习/自测答案 |
| 【未改】 | `config/env.json` | 保持平铺结构 `{"test": url, "pre": url}`，一行没动 |

## 三、三层配置

| 层 | 位置 | 职责 |
|---|---|---|
| ① 代码层 | api_client.py / conftest.py | 只认 `base_url` 这个名字，绝不出现具体地址 |
| ② 配置层 | config/env.json | test/pre 各套地址，运维改这里 |
| ③ 用例层 | dayXX_homework.py | 只写"测什么"（数据/断言），不知道环境存在 |

**运行时链路**：`--env pre` → conftest `getoption` → 读 env.json 取地址 → client fixture 拿到 base_url → 用例无感知。

## 四、代码逐行走读（按实际提交版本）

### 4.1 conftest.py（44 行）

```python
 1  # ===== conftest.py：pytest 自动加载，fixture 全局共享 =====
 2  import json
 3  import pytest
 4  import requests
 5  from api_client import ApiClient
 6
 7  #ENV="test"# 切换环境：只改这一行(day25框架工程化使用，已废弃)
 8  # ---- 新增：注册 --env 命令行参数 ----
 9  def pytest_addoption(parser):
10      parser.addoption("--env", action="store", default="test",
11                       help="运行环境: test/pre")
12
13  @pytest.fixture(scope="session")
14  def env_name(request):
15      return request.config.getoption("--env")
16
17  # @pytest.fixture
18  # def base_url():
19  #     """测试环境基础地址——换环境只改这里"""
20  #     with open("config/env.json","r",encoding="utf-8") as f:
21  #         envs=json.load(f)
22  #         return envs[ENV]
23  # base_url从"写死的字符串"变成"查表的结果"——环境名→地址的映射放配置文件，切环境 = 改 ENV 一个字母
24  #day25框架工程化使用，已废弃
25
26  @pytest.fixture(scope="session")
27  def base_url(env_name):
28      with open("config/env.json", "r", encoding="utf-8") as f:
29          cfg = json.load(f)                 # {"test": "...", "pre": "..."}
30      assert env_name in cfg, \
31          f"环境不存在: {env_name}，可选 {list(cfg.keys())}"
32      return cfg[env_name]                   # ✅ 直接按 key 取
33
34  @pytest.fixture
35  def check_client():
36      return requests
37
38  @pytest.fixture
39  def make_token():
40      return "token123"
41
42  @pytest.fixture
43  def client(base_url):          # fixture 里用另一个 fixture（依赖注入）
44      return ApiClient(base_url)
```

| 行 | 代码 | 作用 |
|---|---|---|
| 1 | 文件头注释 | conftest 是 pytest 自动加载的"约定文件"（放在 rootdir 下，无需 import） |
| 2 | `import json` | 读 env.json 文本 → dict |
| 3 | `import pytest` | `@pytest.fixture` 装饰器 + 钩子机制 |
| 4 | `import requests` | 原有 `check_client` fixture 返回 requests 模块（供旧用例 `check_client.get(...)` 用） |
| 5 | `from api_client import ApiClient` | `client` fixture 要实例化 |
| 7 | 注释 `#ENV="test"...# 已废弃` | 旧写法注释保留、标注废弃——符合"不删复习材料"的习惯 |
| 8 | 分节注释 | 好读性：标出新旧代码边界 |
| 9 | `def pytest_addoption(parser)` | **钩子函数名必须一字不差**，pytest 启动最早期自动调用 |
| 10 | `parser.addoption("--env", action="store", default="test"` | 注册参数；`action="store"` 表示存一个值（非开关）；`default="test"` 不传时默认 test |
| 11 | `help="运行环境: test/pre"` | `pytest --help` 里的说明文字 |
| 12-15 | `@pytest.fixture(scope="session") / def env_name(request) / return request.config.getoption("--env")` | `request` 是 pytest 注入的 FixtureRequest；`getoption` 取命令行字符串值，如 `"pre"`；session 作用域=全会话只算一次 |
| 17-24 | 旧 base_url 整体注释 + 第 23 行原理解释 + 第 24 行"已废弃" | 保留历史实现便于对照，不删除 |
| 26 | `@pytest.fixture(scope="session")` | 只读配置读一次就够（function 会每用例 open 一次文件） |
| 27 | `def base_url(env_name)` | 形参名 = 要依赖的 fixture 名（依赖注入）；pytest 先创建 env_name 再创建 base_url |
| 28 | `with open("config/env.json", "r", encoding="utf-8")` | `with` 自动关文件；`encoding="utf-8"` 防 Windows 默认 GBK（读中文 ini/json 的老坑） |
| 29 | `cfg = json.load(f)` | JSON 文本 → dict `{"test": "http://127.0.0.1:8000", "pre": "http://pre.api.example.com"}` |
| 30-31 | `assert env_name in cfg, f"环境不存在..."` | 防 `--env prod` 时静默 KeyError，报错直接列出可选值 |
| 32 | `return cfg[env_name]` | 返回地址字符串（平铺结构直接取 key，不加 envs 层） |
| 34-36 | `def check_client(): return requests` | 旧用例的 fixture，今天不动 |
| 38-40 | `def make_token(): return "token123"` | 旧 fixture，今天不动 |
| 42-43 | `def client(base_url)` | 用例只拿 client 就能发请求；依赖注入 base_url |
| 44 | `return ApiClient(base_url)` | function 作用域：每个用例 new 一个 client，登录态不串味 |

### 4.2 day37_homework.py（21 行用例 + 练习/自测答案）

```python
 1  import json
 2  import pytest
 3
 4
 5  def test_env_config(env_name, base_url):
 6      with open("config/env.json", "r", encoding="utf-8") as f:
 7          cfg = json.load(f)
 8      assert base_url == cfg[env_name]       # ✅ 同样直接取
 9
10
11  def test_env_name_valid(env_name):
12      assert env_name in ("test", "pre", "prod")
13
14
15  def test_real_api_only_in_test(env_name, client):
16      """真实请求只在 test 环境跑；pre/prod 是假地址，跳过"""
17      if env_name != "test":
18          pytest.skip(f"当前是 {env_name} 假环境，跳过真实请求")
19      resp = client.get_user()
20      assert resp.status_code == 200
21      assert resp.json()["name"] == "张三"
```

| 行 | 代码 | 作用 |
|---|---|---|
| 1 | `import json` | 用例自己再读一遍配置（做对照） |
| 2 | `import pytest` | 用 `pytest.skip` |
| 5 | `def test_env_config(env_name, base_url)` | 两个 fixture 注入：环境名 + 地址 |
| 6-7 | `open + json.load` | 读原始配置，拿到"标准答案" |
| 8 | `assert base_url == cfg[env_name]` | **元测试**：验证 fixture 返回值与配置文件一致——测的是"读配置这段代码"本身 |
| 11 | `def test_env_name_valid(env_name)` | 只依赖 env_name，不碰网络、不读文件 |
| 12 | `assert env_name in ("test", "pre", "prod")` | 白名单校验（⚠️ 与 env.json 不同步，已修复为读 cfg，见 4.3） |
| 15 | `def test_real_api_only_in_test(env_name, client)` | env_name 做开关，client 发真实请求 |
| 16 | docstring | 说明用例意图（报告里可见） |
| 17-18 | `if env_name != "test": pytest.skip(...)` | **skip 是黄灯不是红灯**：非 test 标记跳过，不算失败；消息会显示在报告里 |
| 19 | `resp = client.get_user()` | ApiClient 内部懒登录 + 带 Bearer 头 + 401 重登 |
| 20 | `assert resp.status_code == 200` | 状态码断言（第一层） |
| 21 | `assert resp.json()["name"] == "张三"` | 字段值断言（第三层） |

**运行时序**：

```
pytest 启动 → 注册 --env → 收集 3 条
→ 跑 test_env_config：env_name(session) 创建 → getoption → "test"
                     base_url(session) 创建 → 读 env.json → http://127.0.0.1:8000
→ 跑 test_env_name_valid：env_name 已缓存，复用
→ 跑 test_real_api_only_in_test：client(function) 新建 → 懒登录 → 请求
```

**两个作用域并存**：`env_name`/`base_url` = session（只读配置读一次）；`client` = function（每用例新建，防登录态串味）——Day31 原则的完整落地。

### 4.3 走读发现的三个细节（① 已修复，②③ 待处理）

**① 第 12 行白名单含 `prod`，但 env.json 只有 test/pre —— 报告会自相矛盾（✅ 已修复）**

改前现象：

```
--env prod 时：
  test_env_name_valid      → PASSED（白名单里有 prod，绿灯）
  test_env_config          → ERROR（base_url 的 assert 失败）
  test_real_api_only_in_test → ERROR（同上）
```

一条绿两条红，看起来像"部分功能正常"，实际是同一个配置缺失引发的。**白名单是第三份真相**（env.json 一份 + base_url 的 assert 一份 + 白名单一份），任意一份改动忘同步就会不一致。

**修法：白名单从配置读，只留一份真相。** 第 11-12 行改为：

```python
def test_env_name_valid(env_name):
    with open("config/env.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)
    assert env_name in cfg, f"环境 {env_name} 不在配置中，可选 {list(cfg.keys())}"
```

（`json` 第 1 行已导入，无需新增 import。）

**修复后实测（三环境全验证）：**

| 命令 | 结果 | 说明 |
|---|---|---|
| 默认（test） | 3 passed | 正常环境不受影响 |
| `--env pre` | 2 passed, 1 skipped | 与改前一致，skip 原因正确 |
| `--env prod` | **1 failed + 2 errors** | 统一全红，不再有误导性绿灯 |

`--env prod` 的报错直接点明根因：

```
E   AssertionError: 环境不存在: prod，可选 ['test', 'pre']
E   assert 'prod' in {'test': 'http://127.0.0.1:8000', 'pre': 'http://pre.api.example.com'}
```

**两种红的区别**（报告定位用）：

- `test_env_name_valid` → **FAILED**：用例跑起来了，断言不成立
- `test_env_config` / `test_real_api_only_in_test` → **ERROR**：`base_url` fixture 准备阶段就挂了，用例根本没执行

同一个配置缺失，表现成 1 FAILED + 2 ERROR；读懂这个区别，才知道该往"用例数据"还是"环境配置"上查。

**② 第 47-64 行自测答案里重复定义 `pytest_addoption` / `env_name` / `env_config`**

- `pytest_addoption` 定义在**测试文件里不生效**（pytest 只从 conftest / plugin 加载钩子）
- `env_name` fixture 定义在测试模块里会**覆盖** conftest 的同名 fixture（模块级优先级更高）——碰巧定义一样所以无感
- 隐患：两处不同步时，行为会悄悄变

**练习代码建议放独立文件（如 `day37_selftest.py`）或注释掉**，别混在正式用例文件里。

**③ 模块顶层 `print`（第 23-46 行）会在收集阶段执行**

pytest 收集 = import 模块 = 执行顶层代码，这些 `print` 会跑一遍（默认被捕获，`-s` 时可见）。不影响结果，但输出会变脏。练习答案用 `# 注释` 更干净。

## 五、今日三个坑

### 1. `fixture 'env_name' not found`

只改了 `base_url` 内部，没定义 `env_name` fixture。报错里 `available fixtures` 列表可以直接看出缺哪个。

### 2. 配置结构别乱改

示例假设 `{"envs": {...}}` 包裹层，实际是平铺 `{"test": url, "pre": url}`——**以现有结构为准，代码适配它**。

### 3. 什么时候升级成对象结构

一个环境要带多个字段（base_url + db_url + app_key）时才改：

```json
{"test": {"base_url": "...", "db_url": "..."}}
```

只有一个 URL 时平铺就是最优。

## 六、答疑：作用域与 CI 选型

### base_url 用 session 还是 function？

配置**只读**、会话内不变 → `session` 读一次就够；`function` 会每个用例重复 open 文件，纯 IO 浪费。呼应 Day31 原则：会被用例改的准备用 function，只读配置用 session。

### Jenkins 里 --env 还是环境变量？

- **`--env` 更显式**：`pytest --env pre` 写在构建命令里，报错清晰
- **环境变量更通用**：`ENV=pre` 跨工具/语言复用（Docker/部署脚本都认）
- 结论：框架内用 `--env`，CI 层用变量传值（`--env ${ENV}`）

## 七、自测答案（对照）

1. 写死 BASE：换环境改 N 处、漏一处混环境；无法按环境集中管理/CI 切换
2. `pytest_addoption`：注册自定义命令行参数的钩子
3. `getoption("--env")`：返回字符串（默认 "test"，传 pre 则 "pre"）
4. session：只读配置读一次就够
5. conftest 里注册 `--env` + `env_config`（见 4.1）

## 八、明日预告（Day38）

配置分离之后：**日志体系**（用例执行日志 / 请求响应日志 / 失败现场），让跑挂的用例有迹可循。

---

*笔记由 AI 根据当日学习内容整理。*
