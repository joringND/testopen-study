# Day28 学习笔记：xfail 预期失败 + 断言技巧

> 日期：2026-10-28
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 5 周 · Day28
> 状态：✅ 练习 2 passed 1 xfailed；自测 5/5 满分
> 里程碑：会用"预期失败"管理已知bug + 断言技能树（语义化/异常/先挂先停）

---

## 一、今日目标

1. `@pytest.mark.xfail`：已知 bug / 未实现功能 → 预期失败（不算失败）
2. 断言技巧：断言语义化、pytest.raises、先挂先停机制

## 二、今日涉及文件

| 操作 | 文件 | 改动 |
|---|---|---|
| 【新建】 | `day28_homework.py` | xfail 用例 + raises + 断言修正 + demo 验证 |

（mock、api_client、conftest 均未改动）

## 三、知识点 1：xfail 预期失败

```python
@pytest.mark.xfail(reason="已知bug:/get_orders 接口未实现")
def test_get_orders():
    resp = requests.get("http://127.0.0.1:8000/get_orders", timeout=5)
    assert resp.status_code == 200
```

| 情形 | 结果 |
|---|---|
| 标记的用例**失败** | → **XFAIL**（黄色，不占失败红） |
| 标记的用例**通过** | → **XPASS**（默认算"惊喜"） |
| `strict=True` | → XPASS 变成**失败**（bug 已修就该摘掉 xfail） |

**与 skip 的区别**：

```
skip  → 用例根本不执行（我不测了）
xfail → 用例照常执行，只是"结果早就知道"（测了，但知道会挂）
```

**真实用途**：已知 bug、接口未实现（先挂用例等开发）、环境限制。

## 四、知识点 2：断言技巧

### ① 断言语义化（失败时提示直接显示）

```python
assert data["code"] == 0, f"登录失败！实际返回: {data}"
```

失败输出：
```
E  AssertionError: 登录失败！实际返回: {...}    ← 提示
E  assert 404 == 0                              ← 实际值 vs 期望值
```

### ② pytest.raises 断言"预期抛异常"

```python
def test_divide_error():
    with pytest.raises(ZeroDivisionError):   # 预期这段会抛异常
        1 / 0                                 # 没抛 → 用例失败
```

### ③ 断言"存在"用 in

```python
assert "token" in data.keys()
```

## 五、核心机制：断言"先挂先停"

**assert 失败 = 立即抛 AssertionError = 函数当场终止，后续断言不执行**：

```python
assert resp.status_code == 200       # 第1条：失败 → 💥 函数结束
assert data["code"] == 0, "..."      # 第2条：永远到不了
```

- **每条断言自带提示**：提示只在它**自己那条失败时**显示
- **从外到内三层断言**：状态码 → 业务 code → 关键字段（外层挂了内层没意义——404 的响应 body 里可能没有业务字段）
- 定位"挂的是哪条"→ 每条断言配自己的提示

## 六、今日实战记录

### ① 断言查错 key（项目感在断言的落地）

`test_get_user` 断言 `"token" in data.keys()` 失败——**token 在 /login 返回里，不在 /get_user 返回里**：

| 接口 | 返回 keys |
|---|---|
| `POST /login` | code, **token**, msg |
| `GET /get_user` | code, name, age ← 没有 token |

修正：get_user 断 name/age；验证登录态查 `client.token`（login 时存的对象属性）。
**教训**：写断言前先查速查表/print(resp.json())/.keys()——"写不出断言 = 不知道返回有哪些 key"。
（顺带：报错里的 `'\u5f20\u4e09'` 是"张三"的 Unicode 编码，不是乱码。）

### ② 先挂先停验证（demo）

注释掉第 1 条断言后，第 2 条提示 `② 业务code不对` + `assert 404 == 0` 正常打印——机制闭环。

### ③ xfail 实战

`test_get_orders` XFAIL（接口未实现先挂用例）——真实工作流：先写用例等开发。

## 六.5 答疑补录（今日新增 3 个知识点）

### ① raise / pytest.raises / assert 三兄弟对比

| | `raise`（Python 语句） | `pytest.raises`（pytest 工具） | `assert`（断言） |
|---|---|---|---|
| **角色** | **制造**异常 | **验证**异常 | **验证**条件 |
| **语法** | `raise ValueError("信息")` | `with pytest.raises(ValueError): 代码` | `assert 条件, "提示"` |
| **谁写的** | 写框架/业务代码的人 | 写测试的人 | 写测试的人 |
| **行为** | 主动抛错，程序中断 | 没抛错 → **测试失败**；抛了且类型对 → 通过 | 条件不成立 → 抛 AssertionError |
| **用在项目哪** | `api_client.py`（校验参数） | `dayXX_homework.py` | `dayXX_homework.py` |

**一句话定位**：raise=生产者（制造错误）；pytest.raises=消费者（验收"确实会抛预期错"）；assert=验收条件（结果对不对）。

**完整链路**：api_client 用 raise 拦空密码 → 测试用 pytest.raises 验证拦截生效 → assert 断言正常路径返回。

### ② conftest 的 fixture 注入机制（不 import 也能用）

- **fixture 靠"参数名"自动注入**：用例形参名 = fixture 名，pytest 自动找同名注入，**与 import 无关**
- **查找顺序**：当前文件 → 当前目录 conftest.py → 父目录 conftest 逐级往上 → 插件；找不到报 `fixture 'xxx' not found`
- `import pytest` 只为用 @pytest.mark / pytest.raises，与 conftest 注入是两回事
- **反模式**：`from conftest import client` 不要写（conftest 是让 pytest 自动加载的，不是给你 import 的）
- 只有 `@pytest.fixture` 装饰过的东西能按名字注入；普通函数不能

### ③ 接口返回的 keys vs 对象属性

- **接口返回的是数据（dict）**，查 `.keys()`；**属性是 Python 对象身上的**，点号访问
- 同一行三种访问：`data["code"]`（dict 的 key）/ `resp.status_code`（Response 属性）/ `client.token`（ApiClient 属性）
- **对象属性三查法**：
  1. **类定义**：`__init__` 里 `self.xxx =` 的就是属性（最权威）
  2. **`obj.__dict__`**：实例属性字典一行列出
  3. **`dir(obj)`**：属性+方法全列出（配合 `type(obj)` 看类型）
- **属性 vs 方法**：看有没有括号——`resp.status_code`（属性/值）vs `resp.json()`（方法/动作）

## 七、自测批改记录（5/5 满分）

| 题 | 判定 | 要点 |
|---|---|---|
| 1 xfail vs skip | ✅ | skip 不执行；xfail 执行但预期失败 |
| 2 XFAIL/XPASS/strict | ✅ | XFAIL=跑了预期失败；XPASS=竟然通过；strict 后 XPASS 不被允许 |
| 3 逗号后提示 | ✅ | 失败时提示直接显示（可拼实际值） |
| 4 pytest.raises | ✅ | with pytest.raises(ZeroDivisionError): 1/0 |
| 5 xfail 完整用例 | ✅ | 标记 + reason + 断言齐全 |

## 八、明日预告（Day29）

**测试报告与运行控制**：
- pytest-html 生成 HTML 测试报告（你环境已装 4.2.0）
- 运行控制：`-k` 按关键字选用例、`--tb` 报错模式、`-q` 安静模式、pytest.ini addopts 完善
- 预告题：跑完测试后，怎么把结果变成一份**能发给别人看的报告**？

---

*笔记由 AI 根据当日学习内容整理。*
