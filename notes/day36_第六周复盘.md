# Day36 学习笔记：第 6 周复盘大考（接口框架进阶毕业）

> 日期：2026-11-08
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 6 周 · Day36
> 状态：✅ 大考 8/10 及格，第 6 周毕业
> 里程碑：接口框架四根柱子全部立起——上传下载 / 会话超时 / 数据驱动 / 结构断言

---

## 一、本周知识地图

| 天 | 主题 | 核心产出 | 代表坑 |
|---|---|---|---|
| Day32 | 文件上传/下载 | `files=` + multipart(cgi) / `stream=True` + iter_content | do_POST 一刀切、Content-Disposition 拼错 |
| Day33 | 会话与超时 | Session 复用 / timeout / Retry+HTTPAdapter | `/flacky` 拼错、认证错位 |
| Day34 | 数据驱动 | json 外置 + parametrize（1 用例 × N 数据） | 端口 8080/8000、for≠parametrize |
| Day35 | 接口断言 | key 集合 / 类型 / 嵌套 + assert_structure | ApiClient() 缺 base_url、bool 子类 |

**主线**：能发请求 → 能控请求（超时/重试/复用）→ 能批量测（数据驱动）→ 能深断言（结构）。

**本周用例**：3 + 3 + 4 + 6 = **16 passed**。

## 二、大考成绩：8/10

| 题 | 分 | 判定 |
|---|---|---|
| Q1 上传 files= + 三断言（code/filename/size） | 1 | ✅ |
| Q2 stream=True 不占内存 + iter_content 分块 | 1 | ✅ |
| Q3 Session 两层 + 慎"共享"非"使用" | 1 | ✅ |
| Q4 timeout=(连接5, 读取10) + 不设会卡死 | 1 | ✅ |
| Q5 网络波动可重试/密码错不可 + status_forcelist | 1 | ✅ |
| **Q6 parametrize 执行阶段** | **0** | ❌ 答成执行阶段，应为**收集阶段** |
| Q7 for 循环 vs parametrize（1条 vs N条 + 三后果） | 1 | ✅ |
| Q8 断言四层 + 漏结构 bug | 1 | ✅ |
| Q9 bool 子类 + set() 集合断言 | 1 | ✅ |
| **Q10 综合代码** | **0** | ❌ 遍历对象错 + 字面 key + 未做 2 组场景 |

## 三、错题纠正

### 1. parametrize 在收集阶段执行（高频考点）

```
收集阶段（collection，import 时）→ 展开用例 → 运行阶段（call）
```

- `@pytest.mark.parametrize` 的数据函数（如 `load_cases()`）在**收集阶段**执行
- 所以 pytest 必须先知道"有几条用例"（4 条）才能收集
- 数据文件不存在 → **收集就报错**，用例还没跑就挂了
- 记忆：**先展开、再收集、最后运行**

### 2. assert_structure 两处致命 bug

```python
# ❌ 错
for k, t in data.items():            # 遍历了 data（拿到值不是类型）
    assert isinstance(data["k"], t)  # "k" 是字面字符串，不是变量

# ✅ 对
for k, t in schema.items():          # 遍历 schema（字段 → 期望类型）
    assert isinstance(data[k], t)    # data[k]，k 是变量
```

- 遍历对象错 → `t` 拿到的是值，`isinstance` 会崩
- `data["k"]` 是字面 key，永远取不到循环变量

### 3. Q10 正确版（2 组请求头场景）

```python
def assert_structure(data, schema):
    assert set(data.keys()) == set(schema.keys()), \
        f"字段不符: 实际={sorted(data.keys())} 期望={sorted(schema.keys())}"
    for k, t in schema.items():
        assert isinstance(data[k], t), \
            f"{k} 类型错: 实际 {type(data[k]).__name__} 期望 {t.__name__}"


@pytest.mark.parametrize("scene,schema", [
    ("normal",   {"code": int, "order_id": str, "amount": float}),
    ("tampered", {"code": int, "msg": str}),        # 401 的返回体结构
])
def test_order_scene(client, scene, schema):
    if scene == "normal":
        data = client.get_order().json()
    else:
        resp = requests.get(f"{BASE}/get_order",
                            headers={"Authorization": "Bearer bad-token"},
                            timeout=5)
        assert resp.status_code == 401
        data = resp.json()
    assert_structure(data, schema)
```

**关键认知**：**401 和 200 是两套结构**（`{code,msg}` vs `{code,order_id,amount}`），schema 跟着场景变——这正是 parametrize 管数据、fixture 管环境的价值。

## 四、本周踩坑榜（复习用）

1. **拼错即 404/拒连**：`/flacky`、`8080`、`_send_json`——路径/端口/方法名一字不差
2. **参数名**：`files=`（复数）不是 `file=`；multipart 用 `cgi` 不是 `request`
3. **认证错位**：Session 的 Cookie 对 Bearer 认证无效，要显式带 `Authorization`
4. **for 循环 ≠ parametrize**：1 条用例跑 N 遍 vs N 条独立用例
5. **bool 是 int 子类**：`isinstance(True, int)` 为 True
6. **别手动 new ApiClient()**：用 conftest 的 `client` fixture
7. **parametrize 数据在收集阶段执行**（本次错题）

## 五、第 7 周预告

第 7 周进入**接口框架工程化**：配置分离（多环境）、日志、断言封装、用例分层，把现有散装用例收成一个可维护的框架；配套开始**接口性能测试入门**（Locust 基础）。

---

*笔记由 AI 根据当日学习内容整理。*
