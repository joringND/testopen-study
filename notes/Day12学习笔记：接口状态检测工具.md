# Day12 学习笔记：接口状态检测工具（第2周收官项目）

> 日期：2026-10-10
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第2周 · Day12
> 状态：✅ 工具验收通过（5接口全测不崩，通过率40.0%）+ 理解题完成

---

## 一、项目：接口状态检测工具

**目标**：检测多个接口的健康状态，输出测试报告，一个挂了不中断。

**用到的知识**：Day8 函数 / Day9 `*args/**kwargs` / Day10 try-except / Day11 requests+模块 / 第1周字典统计+报告格式

### 最终代码（day12_api_check.py）

```python
import requests
from my_tools import check_status

urls = [
    "https://www.baidu.com",                  # 200 → 通过
    "https://www.bing.com",                   # 200 → 通过
    "https://httpbin.org/status/404",         # 404 → 接口不存在
    "https://httpbin.org/status/500",         # 500 → 服务器错误
    "https://nonexistent-domain-abc123.com",  # 请求失败 → 异常分支
]

# check_api：返回结构化字典（不用拼接字符串）
def check_api(url, **kwargs):
    try:
        resp = requests.get(url, **kwargs)
        return {"url": url, "status": resp.status_code,
                "result": check_status(resp.status_code)}
    except Exception as e:
        return {"url": url, "status": "ERR", "result": f"请求失败：{e}"}

# check_all_apis：批量检测，统计在函数内，return 报告
def check_all_apis(*urls):
    report = {"通过": 0, "失败": 0, "失败接口": []}
    print("===== 接口检测报告 =====")
    for url in urls:
        res = check_api(url)
        print(f"{url}: {res['result']}")
        if res["result"] == "通过":
            report["通过"] += 1
        else:
            report["失败"] += 1
            report["失败接口"].append(url)
    return report

report = check_all_apis(*urls)
pass_rate = round(report["通过"] / len(urls) * 100, 1)
print(f"共检测{len(urls)}个接口\n通过{report['通过']}个，失败{report['失败']}个\n通过率{pass_rate}%\n失败接口：{report['失败接口']}")
```

### 验收输出

```
===== 接口检测报告 =====
https://www.baidu.com: 通过
https://www.bing.com: 通过
https://httpbin.org/status/404: 接口不存在
https://httpbin.org/status/500: 服务器错误
https://nonexistent-domain-abc123.com: 请求失败：HTTPSConnectionPool(...) Max retries exceeded...
共检测5个接口
通过2个，失败3个
通过率40.0%
失败接口: ['https://httpbin.org/status/404', 'https://httpbin.org/status/500', 'https://nonexistent-domain-abc123.com']
```

## 二、解题过程错误复盘（重点）

### 🐛 Bug1：`check_all_apis()` 调用没传参 → KeyError

- 现象：`report["通过"]` 报 KeyError
- 原因：`check_all_apis()` 空调用 → `*urls` 是空元组 → 循环一次没跑 → report 里"通过/失败"从未创建
- 修法：`check_all_apis(*urls)`（星号展开列表）

### 🐛 Bug2：通过率公式错误

- ❌ `通过 / 失败 * 100`
- ✅ `通过 / len(urls) * 100`（通过 ÷ **总数**，失败为 0 时也不会除零崩）

### 🐛 Bug3：用 `split()` 解析函数返回值（设计脆弱）

- ❌ `res = check_api(url).split(); res[-1]`——请求失败时错误信息含空格会被切碎，`res[-1]` 取到最后一段英文乱码
- ✅ 函数返回**字典**（结构化数据），调用方 `res["result"]` 直接取值
- 原则：**函数返回结构化数据，不返回"给人看的字符串"**

### ⚠️ 隐患：函数内外同名 `urls`（碰巧对）

- 函数内 `*urls` = 调用传入的元组；函数外 `urls` = 全局列表
- 当时两边都恰好 5 个 → 输出碰巧正确
- 修法：统计放函数内 + `return report`，调用处接收——彻底解耦，不存在"碰巧"

### ⚠️ 遗留：验证代码混入成品

- 文件开头两个 `print(check_one(...))` 是练习验证输出，正式工具要删掉
- 原则：**工具交付前清理调试代码**

## 三、答疑记录

### Q1：为什么每个接口单独 try-except？（答错纠正）

- ❌ 曾答"整个循环包一个 try 没有问题"——**错**
- ✅ try 在循环**内**：单个接口失败被捕获，继续下一个（隔离粒度 = try 粒度）
- ❌ try 在循环**外**：第一个异常直接跳出整个循环，后面全不测
- 口诀：**try 包的是"一次动作"，不是"一整批动作"**

### Q2：`**kwargs` 传给了谁？

- 原样打包转发（透传）给 `requests.get()`：`check_api(url, timeout=3)` → `requests.get(url, timeout=3)`
- 与 Day9 `build_case` 相同点：都用 `**kwargs` 做"通用接收"——一个装参数、一个转发参数

### Q3：字典计数与 Day6 相同点

- 相同：字典计数 + `get(key, 0) + 1` 套路（先取旧值再 +1 存回）
- 元组不可变无法累计，计数必须用可变容器（字典/列表）
- 类型注意：两边都用**字符串当 key**（Day6 状态码 "200"、Day12 结果 "通过"），保持一致

### Q4：函数作用域（return 交结果）

- 函数内 `report` 是局部变量，函数外直接访问 → NameError
- 但 `report = check_all_apis(*urls)` **接收 return 的成品** → 函数外就能用
- 一句话：函数外能不能用，取决于**有没有接收 return**

## 四、第2周知识串联（Day8~12）

| 天 | 知识 | 在工具里的落点 |
|---|---|---|
| Day8 | 函数/参数/return | check_api / check_all_apis / return report |
| Day9 | *args / **kwargs | check_api(url, **kwargs) 透传 |
| Day10 | try-except | 每个接口单独容错 |
| Day11 | requests / 模块 | requests.get + my_tools import |
| 第1周 | 字典/循环/报告 | 统计 + 报告格式 |

**至此你已经能写出第一个"能拿出手"的测试工具。**

## 五、明日预告（Day13）

**日志错误行过滤脚本**：读取日志文件，过滤出报错行（ERROR/500/超时等），输出统计——把 Day6 文件读取 + 字符串匹配 + 过滤输出串起来。

---

*笔记由 AI 根据当日学习内容整理。*
