# Day6 学习笔记：文件读取 + 日志状态码统计

> 日期：2026-10-07（节假日档）
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第1月 · Day6
> 状态：✅ 全部完成（含接口统计加分项，代码已提交）

---

## 一、今日目标与完成情况

| 目标 | 结果 |
|---|---|
| 文件读取（with open / encoding / 逐行） | ✅ |
| 日志状态码统计项目 | ✅ 输出全部正确 |
| 接口统计（加分项） | ✅ parts[-2] 实现 |
| AI 自测 5 题 | ✅ 全对 |

## 二、核心知识点：文件读取

```python
# 推荐写法：with 自动关闭文件
with open("api_log.txt", "r", encoding="utf-8") as f:
    for line in f:            # 逐行读取，大日志不占内存
        line = line.strip()   # 去行尾换行符 \n
        parts = line.split()  # 按空格切分
        status = parts[-1]    # 最后一个元素 = 状态码
        url = parts[-2]       # 倒数第二个 = 接口路径

# 读取模式
"r" 读  /  "w" 写(覆盖)  /  "a" 追加

# Windows 读中文文件必须写 encoding="utf-8"，否则 UnicodeDecodeError
```

## 三、最终项目代码（day06_log_stat.py）

```python
result = {}
total = 0
with open("api_log.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        parts = line.split()              # ['2026-10-07','10:00:01','GET','/api/login','200']
        status = parts[-1]
        result[status] = result.get(status, 0) + 1

print(f"===== 状态码统计 =====")
for key, value in result.items():
    total += value
    print(f"{key}: {value}次")
pass_rate = (result.get("200", 0) / total) * 100
print("=====================")
print(f"总请求数：{total}")
print(f"200占比：{pass_rate:.1f}%")       # .1f 保留1位小数

# 加分项：接口统计
url_count = {}
with open("api_log.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        parts = line.split()
        url = parts[-2]
        url_count[url] = url_count.get(url, 0) + 1

print(f"===== 接口统计 =====")
for key, value in url_count.items():
    print(f"{key}: {value}次")
```

**验证输出**：200×10、201×1、404×2、500×2，总数 15，200 占比 66.7%。

## 四、今日最大教训：类型敏感（测试思维）

🐛 **Bug**：`line[-3:]` 取到的是**字符串** `"200"`，字典 key 是 `"200"`；但 `result.get(200, 0)` 查的是**整数** 200 → 查不到返回 0 → 占比输出 0.0% 错误。

```python
# ❌ 错误
pass_rate = (result.get(200, 0) / total) * 100    # 永远 0

# ✅ 正确：用字符串
pass_rate = (result.get("200", 0) / total) * 100
```

> **Python 里 `200 != "200"`**：类型不同，key 不同。字典取值必须用和写入时**相同类型**的 key。
> **测开第一课**："代码能跑"≠"结果正确"。写完要看输出合不合理（200 明明有 10 次，占比不可能是 0）。交叉验证：Ctrl+F 数日志里 200 的次数，和程序输出对账。

## 五、今日实用技巧

1. 状态码/路径提取用 `split()[-1]` / `split()[-2]`，比固定下标/切片更稳（日志格式变化也能跑）
2. 小数格式化：`f"{num:.1f}"` 保留 1 位小数，报告输出必备
3. 交叉验证：人工数 + 程序算，对账确认

## 六、自测批改：5 题全对

with 自动关闭 / strip 去换行 / encoding="utf-8" / split 取 parts[-1] / 打印 500 行代码——全部正确。

## 七、明日预告（Day7 · 本周复盘日）

**第一周复盘**：错题回顾（本周踩的 8 个坑）+ 本周知识思维导图 + 检查 Git 仓库完整性。周末我会用 AI 出"第一周综合测试卷"，检验你真正掌握的程度。

---

*笔记由 AI 根据当日学习内容整理，建议每周日回顾一遍。*
