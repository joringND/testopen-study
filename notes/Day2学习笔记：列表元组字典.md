# Day2 学习笔记：列表、元组、字典

> 日期：2026-10-03（节假日档）
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第1月 · Day2
> 状态：✅ 全部完成（代码已提交 GitHub，第 4 次提交）

---

## 一、今日目标与完成情况

| 目标 | 结果 |
|---|---|
| 掌握列表 list / 元组 tuple / 字典 dict | ✅ |
| 示例代码运行 | ✅ 全部跑通 |
| 练习 3 题 | ✅ 逻辑全对（修正 1 个命名问题） |
| AI 自测 5 题 | ✅ 4 对 1 错（get 与 [] 说反，已纠正） |
| VSCode 图形化提交 | ✅ 学会（以后不用敲命令行） |

## 二、三种数据结构速查表

| 对比项 | 列表 list | 元组 tuple | 字典 dict |
|---|---|---|---|
| 写法 | `[1, 2, 3]` | `(1, 2, 3)` | `{"k": "v"}` |
| 有序 | ✅ 按索引 | ✅ 按索引 | ✅ 3.7+ 按插入顺序 |
| 可变 | ✅ | ❌ | ✅ |
| 取值 | `l[0]` | `t[0]` | `d["key"]` |
| 添加 | `append/insert` | 不支持 | `d["新key"] = 值` |
| 删除 | `remove/pop` | 不支持 | `pop("key")` |
| 修改 | `l[0] = x` | 不支持 | `d["key"] = x` |
| 测开场景 | 一组用例名/数据 | 固定状态码 | 一个用例的全部字段 |

> 口诀：**列表装一组、元组装固定、字典装一个对象的多个属性**。接口返回的 JSON 天然就是嵌套的字典+列表。

## 三、核心操作示例

```python
# 列表
test_cases = ["登录接口", "下单接口"]
test_cases.append("支付接口")        # 末尾追加
test_cases.insert(1, "注册接口")     # 指定位置插入
test_cases[0] = "登录v2"             # 修改
test_cases.remove("登录v2")          # 按值删除
last = test_cases.pop()              # 弹出末尾
len(test_cases)                      # 长度
"登录" in test_cases                 # 包含判断

# 元组（不可变）
status_codes = (200, 201, 204)
status_codes[0] = 404                # ❌ TypeError: 'tuple' object does not support item assignment

# 字典
case = {"name": "root", "method": "POST", "url": "/api/login", "expect": 200}
case["name"]                # 取值（key 不存在报 KeyError）
case.get("name")            # 取值（key 不存在返回 None，推荐）
case.get("timeout", 30)     # 带默认值
"name" in case              # 判断 key 存在
case["headers"] = {...}     # 新增
case["expect"] = 201        # 修改
case.pop("method")          # 删除
for key in case: ...        # 遍历 key
for key, value in case.items(): ...   # 遍历键值对
```

## 四、今日踩坑记录（重点复习）

1. **❌ 变量名用了 `dict`**：`dict` 是内置类型名，会遮蔽 Python 内置功能。**规矩：不用内置类型名（dict/list/str/int）做变量名**，用业务含义命名（如 `case`）。
2. **❌ 字符串引号嵌套**：`print("d.get("key")")` 外层内层都是双引号 → 语法错误。**外层单引号、内层双引号**（或反过来），或使用转义 `\"`、三引号。
3. **❌ 混淆 `[]` 和 `get()`**：
   - `d["key"]`：key 不存在 → **抛 KeyError 异常，程序中断**
   - `d.get("key")`：key 不存在 → **返回 None/默认值，程序继续**，更安全
   - 测开习惯：解析接口响应时，不确定的字段一律用 `get()`

## 五、额外收获：VSCode 图形化提交（替代命令行）

流程：`Ctrl+Shift+G` 打开源代码管理 → 看更改列表（U=新文件/M=已修改）→ 点 **+** 暂存（= git add）→ 顶部写提交信息（= git commit -m）→ 点 ✓ 提交 → 推送（... → 推送，或直接用"提交并推送"）。

**原理**：VSCode 不是每次选择推送目标——
- 仓库地址写在 `.git/config`（`remote origin`），clone 时自动绑定（`git remote -v` 查看）
- 推送分支 = 当前分支（底部状态栏右侧显示，如 `main*`；`git branch` 查看）

## 六、明日预告（Day3）

**if / elif / else 条件判断**：用代码做决策。练习：用 if 判断接口返回状态码、模拟登录结果判断。

---

*笔记由 AI 根据当日学习内容整理，建议每周日回顾一遍。*
