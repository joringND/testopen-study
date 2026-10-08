# Day9 学习笔记：可变参数 *args / **kwargs

> 日期：2026-10-09
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第2周 · Day9
> 状态：✅ 全部完成（练习1✅、练习2✅、练习3格式修正✅、自测5题全对）

---

## 一、核心机制：可变参数"打包"

| 语法 | 接收内容 | 打包成 | 用法 |
|---|---|---|---|
| `*args` | 任意多个**位置参数** | 元组 | `for n in args` 遍历 |
| `**kwargs` | 任意多个**关键字参数** | 字典 | `for k, v in kwargs.items()` |

记忆：一个星 = 位置参数（元组）；两个星 = 关键字参数（字典）。名字约定俗成用 args/kwargs。

## 二、知识点

### 1. *args：任意位置参数 → 元组

```python
def sum_all(*nums):
    total = 0
    for n in nums:
        total += n
    return total

print(sum_all(1, 2, 3))           # 6
print(sum_all(10, 20, 30, 40))    # 100（传几个都行）
```

### 2. **kwargs：任意关键字参数 → 字典

```python
def build_case(**kwargs):
    return kwargs                 # 打包成字典返回

case = build_case(name="登录", method="POST", expect=200)
print(case)                       # {'name': '登录', 'method': 'POST', 'expect': 200}
```

### 3. 参数顺序铁律

```python
def func(a, b=10, *args, **kwargs):   # 唯一正确顺序
    pass
```

**位置参数 → 默认参数 → `*args` → `**kwargs`**

### 4. 测开场景：通用接口请求封装（第 6 月接口自动化正式用）

```python
def send_request(url, method="GET", **kwargs):
    print(f"请求：{method} {url}")
    print(f"附加参数：{kwargs}")     # 不同接口传不同参数，通吃

send_request("/api/login", method="POST",
             params={"username": "admin"},
             headers={"Content-Type": "application/json"},
             timeout=10)
```

## 三、练习批改记录

| 项目 | 判定 | 备注 |
|---|---|---|
| 练习1 sum_all 求和 | ✅ | *args 遍历 + return |
| 练习2 build_case | ✅ | 首次用 print，已纠正为 return（概念内化） |
| 练习3 run_cases | ✅ | 补 for 循环逐个打印 + 格式 `[{env}]` `：` |
| 自测 5 题 | ✅ | 元组/字典/顺序/求和/遍历全对 |

## 四、今日要点复盘

1. `*args` 收进来就是为了**遍历**（for 循环拆开用）
2. **函数用 return 交结果，print 只做调试**——build_case 造完用例必须 return 给测试模块
3. 参数顺序铁律面试必考
4. 封装思维：send_request 一个函数，接收所有接口的不同参数——这就是"通用工具"

## 五、明日预告（Day10）

**异常捕获 try-except**：程序报错不崩溃，优雅处理
- try / except / else / finally
- 捕获特定异常（KeyError、FileNotFoundError）
- 测开场景：用例执行遇到报错 → 记录失败继续跑，而不是整个脚本崩掉

---

*笔记由 AI 根据当日学习内容整理。*
