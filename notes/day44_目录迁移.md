# Day44 学习笔记：目录迁移（用例归入 `tests/`）

> 日期：2026-11-18
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 8 周 · 第 3 天
> 主题：把散在根目录的 `day*_homework.py` 全部搬进 `tests/`，用 `pytest.ini` 保住 `import`
> 验收：`pytest tests` → `86 passed, 2 skipped, 11 xfailed`；`run_tests.bat` test 同；pre → `2 passed, 1 skipped`

---

## 一、今天解决了什么

搬家之前，项目根目录是一个“什么都有”的平铺堆：用例、客户端、插件、配置、报告、mock 服务挤在一起。虽然 Day42/43 已经把代码分进 `support/` 和 `clients/`，但**用例本身还是散在根上**，结果就是三件事必须手工维护：

| 现象 | 原因 |
|---|---|
| `run_tests.bat` 里手写 11 个文件名 | pytest 不认识 `dayXX_homework.py` 这种命名 |
| 新增一个用例文件，得去改 bat，忘了就不跑 | 收集范围靠“清单”而不是“目录” |
| bat 里有一个文件名不存在，整场直接中止 | `file or directory not found` 让 pytest 放弃收集 |

今天把用例收进 `tests/`，并把“谁知道用例在哪”这件事从**人的清单**移交给了**pytest 的目录规则**。

三个数字的变化：

| 口径 | 迁移前 | 迁移后 |
|---|---|---|
| 收集方式 | bat 手写 11 个文件名 | `pytest tests` 扫整个目录 |
| 收集数量 | 48 条 | 99 条（17 个用例文件） |
| 结果 | `48 passed, 2 skipped, 7 xfailed` | `86 passed, 2 skipped, 11 xfailed` |

数字变大不是“用例变多了”，而是**以前从没被执行过的用例，现在进入了视野**（第五节）。

---

## 二、迁移后的目录结构

```
testopen-study/
├── pytest.ini                    ← 留根（决定 rootdir）
├── conftest.py                   ← 留根（pytest_plugins 装配清单）
├── run_tests.bat                 ← 留根（FILES=tests）
├── mock_server.py                ← 留根（独立进程）
├── api_client.py                 ← 留根（薄壳，被多处 import）
├── clients/                      ← 留根（http_session + test_api）
├── support/                      ← 留根（paths/env_config/api_fixtures/reporting）
├── config/env.json               ← 留根（被 paths.py 绝对路径引用）
├── data/                         ← 留根（被用例按 cwd 相对读取）
├── artifacts/  logs/             ← 留根（paths.py 已绝对化）
└── tests/
    ├── day16_homework.py
    ├── day21_homework.py ... day39_homework.py
    └── （17 个用例文件）
```

### 为什么只搬用例

一张判据表就能定死所有争议：

| 判据 | 涉及对象 | 结论 |
|---|---|---|
| 被 Python `import` 引用的 | `api_client.py` `clients/` `support/` | 留根 |
| 被**路径常量**引用计算的 | `config/` `data/` `artifacts/` `logs/`（`paths.py` 里的 `BASE_DIR`） | 留根 |
| 被 **pytest 特殊识别**的 | `pytest.ini`（rootdir）、`conftest.py`（`pytest_plugins` 只允许顶层） | 留根 |
| 独立进程 | `mock_server.py` | 留根 |
| **只是被 pytest 收集的用例** | `day*_homework.py` | **可以搬** |

一句话：**凡是“被别人按名字或按路径找”的，都不能搬；只有“只被 pytest 按目录扫”的，才能搬。**

### `support/` 为什么绝对不能搬

`support/paths.py` 第 4 行：

```python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

`support/paths.py` 往上两级 = **项目根**。如果 `support/` 搬进 `tests/support/`，往上两级就变成 `tests/`：

- `CONFIG_PATH` → `tests/config/env.json`（不存在 → Day37 的 `--env` 全链路失效）
- `ARTIFACT_DIR` → `tests/artifacts`（凭空新建一个，Day39 的落盘证据跑错地方）
- `LOG_DIR` → `tests/logs`（`log_file` 写不进预期的位置）

**这就是“路径常量必须基于一个稳定的锚点”的意义**：`__file__` 会随文件移动而变，所以只要文件位置和它推算的目标目录不在同一棵树里，一搬就错位。

---

## 三、两个机制决定成败

### 3.1 `import api_client` 为什么会断

pytest 默认的导入方式（prepend）会做一件事：把**测试文件所在的那一层目录**插入 `sys.path`。文件和目录一起变，插入点就跟着变：

| 状态 | 测试文件位置 | `sys.path` 插入点 | `import api_client` |
|---|---|---|---|
| 迁移前 | 根目录 | `D:\...\testopen-study\` | ✅ |
| 迁移后（未配置） | `tests\` | `D:\...\testopen-study\tests\` | ❌ `ModuleNotFoundError` |

解法是 `pytest.ini` 里的 `pythonpath`：

```ini
pythonpath = .
```

`pythonpath` 是 pytest 7.0 起的内置配置（8.4.2 支持，无需插件），作用是**把 rootdir 加入 `sys.path`**。

三个必须记住的细节：

1. **`.` 相对 `rootdir` 解析**，不是执行命令的当前目录，也不是配置文件所在目录
2. `rootdir` 由 `pytest.ini` 的位置决定 → **`pytest.ini` 一旦搬走，`.` 就指向错误的地方**
3. `pythonpath` 的配置项如果没写在 `[pytest]` 段内，会**静默失效**（不报错，只是不生效）

其余两种解法及为什么不选：

| 解法 | 副作用 |
|---|---|
| `tests/__init__.py` | `sys.path` 插入点上移到根，确实能解决 import；但模块名变成 `tests.day37_homework`，**nodeid 全变**，报告、bat、笔记引用都要跟着改 |
| 在 `tests/conftest.py` 里 `sys.path.insert(0, ...)` | 手写路径注入，pytest 已有官方配置项，属于多余机制；且和 `pythonpath` 混用容易看花眼 |

### 3.2 两套收集规则：给文件 ≠ 给目录

这是今天最有价值的发现。同一个文件，两种命令形式结果完全不同：

| 命令 | 收集逻辑 | 结果 |
|---|---|---|
| `pytest tests/day37_homework.py` | 显式指定**文件**，直接收集，**不检查命名** | `3 items` ✅ |
| `pytest tests` | 给**目录** → 递归 + 按 `python_files` 过滤文件名 | `0 items` ❌ |

pytest 默认只认两种文件名：`test_*.py` 和 `*_test.py`。`day37_homework.py` 一个都不匹配，所以给目录时**全被命名规则挡掉**。

这解释了一个很容易误解的现象：

> “我单文件明明能跑，为什么给目录就 collected 0 items？”

因为 pytest 对“显式点名的文件”是信任的——你说跑这个，它就跑；对“目录”才执行命名筛选——目录里有什么该收、什么不该收，它得按规则判断。

修法是加一行，但必须注意一个陷阱：

```ini
python_files = test_*.py *_test.py day*_homework.py
```

**`python_files` 是“覆盖”而不是“追加”。** 一旦写了这行，默认的 `test_*.py` / `*_test.py` 就失效了。所以必须把默认两项**显式保留**——只写 `day*_homework.py`，以后新建 `test_login.py` 反而收不到。

### 3.3 三处联动，少一处就有一个场景断

| 位置 | 改什么 | 少了会怎样 |
|---|---|---|
| `pytest.ini` · `testpaths` | `tests` | 裸跑 `pytest` 不知道去哪收（虽然命令行给路径时会被忽略） |
| `pytest.ini` · `pythonpath` | `.` | 任何形式都 `ModuleNotFoundError` |
| `pytest.ini` · `python_files` | 加 `day*_homework.py` | 单文件能跑，给目录 0 条 |
| `run_tests.bat` · `FILES` | `tests` | bat 找不到文件，整场中止 |

---

## 四、今日实录：三次卡点

### 4.1 虚警：`PytestUnknownMarkWarning`

迁移完成后第一次 `--co`，收集成功，但冒出 4 条警告：

```
PytestUnknownMarkWarning: Unknown pytest.mark.smoke - is this a typo?
PytestUnknownMarkWarning: Unknown pytest.mark.full - is this a typo?
```

而 `pytest.ini` 里明明有 `markers` 段。查证：

```
> python -m pytest --markers
@pytest.mark.smoke: 冒烟用例，验证核心链路
@pytest.mark.full: 全量回归用例
```

**markers 其实是注册成功的。** 之前的警告来自“读到的还是旧版 `pytest.ini`”（编辑器改了内容但那次执行在磁盘更新之前）。

用一条命令终结这类怀疑——把警告升级成错误，若还能收集成功就是注册生效：

```powershell
python -m pytest tests/day25_homework.py --co -W "error::pytest.PytestUnknownMarkWarning"
```

结果 `6 tests collected`，无错误。

**这条教训值得记住**：`UnknownMarkWarning` 有两种可能——真的没注册，或者读到了旧配置。**不要凭“上一次的输出”判断配置状态**，用 `--markers` 或 `-W error::` 现查一次。

### 4.2 真问题：`collected 0 items`

```
> python -m pytest tests -v
collected 0 items
no tests ran in 0.03s
```

而同一批文件单跑正常。原因就是 3.2 节：目录走了 `python_files` 过滤。加 `python_files` 后 → `collected 99 items`。

### 4.3 清单式的脆性：一个文件名不存在，整场中止

bat 第一版按“day25~day39”逐日推了 15 个文件名，实跑结果：

```
collected 0 items
ERROR: file or directory not found: tests\day26_homework.py
```

**`day26` 从来没有作业文件**（Day26 是复盘日，Day29/31 也是只有 print 的复盘脚本）。pytest 遇到第一个不存在的路径就**放弃整个收集**，连“其他文件能不能跑”都不告诉你。

这是“清单式”的第三重代价：不只是要手维护，还会**因为一个笔误把整场拖死**，而且错误信息离真相很远（看起来像“没收集到用例”，其实是“路径写错”）。

---

## 五、四个历史失败：迁移把旧债照亮了

`pytest tests` 第一次真正跑，出现 4 条失败，全部来自 `day21` / `day22`：

| 失败用例 | 报错 | 根因 |
|---|---|---|
| `day21::test_login_ok` | `assert 'token-96' == 'token123'` | 断言写死 `token123`；mock 从 Day30 起改成动态 `token-N` |
| `day21::test_login_headers` | `assert 401 == 0` | 请求头写死 `Bearer token123`，不是当前 LATEST_TOKEN |
| `day21::test_session` | `KeyError: 'name'` | 用 Session Cookie 访问 `/get_user`，而 mock 只认 `Authorization: Bearer` |
| `day22::test_api_client_data_name` | `KeyError: 'name'` | `day22` 文件里自带旧 `ApiClient` 类，用 `self.session` 发请求、不保存 Bearer token |

**共同点：全都是 Day21~22 阶段的练习代码，写死了 `token123` 或依赖 Cookie 认证，从没跟上 mock 的演进。**

它们此前一直失败，只是**从来没人跑到**——bat 的清单里没有 `day21`、`day22`。

### 关键认知

> 目录迁移**不会让旧代码变坏**，但会让旧代码的坏**暴露**。

- 清单式：跑的是“我记得的那批”，旧文件永远不会告诉你它坏了
- 目录式：跑的是“仓库里全部”，坏掉的会自己举牌

从“我以为全绿”到“我知道哪 4 条是红的”，信息量完全不同。这是迁移最实在的收益，比“目录整齐”重要得多。

### 处置：挂 xfail，不改代码

按既定约定（演示/复习用例不删、挂起来留着），四条全部转 xfail：

```python
@pytest.mark.xfail(reason="Day21 历史练习：mock 已改为动态 token，token123 断言过时", strict=False)
def test_login_ok(): ...

@pytest.mark.xfail(reason="Day21 历史练习：硬编码 Bearer token123，非当前 LATEST_TOKEN", strict=False)
def test_login_headers(): ...

@pytest.mark.xfail(reason="Day21 历史练习：mock 只认 Bearer，Session Cookie 方案不适用", strict=False)
def test_session(): ...

@pytest.mark.xfail(reason="Day22 历史练习：文件内旧 ApiClient 不保存 Bearer token，已被 Day43 新客户端取代", strict=False)
def test_api_client_data_name(): ...
```

改完 `7 xfailed → 11 xfailed`，`86 passed` 不变。

**为什么改断言是错的**：改断言等于让旧练习去追新契约，会牵出一片（`test_login_headers` 得先拿 token 再发请求，`test_session` 根本没有可行路径）。挂起来当“反面教材”，比删掉更有价值——Day30 处理 `/flaky` 和 Session 时就是这个思路。

---

## 六、bat 的取舍：为什么放弃“守 48 条”

迁移后在 bat 里有两个方向：

| 方向 | 做法 | 代价 |
|---|---|---|
| A. 守住 48 条 | 从真实清单里挑出原来那 11 个文件名，逐个加 `tests\` | 继续手工维护；新增用例不会自动纳入；文件名一变就整场中止 |
| B. 直接指向目录（采用） | `set FILES=tests` | 范围变 99 条，含 4 条历史 xfail |

选 B 的账：

| 项 | 清单式 | 目录式 |
|---|---|---|
| 新增用例 | 必须手工加，忘就不跑 | 落在 `tests/` 就自动纳入 |
| 文件改名/删除 | `file or directory not found`，整场中止 | 自动适应 |
| 覆盖范围 | 只有记得的那批 | 仓库里全部 |
| 耗时 | 2.7s | 2.8s（99 条） |

**用 0.1 秒换掉“手工维护清单”这个长期负担。**

最终 bat 关键三行：

```bat
set FILES=tests
if not "%ENV%"=="test" set FILES=tests\day37_homework.py
%PYTHON% -m pytest %FILES% --env %ENV% -v --tb=short --html=%REPORT% --self-contained-html
```

pre 分流保持不变：假域名环境下只跑 day37 的配置用例（真实请求那条自己 SKIPPED）。

### 补充：以后要“只跑精选那批”怎么办

不要回到文件名清单，用标记：

```powershell
python -m pytest tests -m smoke
```

**用标记表达“跑哪些”，比用文件名表达更稳**——这是 Day30 建标记体系时的原意，今天才真正用上。

---

## 七、坑预警

| 坑 | 现象 | 处置 |
|---|---|---|
| 只改 `testpaths` 没加 `pythonpath` | 带文件名跑就 `ModuleNotFoundError` | 两个都要加 |
| 只加 `pythonpath` 没加 `python_files` | 单文件能跑，`pytest tests` → `0 items` | 两个都要加 |
| `python_files` 只写 `day*_homework.py` | 以后新建 `test_xxx.py` 收不到 | **覆盖不是追加**，必须保留 `test_*.py *_test.py` |
| `pythonpath` 写错段 | 静默失效，不报错 | 必须在 `[pytest]` 段内 |
| 加了 `tests/__init__.py` | nodeid 变 `tests.xxx`，报告和历史记录全变 | 删掉，用 `pythonpath` |
| 把 `pytest.ini` 也搬进 `tests/` | rootdir 变 `tests`，`pythonpath` 的 `.` 指错，`logs/` `artifacts/` 全部相对错位 | 留根 |
| 把 `support/` 搬进 `tests/` | `BASE_DIR` 算成 `tests/`，配置和证据目录全错位 | 留根 |
| 从 `tests/` 目录里执行 pytest | 用例里 `open("data/x.json")` 找 `tests/data/` → `FileNotFoundError`，且报在**收集阶段** | 永远从项目根执行 |
| 用资源管理器拖拽搬文件 | Git 记成“删除+新增”，历史断成两段 | 用 `git mv` |
| bat 里出现 `tests\tests\` | `file or directory not found` | 检查是否重复加前缀 |

### 关于“从项目根执行”这条

`day23` / `day24` / `day32` / `day34` 里的 `open("data/xxx.json")` 是**相对 cwd**：

```python
with open("data/users.json", "r", encoding="utf-8") as f:
```

从项目根执行 → 解析成 `D:\...\testopen-study\data\...` ✅
`cd tests` 再执行 → 解析成 `D:\...\testopen-study\tests\data\...` ❌

而且这 4 处的 `open()` 都在**模块顶层**（不在函数里），所以它在**收集阶段（import 模块时）就执行**。cwd 错了，报错会出现在 `collected` 之前——表现为“收集就失败”，而不是“某条用例失败”。

这正好复现 Day36 复习考点：**pytest 收集 = import = 执行顶层代码**。

根治方向（以后做）：让用例改用 `paths.BASE_DIR` 拼绝对路径，就不再依赖 cwd。今天是“留根 + 从根执行”的临时契约。

---

## 八、验收证据

### 8.1 最终 `pytest.ini`

```ini
[pytest]
testpaths = tests
pythonpath = .
python_files = test_*.py *_test.py day*_homework.py
addopts = -v
markers =
    smoke: 冒烟用例，验证核心链路
    full: 全量回归用例
log_cli=true
log_cli_level=INFO
log_file=logs/run.log
log_file_level=INFO
log_format=%(asctime)s %(levelname)s %(name)s: %(message)s
log_date_format=%Y-%m-%d %H:%M:%S
```

### 8.2 单文件（迁移后第一道验证）

```
> pytest tests/day37_homework.py -v
rootdir: D:\Desktop\my_python\learn\testopen-study
configfile: pytest.ini
collected 3 items
tests/day37_homework.py::test_env_config PASSED
tests/day37_homework.py::test_env_name_valid PASSED
tests/day37_homework.py::test_real_api_only_in_test PASSED
3 passed in 0.05s
```

日志前缀是 `INFO clients.http_session` —— 说明 `clients/` 留根生效，用例走的是 Day43 新客户端。

### 8.3 目录级全量

```
> pytest tests -v
collected 99 items
4 failed, 86 passed, 2 skipped, 7 xfailed in 2.88s
```

（4 failed 为历史练习，已在第五节处置）

挂 xfail 之后：

```
86 passed, 2 skipped, 11 xfailed in 2.84s
```

### 8.4 bat 双环境

```
> run_tests.bat
86 passed, 2 skipped, 11 xfailed in 2.94s
Report: report_test_20261118_231135.html

> run_tests.bat pre
collected 3 items
tests/day37_homework.py::test_env_config PASSED
tests/day37_homework.py::test_env_name_valid PASSED
tests/day37_homework.py::test_real_api_only_in_test SKIPPED (当前是 pre 假环境，跳过真实请求)
2 passed, 1 skipped in 0.05s
Report: report_pre_20261118_231227.html
```

### 8.5 量级核对

| 指标 | 值 |
|---|---|
| 99 | 17 个文件的总用例数 |
| 86 passed | 通过 |
| 2 skipped | `day25` 的 skip 演示（`test_python_version_feature`、`test_not_implemented_yet`） |
| 11 xfailed | 原 7 条演示 + 新增 4 条历史练习 |
| 99 | 86 + 2 + 11 ✅ 归位 |

---

## 九、自测 5 题与参考答案

**Q1. 为什么 `support/` 不能跟着用例一起搬进 `tests/`？指出会算错的那个变量和具体后果。**

`support/paths.py` 的 `BASE_DIR` 由 `__file__` 往上两级推出。搬进 `tests/support/` 后，`BASE_DIR` 从“项目根”变成“`tests/`”，后果连锁：

- `CONFIG_PATH` → `tests/config/env.json` 不存在 → Day37 的 `--env` 链条断
- `ARTIFACT_DIR` → `tests/artifacts`，Day39 的失败证据落到错误位置
- `LOG_DIR` → `tests/logs`，日志写不进 `logs/run.log`

**Q2. `pythonpath = .` 里的 `.` 相对谁解析？为什么不能用“执行命令的当前目录”理解它？**

相对 `rootdir`。rootdir 由 `pytest.ini` 所在目录决定，与你在哪执行命令无关。所以 `pytest.ini` 必须留根——它一搬，`.` 就指向别处，而你在 cmd 里 `cd` 到哪并不能修正这个问题。

**Q3. 同一个文件，`pytest tests/day37_homework.py` 能收 3 条，`pytest tests` 却是 0 条，为什么？**

两套收集规则：给**文件**是显式指定，pytest 直接收，不检查命名；给**目录**才走 `python_files` 过滤（默认只认 `test_*.py` / `*_test.py`）。`day37_homework.py` 不匹配 → 目录扫到时被跳过。

**Q4. 加 `python_files = day*_homework.py` 会带来什么隐患？正确写法是什么？**

`python_files` 是**覆盖**不是追加。只写这一项，默认的 `test_*.py` / `*_test.py` 就失效，以后新建标准命名的用例文件反而收不到。正确写法必须保留默认两项：

```ini
python_files = test_*.py *_test.py day*_homework.py
```

**Q5. bat 从“11 个文件名”改成 `FILES=tests`，收益和代价分别是什么？**

收益：新增用例自动纳入，文件改名/删除不会让整场中止，覆盖范围从“记得的那批”变成“仓库全部”。

代价：从 48 条变 99 条，含 4 条历史 xfail；耗时增加约 0.1 秒；原来用 48 建立的“全绿基线”要重新定义为 99 条口径。

**关键判断**：代价是“多看见 4 条已知的债”，收益是“不再有看不见的债”。

---

## 十、本日结论

| 项 | 结论 |
|---|---|
| 技术目标 | ✅ 达成：17 个用例文件全部归入 `tests/`，根目录只剩基础设施 |
| 功能回归 | ✅ test `86 passed, 2 skipped, 11 xfailed`；pre `2 passed, 1 skipped` |
| 最大收获 | **给文件 ≠ 给目录**：显式路径不过滤命名，目录才按 `python_files` 筛 |
| 第二大收获 | 目录式回归把 4 条“从没被跑到”的历史失败照亮 → 迁移的价值不在整齐，在可见性 |
| 最大教训 | 清单式回归的脆性是三层叠加：要手维护、忘加就不跑、一个笔误让整场中止 |
| 遗留待办 1 | `day23/24/32/34` 的 `open("data/...")` 仍依赖 cwd，将来改用 `paths.BASE_DIR` |
| 遗留待办 2 | 根目录历史练习文件（`day10_exception.py` 等）未纳入 `tests/`，暂不处理 |
| 遗留待办 3 | 4 条历史 xfail 是“反面教材”，不做修复 |

### 一句话记住今天

> **搬家前先问三句：谁按名字 import 它？谁按路径常量算它？谁按目录扫它？——前两类留根，第三类搬走。**

---

## 十一、课后答疑

### 11.1 `--co` 是什么，它到底做了什么

`--co` 是 `--collect-only` 的缩写（pytest 允许按前缀缩写长参数）。

它**只走“收集”阶段，不执行测试函数体**：

```
扫描路径
  ↓  按 python_files 匹配文件
  ↓  import 每个模块
  ↓  找出 test 函数 / 类
  ↓  展开 parametrize
  ↓  生成待跑清单（items）
  ↓  ← 停在这里，打印清单，结束
     （不进入 call 阶段：断言不跑、fixture 的 setup 不执行）
```

### 11.2 它并不是“什么都不做”

因为**收集就要 import 模块，而 import 会执行模块顶层代码**：

| `--co` 时会发生 | 今天的实证 |
|---|---|
| 执行模块级语句 | `day23` / `day24` / `day32` / `day34` 顶层的 `open("data/...")` 照样读文件 |
| 打印模块级 `print` | `day29` 那种纯脚本会被打印出来 |
| 加载 `conftest`、注册 fixture **定义** | 但不执行 fixture 函数体（所以 `login` 不会被调用） |
| 触发 session 级 hook | `pytest_terminal_summary` 照样打印 `artifacts 目录共 23 个证据文件` |

这就是第七节那条坑的机制来源：**收集 = import = 执行顶层代码**。所以 cwd 错了会在 `--co` 阶段就报 `FileNotFoundError`，不必等真跑才发现。

### 11.3 今天为什么反复用它

它是**成本最低的验证手段**（0.03~0.04 秒），能在“跑用例”之前先把三类问题挡掉：

| 验证目标 | 怎么用 | 今天看到了什么 |
|---|---|---|
| 配置是否被读到 | 看 header 的 `rootdir` / `configfile` | `rootdir` 是项目根、`configfile: pytest.ini` ✅ |
| 收集规则是否匹配 | 看 `collected N items` | `0 items` → 抓到 `python_files` 没配这个真问题 |
| 注册类配置是否生效 | `--co -W "error::pytest.PytestUnknownMarkWarning"` | 收集成功、无错误 → 证明 markers 已注册，之前的警告是旧配置残留 |

### 11.4 常用变体

```powershell
pytest tests --co -q                          # 只列 nodeid，一行一条
pytest tests --co -q | Measure-Object -Line   # 数行数
pytest tests/day25_homework.py --co           # 单文件 + 完整 header
```

### 11.5 和真跑的区别，一张表说清

| 命令 | 收集 | 执行 | 典型用途 |
|---|---|---|---|
| `pytest tests --co` | ✅ | ❌ | 调命名规则、查收集数量、验配置、验 marker 注册 |
| `pytest tests` | ✅ | ✅ | 真跑 |

一句话记：**`--co` = 只点名不考试。** 名字点错（文件没被匹配）、人数不对（parametrize 展开异常）、考场没布置好（rootdir / configfile 不对），都在这一步就露出来。

---

## 十二、下一步（Day45 预告）

第 8 周三天已走完：Day42 拆 `conftest`（六职责 → 三插件）→ Day43 拆 `ApiClient`（传输层 + 业务层 + 薄壳）→ Day44 用例进 `tests/`。

**Day45 = 第八周复盘大考**，范围与预期考点：

| 考点 | 出自 |
|---|---|
| 六职责拆成哪三个插件？`pytest_plugins` 为什么必须留在顶层 conftest | Day42 |
| hook 里抛异常为什么升级成 `INTERNALERROR` 吞掉整场 session | Day42 |
| `super().__init__` 的“一个对象两批属性”、401 重登为何留业务层 | Day43 |
| 签名 vs 函数体：什么能改、什么不能动 | Day43 |
| `pythonpath` 的 `.` 相对谁：rootdir 还是 cwd | Day44 |
| 给文件 vs 给目录的两套收集规则；`python_files` 是覆盖不是追加 | Day44 |
| 清单式 vs 目录式回归的三重代价 | Day44 |
| 综合题：给一个新项目（用例在 `cases/`，客户端在 `core/`），写出 `pytest.ini` 与目录方案 | Day42~44 综合 |

复盘前建议准备：把 `pytest.ini` 全文、`conftest.py` 三行、`support/` 四文件职责、`clients/` 两层分工各自在白纸上默写一遍。**能默写 = 真掌握；看着抄 = 只是见过。**
