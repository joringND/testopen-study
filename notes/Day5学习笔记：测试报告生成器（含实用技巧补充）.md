# Day5 学习笔记：综合项目——测试报告生成器（本周收官）

> 日期：2026-10-06（工作日档）
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第1月 · Day5
> 状态：✅ 全部完成（含加分项：失败用例明细）

---

## 一、今日项目：测试报告生成器（完整代码）

```python
# 1. 组织数据：列表 + 字典（Day2）
test_cases = [
    {"name": "登录接口", "status": 200},
    {"name": "下单接口", "status": 200},
    {"name": "支付接口", "status": 500},
    {"name": "退款接口", "status": 404},
    {"name": "查询接口", "status": 200},
]

# 2. 遍历 + 判断 + 统计（Day3 + Day4）
pass_count = 0
failed_cases = []                    # 加分项：收集失败用例名
print("===== 测试报告 =====")
for case in test_cases:
    case_name = case.get("name", None)
    result = "失败"
    if case["status"] == 200:
        result = "通过"
        pass_count += 1
    else:
        failed_cases.append(case["name"])
    print(f"{case_name}:{result}")
print("====================")

# 3. 汇总输出（Day1 f-string）
fail_count = len(test_cases) - pass_count
pass_rate = (pass_count / len(test_cases)) * 100
print(f"共执行{len(test_cases)}条用例")
print(f"通过{pass_count}条，失败{fail_count}条")
print(f"通过率{pass_rate}%")
print(f"失败用例：{failed_cases}")
```

## 二、项目批改记录（亮点）

1. ✅ 数据组织用 列表+字典，贴近真实测试数据
2. ✅ `case.get("name")` 温柔取值（Day2 知识用上）
3. ✅ "先默认后覆盖"：`result = "失败"`，命中 200 才改"通过"
4. ✅ `fail_count` 用总数减通过数，不重复计数
5. ✅ 加分项：`failed_cases` 收集失败用例，报告输出失败明细
6. ✅ 命名优化：`case_name` / `pass_rate` / `failed_cases`（命名=注释）

## 三、本周知识总结（Day1~5）

| Day | 主题 | 关键点 |
|---|---|---|
| Day1 | 变量、字符串 | f-string、切片、命名三规则 |
| Day2 | 列表/元组/字典 | 增删改查、get()、items()、可变性 |
| Day3 | if 判断 | 冒号+缩进、先严格后宽松、兜底优化 |
| Day4 | for/while | 遍历、range、break/continue、嵌套、计数 |
| Day5 | 综合项目 | 5 个环节串起全部知识 |

## 四、本周自测批改：10 对 9

唯一错误：`"hello world".split(" ")` 的结果是 **`['hello', 'world']`（列表）**，不是 "helloworld"。split 是"切分成列表"，不是"去空格"。

## 五、踩坑记录（本周汇总）

1. `my-name` 不合法（连字符=减号）
2. 变量名不能是内置名：dict / sum / list / str / len / print...
3. 字符串引号嵌套：外层单引号内层双引号
4. `d["key"]` 报 KeyError，`get()` 更安全
5. if-elif 顺序：先严格后宽松，宽条件在前=死代码
6. while 计数器从 1 开始，且必须改变条件防死循环
7. split 返回列表
8. 嵌套循环 break 只跳最近一层

## 六、补充：实用技巧（学习提问整理）

### 1. 一个 print 输出多行：`\n` 换行符

```python
# 多行文本用 \n 连接，一个 print 搞定
print("共执行5条用例\n通过3条，失败2条\n通过率60.0%")

# f-string 里也能用
print(f"共执行{pass_count}条用例\n通过{pass_count}条，失败{fail_count}条")

# 整段文字用三引号
print("""第一行
第二行
第三行""")
```

> `\n` = 字符串里插一个换行；`\n\n` 空一行；`\t` = Tab 制表符。处理日志时天天见。

### 2. 去除字符串空格（5 种，按"去哪些"区分）

```python
s = "  hello  world  "

s.strip()               # 去首尾空格 -> "hello  world"（中间保留）
s.lstrip()              # 去左边   -> "hello  world  "
s.rstrip()              # 去右边   -> "  hello  world"
s.replace(" ", "")      # 去所有空格（含中间）-> "helloworld"
"".join(s.split())      # 去所有空白（空格/Tab/换行）-> "helloworld"
```

| 场景 | 用哪个 |
|---|---|
| 用户输入末尾带空格 | `strip()` |
| JSON 值夹空格要精确比对 | `replace(" ", "")` 或 `"".join(s.split())` |
| 日志行首尾空白再去切分 | `strip()` + `split()` |

> 记忆：strip 家族去"边"（首尾），replace/join 去"所有"（含中间）。接口断言比对时两边都 `strip()` 再比，防止"空格导致用例误报失败"。

## 七、明日预告（Day6 · 节假日）

**文件读取 + 日志状态码统计**：学 `open()`/`with` 读文件，读取一份接口日志 txt，统计各状态码出现次数——把本周知识和"真实日志处理"接上。这是第 2 月 Linux 日志排障的前置。

---

*笔记由 AI 根据当日学习内容整理，建议每周日回顾一遍。*
