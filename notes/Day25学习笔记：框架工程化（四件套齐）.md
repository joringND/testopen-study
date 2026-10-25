# Day25 学习笔记：框架工程化

> 日期：2026-10-25
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 4 周 · Day25
> 状态：✅ 4 passed + 2 skipped；多环境切换验证通过（ENV test/pre 双跑）
> 里程碑：**框架四件套齐——能上项目、能交付给别人用**

---

## 一、今日目标

把测试框架从"能跑"补成"能上项目"：配置文件统一口径、标记分组、跳过机制、多环境切换。

**一句话**：pytest.ini 定口径 → mark 控制"跑哪些" → skip 处理"跑不了" → 多环境处理"往哪跑"。

## 二、今日涉及文件

| 操作 | 文件 | 改动 |
|---|---|---|
| 【新建】 | `pytest.ini` | 项目根目录：testpaths + markers + addopts |
| 【新建】 | `config/env.json` | 新建 config/ 文件夹：环境名 → 地址映射 |
| 【修改】 | `conftest.py` | base_url fixture 改为从 env.json 读（ENV 变量切环境） |
| 【新建】 | `day25_homework.py` | mark 标记 + skip 演示 + 4 条真实用例 |

## 三、四件套详解

### ① pytest.ini —— 项目级配置文件

```ini
[pytest]
testpaths = day25_homework.py
markers =
    smoke: 冒烟用例，验证核心链路
    full: 全量回归用例
addopts = -v
```

| 配置项 | 作用 |
|---|---|
| `testpaths` | 不指定文件时默认收集谁 |
| `markers` | 注册自定义标记 → 消除 PytestUnknownMarkWarning + 文档化 |
| `addopts` | 每次自动追加参数 |

**收益**：跑 `python -m pytest` 不用敲文件名/参数，全项目口径统一。

### ② mark 标记 —— 分组控制"跑哪些"

```python
@pytest.mark.smoke
def test_login_ok(client): ...
```

```powershell
python -m pytest -m smoke          # 只跑 smoke
python -m pytest -m "not full"     # 跑非 full（含无标记的）
python -m pytest --co              # 只列用例不执行
```

**★ 关键机制**：`-m` 是**筛选器**——没被选中的用例**直接 deselected 不执行**（昨天看到 `4 deselected / 2 selected`）。skip 只对"被选中的"生效。

### ③ skip / skipif —— 优雅跳过

```python
@pytest.mark.skipif(sys.version_info < (3, 10), reason="需要 Python 3.10+ 的新特性")
def test_python_version_feature():
    assert True

@pytest.mark.skip(reason="该功能下个版本才实现")
def test_not_implemented_yet():
    assert False
```

**★ 门禁机制**：装饰器在**进入函数体之前**就判定跳过——函数体（含 assert）根本不会执行。所以上面一个 assert True 一个 assert False 都 SKIPPED，函数体写什么都没用。

**跳过 vs 失败**：SKIPPED = 跑不了的用例，不占失败红；FAILED = 真出错。skipif 条件成立才跳过。

### ④ 多环境切换 —— "往哪跑"由配置决定

```json
// config/env.json
{
  "test": "http://127.0.0.1:8000",
  "pre": "http://pre.api.example.com"
}
```

```python
# conftest.py
import json
import pytest
from api_client import ApiClient

ENV = "test"        # 切环境只改这一行

@pytest.fixture
def base_url():
    with open("config/env.json", "r", encoding="utf-8") as f:
        envs = json.load(f)
    return envs[ENV]

@pytest.fixture
def client(base_url):
    return ApiClient(base_url)
```

**★ 验证证据**：ENV=pre 时用例全失败且报 `<Response [502]>`（网关错误）——说明请求确实打到了 pre 地址 → 切换生效。

**本质**：base_url 从"写死的字符串"变成"查表的结果"。地址抽离成配置数据 → 一处维护、切换零改代码、CI 可用环境变量覆盖（进阶：`os.environ.get("TEST_ENV", "test")`）。

## 四、今日坑与设计教训

### 🐛 坑1：-m smoke 看不到 SKIPPED

现象：`-m smoke` 只跑 2 条，skip 用例没出现。
原因：`-m` 先筛人，被 deselected 的用例不执行；skip 只对选中的生效。
修法：全量跑（不带 -m）→ `4 passed, 2 skipped`。

### 🐛 坑2：在 login() 里加"必须 200"的断言 → 误伤失败场景用例

现象：`test_login_wrong`（期望 401）因为 login() 内 assert 200 而失败。
根因（教学疏忽，已纠正）：**框架方法不替用例做决定**——login() 被成功/失败两种场景共用，不能内置"必须成功"的假设。
教训：
- 方法管"怎么做"，用例管"对不对"
- "先验状态码再解析"的好习惯应放在**用例层**（Day21 三层断言：状态码 → 业务 code → 关键字段）
- 给框架加保护性检查前，先想：会不会误伤其他调用方？

## 五、自测批改记录（5/5 通过）

| 题 | 判定 | 补充要点 |
|---|---|---|
| markers 作用 | ✅ | 消除 warning + 文档化（--markers 可见注释） |
| -m 筛选 | ✅ | `not smoke` 会选中**无标记**用例 |
| skip vs fail | ✅ | SKIPPED 不占红；skipif 条件成立才跳过 |
| 读 env.json fixture | ✅ | 记得 import json/pytest |
| 多环境本质 | ✅ | 地址抽离成配置数据；CI 可环境变量覆盖 |

## 六、今日新收获

1. pytest.ini：testpaths / markers / addopts
2. `-m` 筛选器机制（deselected 不执行）
3. skip/skipif 门禁机制（函数体不执行）
4. 多环境查表 + 502 解读（网关错误）
5. 分层思想：框架方法不替用例做决定
6. 状态码先行的正确落点（用例层三层断言）

## 七、明日预告（Day26）

**第 4 周复盘（Day21~26 综合测试）**——接口框架阶段毕业考：
- 10 题综合测试（GET/POST、session/token/cookie、面向对象、数据驱动、框架四件套）
- 错题回顾 + 第 4 周知识全景图
- 通过即进入第 5 周：pytest 高级特性 + 框架工程落地

---

*笔记由 AI 根据当日学习内容整理。*
