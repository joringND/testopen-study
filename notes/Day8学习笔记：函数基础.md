# Day8 学习笔记：函数基础

> 日期：2026-10-07
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第2周 · Day8
> 状态：✅ 全部完成（练习1✅、练习2修正后✅、练习3✅、自测5题全对）

---

## 一、今日核心：函数 = 可复用的"加工车间"

输入（参数）→ 函数体（处理逻辑）→ 输出（return 返回值）。定义一次，处处调用。

## 二、知识点

### 1. 定义 + 调用

```python
def greet(name):              # def + 函数名 + (参数) + 冒号
    print(f"你好，{name}")     # 函数体（缩进表示归属）

greet("张三")                 # 先定义后调用
```

### 2. 返回值 return

```python
def add(a, b):
    return a + b              # 把结果"交出去"

result = add(3, 5)            # result = 8
```

- `return` 三件事：交回结果、立即结束函数、没写 return 默认返回 `None`

### 3. 默认参数

```python
def login(username, password="123456"):   # 默认参数可省
    ...

login("admin")                # 密码用默认值
login("admin", "888888")      # 覆盖默认值
```

⚠️ 铁律：**默认参数必须放在普通参数后面**，否则语法错误。

## 三、今日最重要概念：print vs return

| | print | return |
|---|---|---|
| 作用 | 输出到屏幕（说给人听） | 把结果交给调用者 |
| 结果可用性 | 看完就没了 | 可存变量、可传递、可写报告 |
| 测开场景 | 调试时看输出 | 结果写进测试报告 |

```python
# ❌ print：调用处拿不到结果
def check_status(code):
    print("通过")

# ✅ return：结果可以接着用
def check_status(code):
    return "通过"

result = check_status(200)    # 存进变量
print(result)                 # 调用处想打印再打印
```

> 测开原则：**函数用 return 交结果，用 print 做调试**。判断结果要进测试报告，就必须 return。

## 四、测开场景封装（今天示例）

```python
# 状态码判断函数
def check_status(status_code):
    if status_code == 200:
        return "通过"
    elif status_code == 404:
        return "接口不存在"
    elif status_code == 500:
        return "服务器错误"
    else:
        return "其他异常"

# 通过率计算函数（round 保留小数）
def cal_pass_rate(passed, total):
    return round(passed / total * 100, 1)
```

## 五、练习批改记录

| 项目 | 判定 |
|---|---|
| 练习1 show_case 定义+调用3次 | ✅ |
| 练习2 check_status | ⚠️ 原用 print，已纠正为 return |
| 练习3 get_avg（round + 默认参数 unit） | ✅ 完美 |
| 自测 5 题 | ✅ 全对（第4题主动用 return，学以致用） |

## 六、明日预告（Day9）

**可变参数 `*args` / `**kwargs`**：参数个数不确定时怎么办？
- `*args`：接收任意多个位置参数（打包成元组）
- `**kwargs`：接收任意多个关键字参数（打包成字典）
- 测开场景：写通用封装时（如"任意传参数给接口请求"）天天用

---

*笔记由 AI 根据当日学习内容整理。*
