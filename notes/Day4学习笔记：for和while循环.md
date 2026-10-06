# Day4 学习笔记：for / while 循环

> 日期：2026-10-06（工作日档）
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第1月 · Day4
> 状态：✅ 全部完成（代码已提交 GitHub）

---

## 一、今日目标与完成情况

| 目标 | 结果 |
|---|---|
| for 循环（遍历列表/字典、range） | ✅ |
| while 循环 + break/continue | ✅ |
| 练习 3 题 | ✅ 逻辑全对（练习3纠正次数偏差） |
| AI 自测 5 题 | ✅ 全对 |
| 附加题：嵌套循环预测输出 | ✅ 9 行全对 |

## 二、核心知识点

### 1. for 循环

```python
# 遍历列表
for case in test_cases:
    print(case)

# 带序号：enumerate（推荐）
for i, case in enumerate(test_cases, start=1):
    print(f"第{i}条：{case}")

# 遍历字典
for key in case_info:                # 默认拿 key
    print(key)
for key, value in case_info.items(): # 同时拿键值
    print(key, value)
```

### 2. range() 数字序列

```python
range(5)        # 0 1 2 3 4
range(1, 5)     # 1 2 3 4（结束不包含）
range(0, 10, 2) # 0 2 4 6 8（起始, 结束, 步长）
```

### 3. while 循环（注意计数器）

```python
attempt = 1
while attempt <= 3:
    if attempt < 3:
        print(f"第{attempt}次：失败，重试中……")
    else:
        print("第3次：成功")
        break
    attempt += 1    # 必须改变条件，否则死循环
```

### 4. break / continue

- `break`：**跳出最近一层循环**（嵌套时只影响所在层，外层继续）
- `continue`：跳过本次迭代，继续下一次
- 想跳出多层循环：用**标志位 flag**（`found = True`，外层检查后 break）

## 三、测开场景：批量执行 + 统计（测试报告雏形）

```python
# 统计状态码出现次数（报告统计核心）
status_list = [200, 200, 404, 500, 200, 404]
result = {}
for status in status_list:
    result[status] = result.get(status, 0) + 1   # get 计数一行版
print(result)    # {200: 3, 404: 2, 500: 1}
```

## 四、今日踩坑记录

1. **❌ 变量名 `sum`**：sum 是 Python 内置求和函数，不能做变量名（Day2 的 dict 教训重演）。用 `total`。内置名清单：dict/list/str/int/sum/len/print/max/min 都不能用。
2. **❌ while 计数器起始**：从 0 开始会导致失败次数多一次，需求"第3次成功"应让计数器从 1 开始。

## 五、今日练习批改记录

| 项目 | 判定 |
|---|---|
| 练习1 遍历+序号 | ✅ 已给 enumerate 优化 |
| 练习2 状态码统计 | ✅ 完美，已给 get 计数优化 |
| 练习3 while 重试 | ⚠️ 次数偏差已纠正（计数器从1开始） |
| 自测 5 题 | ✅ 全对 |
| 嵌套循环 continue 预测 | ✅ 9 行全对 |

## 六、明日预告（Day5）

**本周综合练习**：把 Day1~Day4 的知识（变量/字符串/容器/if/循环）串起来，写一个综合小项目——模拟测试报告生成器（批量处理测试数据 + 判断 + 统计 + 循环），并做本周知识自检。

---

*笔记由 AI 根据当日学习内容整理，建议每周日回顾一遍。*
