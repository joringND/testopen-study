# Day13 学习笔记：日志分析脚本

> 日期：2026-10-11
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第2周 · Day13
> 状态：✅ 全部完成（工具跑通、自测 5 题完成）

---

## 一、日志分析五步链路

读文件 → 逐行判断 → 过滤收集 → 统计 → 报告

## 二、今日 2 个新招

### 1. 字符串匹配

```python
line = "2026-10-11 09:00:01 ERROR 登录接口 请求超时 timeout"

"ERROR" in line          # True（子串包含判断，区分大小写）
"INFO" in line           # False
line.startswith("2026")  # True（开头判断）
line.endswith("timeout") # True（结尾判断）
```

### 2. enumerate 带行号遍历

```python
with open("api_error_log.txt", "r", encoding="utf-8") as f:
    for num, line in enumerate(f, 1):   # 第二个参数 1 = 从第 1 行编号
        if "ERROR" in line:
            print(f"第{num}行: {line.strip()}")
```

**日志分析里"第几行出的错"是定位 bug 的关键信息。**

## 三、最终代码（day13_log_analysis.py）

```python
with open("api_error_log.txt", "r", encoding="utf-8") as f:
    error_count = {}
    error_list = []
    total = 0
    for num, line in enumerate(f, 1):
        total = num
        line = line.strip()
        if "ERROR" in line:
            error_list.append(f"第{num}行：{line}")
        # 关键词统计：每个关键词独立判断
        for keyword in ["500", "404", "timeout"]:
            if keyword in line:
                error_count[keyword] = error_count.get(keyword, 0) + 1

error_rate = round(len(error_list) / total * 100, 1)
print("===== 日志分析报告 =====")
print(f"总行数：{total}")
print(f"ERROR 行数：{len(error_list)}")
print(f"错误率：{error_rate}%")
print("===== 错误类型分布 =====")
for key, value in error_count.items():
    print(f"{key}: {value}次")
print("===== ERROR 行清单 =====")
for item in error_list:
    print(item)
```

## 四、验收输出（全对）

```
===== 日志分析报告 =====
总行数：10
ERROR 行数：5
错误率：50.0%
===== 错误类型分布 =====
timeout: 2次
500: 2次
404: 1次
===== ERROR 行清单 =====
第1行：2026-10-11 09:00:01 ERROR 登录接口 请求超时 timeout
第3行：2026-10-11 09:00:03 ERROR 支付接口 服务器内部错误 500
第5行：2026-10-11 09:00:05 ERROR 查询接口 连接超时 timeout
第7行：2026-10-11 09:00:07 ERROR 支付接口 接口不存在 404
第9行：2026-10-11 09:00:09 ERROR 退款接口 数据库异常 500
```

## 五、今日错误复盘（重点）

### 🐛 坑1：Day6 类型敏感复发

```python
error_count["500"] = error_count.get(500, 0) + 1
#     ↑ 写入字符串"500"     ↑ 读取整数 500 → 永远查不到 → 永远 0
```

**写 key 和读 key 必须逐字符一致**。`"500"` ≠ `500`，第二次遇到 500 不累加。

> ⚠️ 这是 Day6 讲过的坑，今天又踩了。这类"类型敏感"笔误是新手最高频错误之一，每次写字典计数前先默念：**key 的类型两边一致了吗？**

### 🐛 坑2：统计口径错（parts[-1] ≠ 关键词）

```python
parts = line.split()
error_count[parts[-1]] = ...   # 统计的是"每行最后一个字段"
```

需求是"500/404/timeout **关键词**出现次数"，却统计成了"每行最后一个词"——混入 200、900ms 等**非错误项**。

> 教训：**先明确口径再写代码**。要数什么，就只数什么。

### 🐛 坑3：字典取值用 () 圆括号（自测第5题）

```python
error_count("ERROR")   # ❌ 圆括号 = 调用函数 → TypeError
error_count["ERROR"]   # ✅ 方括号 = 取字典值
```

**区分**：字典取值用 `[]`，函数调用用 `()`。

### ⚠️ 小瑕疵

- 格式：`第{num}行，：` 多了逗号 → `第{num}行：`
- 无效代码行：`error_count['error_list']` 单独一行啥也没干，删掉

## 六、自测批改

| 题 | 判定 |
|---|---|
| in 判断子串 + 区分大小写 | ✅ |
| enumerate 作用 + 从 1 计数 | ✅ |
| strip 去换行符/首尾空格 | ✅ |
| 打印含 "500" 的行 | ✅ |
| 统计 ERROR 次数 | ⚠️→✅（() 改 []） |

## 七、明日预告（Day14 · 第2周复盘日）

**本周复盘**：第 2 周综合测试（函数/可变参数/异常/模块/requests/日志分析）+ 错题回顾 + 知识地图。周末收官。

---

*笔记由 AI 根据当日学习内容整理。*
