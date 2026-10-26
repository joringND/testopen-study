# Day27 学习笔记：fixture 进阶

> 日期：2026-10-26
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 5 周 · Day27
> 状态：✅ 练习全通过（6 passed + 练习4 参数化登录）；自测 4/5（1 题错题回顾）
> 里程碑：**fixture 三件套通——参数化、作用域、yield 前后置**

---

## 一、今日目标

fixture 从"会注入"升级为"会用参数、会控作用域、会做前后置"：
1. 参数化 fixture：一个 fixture 生成多组数据
2. 作用域：fixture 多久重建一次（function/module/session）
3. yield 前后置：准备（setup）→ 用例 → 清理（teardown）

## 二、今日涉及文件

| 操作 | 文件 | 改动 |
|---|---|---|
| 【新建】 | `day27_homework.py` | 参数化 fixture + 作用域对比 + logged_client + 练习4 |
| 【修改】 | `pytest.ini` | 中文注释改英文（GBK 编码雷）+ 建议删除 testpaths |

## 三、知识点 1：参数化 fixture

```python
@pytest.fixture(params=["test", "vip", "admin"])
def account(request):
    return request.param        # 当前这一轮的值

def test_account_type(account):
    assert isinstance(account, str)
```

- **params 列表有几个值 → 用例展开成几条**（不是"用例有几个参数跑几次"）
- `request.param` = 当前参数值（request 是 pytest 注入的 fixture 对象）
- 与 `@pytest.mark.parametrize` 区别：parametrize 参数化**用例**（数据驱动）；params 参数化**前置逻辑**（每次用不同数据准备环境）

**用例执行次数公式**：各参数化 fixture 的 params 长度之积（笛卡尔积）；没带 params 的 fixture 因子=1。

## 四、知识点 2：作用域

| scope | 含义 | 用途 |
|---|---|---|
| `function`（默认） | 每个用例新建 | client（登录态会变，安全第一） |
| `module` | 每文件一次 | 读一次大配置/启动一次服务（只读、昂贵） |
| `session` | 整个会话一次 | 全局配置/数据库连接 |
| `class` | 每测试类一次 | 同类用例共享 |

**判断口诀**：准备的东西会不会被用例改？会→function；不会→module。
**核心原则**：作用域越大越省资源，但共享状态风险越高。

## 五、知识点 3：yield 前后置

```python
@pytest.fixture
def logged_client(client):
    client.login("test", "123")     # setup：用例前
    yield client                    # 把值交给用例（用例在此执行）
    client.token = None             # teardown：用例后
```

- **yield 后面的值 = fixture 的返回值**（任何 Python 对象：字符串/dict/对象实例），通过用例参数名注入
- **懒加载**：fixture 第一次被用例引用才执行，不是文件加载时执行
- **生命周期**：yield 前 = 准备；yield 后 = 清理（即使用例失败，teardown 也会跑）

## 六、今日坑记录

| 坑 | 现象 | 根因 | 修法 |
|---|---|---|---|
| ① | `UnicodeDecodeError: 'gbk' codec` | 用了 **Anaconda 的 python**（d:\anaconda3）+ pytest.ini 有**中文注释**（GBK 读 UTF-8 炸） | 统一解释器 Python39 + ini 配置**别放中文** |
| ② | 新用例"没有执行" | `pytest.ini` 的 `testpaths=day25_homework.py`：不带文件名跑 → 只收集 day25 | **跑 pytest 永远带文件名**；或删 testpaths |
| ③ | 以为 "case-data" 是文件 | `yield "case-data"` 是**字符串字面量**（fixture 返回值），不是文件 | yield 值=返回值，用 print 验证 |
| ④ | fixture 不执行 | fixture 是**懒加载**——没被用例引用就不执行 | 检查用例是否被收集/引用 |

**★ 收集规则**：pytest 自动发现 `test_*.py` / `*_test.py`；dayXX_homework.py 文件名不匹配 → **必须显式指定文件名**。

## 六.5 答疑补录（今日新增 3 个知识点）

### ① 接口的"完整返回结构"怎么看？（用户长期疑问，已闭环）

**mock 各接口返回结构**（当前 v4）：

| 接口 | 成功返回 | 失败返回 |
|---|---|---|
| `POST /login` | `{"code":0,"token":"token-1","msg":"登录成功"}` | `{"code":401,"msg":"账号或密码错误"}` |
| `GET /get_user` | `{"code":0,"name":"张三","age":27}` | 401 |
| `GET /get_order` | `{"code":0,"order_id":"ORD-1001","amount":99.9}` | 401 |
| `GET /get_vip` | `{"code":0,"is_vip":true/false}` | 401 |

**三招自查（不猜）**：
1. **看 mock 源码**：`_send(200, {...})` 里的 dict = 返回结构（mock 就是自己的接口文档）
2. **打印完整响应**：`print(resp.json())`
3. **列 key**：`resp.json().keys()`；不确定用 `data.get("key", None)` 更安全

**真实项目**：有接口文档看文档；没文档就打印/抓包看实际响应。

### ② 测试文件顶层 = 只允许 import/常量/函数定义（老坑第 3 次重现）

现象：顶层贴了 `requests.get(...)` → pytest 收集（import）时直接执行 → mock 没开 → 整个文件 ERROR（0 items）。
机制：**pytest 收集 = import 模块 = 执行顶层代码**。
修法：调试脚本放独立文件（dayXX_api_check.py，用 python 跑）或用 `if __name__ == "__main__":` 保护。

### ③ 认证接口不带 token → 断连之谜 + mock 该不该有 else

现象：独立 `requests.get("/get_user")` 没带 Authorization → `RemoteDisconnected`（连接被关），而 login 正常。
根因：mock 的 `/get_user` 分支**没写 else**——if 不成立时什么都不发 → 断连（/get_order、/get_vip 都有 else 401，唯独 get_user 没有）。
修法：① 调试脚本先登录拿 token 再带 `headers={"Authorization": f"Bearer {token}"}`；② **mock 每个分支都该有 else**（认证失败回 401 而不是静默断连）——已修复。
顺带：GET 不要带 `json=`（那是 POST 的用法）。

## 七、自测批改记录（4/5）

| 题 | 判定 | 要点 |
|---|---|---|
| 1 params 作用 | ✅ | 参数化 fixture；request.param 取当前参数 |
| 2 跑几次 | ❌ | **params 长度决定次数**（不是用例参数个数）；公式=笛卡尔积 |
| 3 module vs session | ✅ | 每文件 vs 全程；大文件/起服务用 module |
| 4 yield 时机 | ✅ | 前=用例前（setup），后=用例后（teardown） |
| 5 登录+清理 fixture | ✅ | 完整正确 |

## 八、明日预告（Day28）

**xfail 预期失败 + 断言技巧**：
- `@pytest.mark.xfail`：已知 bug/未实现功能——**预期失败**≠真失败
- 断言技巧：断言语义化（`assert x == 3, "失败时给你看的提示"`）、复合断言、`in` 断言
- 预告题：`assert 1 == 2, "为什么失败"` 里逗号后面是干嘛的？

---

*笔记由 AI 根据当日学习内容整理。*
