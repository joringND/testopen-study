# Day31 学习笔记：第 5 周复盘（大考 8/10）

> 日期：2026-11-01
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 5 周复盘 · Day31
> 状态：✅ 大考 8/10，错题回顾后通过，进入第 6 周
> 里程碑：第 5 周毕业——fixture/xfail/断言/报告/框架整合全链路

---

## 一、第 5 周知识全景（Day27~30）

| Day | 主题 | 核心能力 |
|---|---|---|
| 27 | fixture 进阶 | 参数化 / 作用域 / yield 前后置 |
| 28 | xfail + 断言 | 预期失败 / 断言语义化 / raises / 先挂先停 |
| 29 | 报告 + 运行控制 | --html / -k vs -m / --tb / addopts |
| 30 | 框架整合 | 分层思维 / run_tests.bat / 冒烟 vs 全量 |

## 二、大考成绩：8/10（2 题错，已回顾）

| 题 | 判定 | 要点 |
|---|---|---|
| 1 params 跑几次 | ✅ | params 长度决定次数（3 个值 → 3 次） |
| 2 logged_client fixture | ❌ | 见错题①（参数注入/login 返回值） |
| 3 作用域判断 | ❌ | 见错题②（会被改→function，不是 session） |
| 4 xfail vs skip | ✅ | xfail=执行后预期失败；skip=不执行 |
| 5 先挂先停 | ✅ | 第一条失败→抛异常中断→第二条不执行 |
| 6 断言提示 | ✅ | assert x, f"提示{实际值}" |
| 7 -k vs -m | ✅ | 名字匹配 vs 标记匹配 |
| 8 HTML 报告 | ✅ | --html + --self-contained-html（内嵌样式可分享） |
| 9 --tb 三档 | ✅ | no=不显示 / short=关键几行 / long=完整 |
| 10 接手项目+全量 | ✅ | 先看项目结构；run_tests.bat |

## 三、错题回顾①：fixture 代码三要素

```python
@pytest.fixture
def logged_client(client):        # ① 依赖用参数注入（conftest 的 client）
    client.login("test", "123")   # ② login 是动作，不接返回值（返回 resp 不是 client）
    yield client                  # ③ yield 的是 client 本身
    client.token = None           # ④ teardown
```

**三坑**：缺参数（NameError）；login 返回值赋给 client（resp≠client）；忘 yield 对象本身。

## 四、错题回顾②：作用域判断口诀（重点）

```
会被用例改     → function（每次新建，安全，不污染下一条）
只读且昂贵     → module（每文件一次，省资源）
全局配置       → session（最危险：共享状态=污染源）
```

**为什么会被改的用 function**：作用域越大共享越久，被用例改了 → 下一条拿到脏数据。function 每用例独立。
**记忆**：会被改→function（每次拿干净的）；共享越多风险越大。

## 五、第 6 题实战升级：语义化断言的进阶写法

第 6 题标准答案（大考满分）：`assert data["code"]==0, f"登录失败,{data}"`

实战进阶（加分项，不是错）——按场景选择：

```python
# 进阶版①：三层断言——先断状态码，再断业务 code（Day28 从外到内）
assert resp.status_code == 200, f"HTTP 状态码不对: {resp.status_code}"
assert data["code"] == 0, f"登录失败: {data}"

# 进阶版②：只挑关键字段，避免整个 dict 刷屏（响应很大时）
assert data["code"] == 0, f"登录失败: code={data.get('code')}, msg={data.get('msg')}"
```

**选择原则**：提示语要让人一眼知道"断言的哪个条件、实际值是什么"；响应大时用 `.get()` 只展示关键字段，别把整个 dict 打满屏。

## 六、第 5 周毕业能力清单

- [x] 会用参数化 fixture（笛卡尔积公式）
- [x] 会用 xfail 挂起已知 bug / 演示用例（不删不红）
- [x] 会写语义化断言（提示+实际值）
- [x] 会区分 -k（名字）/ -m（标记）
- [x] 会出可分享 HTML 报告 + 时间戳归档
- [x] 会一键运行（run_tests.bat）+ 冒烟/全量标记
- [x] 会排查认证错位（Session cookie ≠ Bearer 头）

## 七、下周预告（第 6 周：接口框架进阶实战）

- Day32 起：真实接口测试进阶——文件上传/下载、会话管理、请求重试、超时与性能基线
- 把 mock 升级 + 用例工程化（用三步法写新接口用例）
- 目标：从"会跑框架"到"能独立给新接口写完整测试"

---

*笔记由 AI 根据当日学习内容整理。*
