# Day10 学习笔记：异常捕获 try-except

> 日期：2026-10-09
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第2周 · Day10
> 状态：✅ 全部完成（练习1~3 一次通过、练习4 bug 修正、自测5题全对）

---

## 一、核心：try-except 执行流程

```
try：尝试执行代码
  ├─ ✅ 没报错 → 跳过 except → 执行 else（可选）→ finally
  └─ ❌ 报错了 → 跳进 except 处理（程序不崩溃）→ finally
finally：无论怎样都执行（清理收尾）
```

**测开价值**：100 条用例 1 条报错 → 不 try 整个脚本崩，后面 99 条全跑不了；try 住它 → 记录失败 → 继续跑。

## 二、知识点

### 1. 基本结构

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"出错啦：{e}")      # as e：错误信息存进变量
print("程序继续跑")             # 不崩溃
```

### 2. 常见异常速查表

| 异常 | 触发场景 |
|---|---|
| `KeyError` | 字典缺 key |
| `FileNotFoundError` | 文件找不到 |
| `ValueError` | 值不对（如 int("abc")） |
| `ZeroDivisionError` | 除零 |
| `TypeError` | 类型不对 |

### 3. else + finally

```python
try:
    num = int("123")
except ValueError:
    print("不是数字")
else:
    print("转换成功")       # 没异常才执行
finally:
    print("必定执行")       # 有没有异常都执行
```

### 4. raise 主动抛异常

```python
if case["data"] is None:
    raise ValueError("数据为空")   # 主动抛，让 except 统一处理
```

### 5. 多个 except（提问补充）

```python
try:
    ...
except KeyError as e:        # 具体错误放前面
    ...
except ValueError as e:      # 每个块都可以用 e，互不冲突
    ...
except Exception as e:       # 万能兜底放最后
    ...
```

- `as e` 是"局部昵称"，只在当前 except 块内有效，**重复用 e 是惯例，不用 e1/e2/e3**
- 从上到下匹配，命中第一个就停 → **先具体、后通用**（同 if-elif 先严格后宽松）

### 6. 异常归一化（练习4 学到的进阶技巧）

把底层异常翻译成业务错误，不让英文报错裸奔：

```python
def parse_score(text):
    try:
        score = int(text)
    except ValueError:
        raise ValueError("分数格式错误")   # 归一化
    if score < 0:
        raise ValueError("分数格式错误")
    return score
```

接口自动化里把 HTTP 错误转成业务错误，就是这套思路。

## 三、练习批改记录

| 项目 | 判定 | 备注 |
|---|---|---|
| 练习1 safe_divide | ✅ | 一次通过 |
| 练习2 read_first_line | ✅ | with open + FileNotFoundError |
| 练习3 parse_int | ✅ | ValueError 捕获 |
| 练习4 parse_score（补：else/finally/raise） | ⚠️→✅ | 2 个 bug 修正后通过 |
| 自测 5 题 | ✅ | 全对 |

**亮点**：练习1~3 全部用 return、异常类型全部指定、as e 习惯养成。

## 四、今日错误复盘（重点）

### Bug 1：`if int(text) and int(text)>=0` —— "0"被误判非法

**原因**：0 在 Python 里是 **falsy（假值）**，`and` 左边为 0 时短路 → 整个条件为 False → 走 else raise。

**教训**：不要用 truthy/falsy 玩判断花活，**转换和判断分开写**：
```python
score = int(text)     # 只做转换（放 try 里）
if score < 0:         # 单独判断
    raise ValueError(...)
```

### Bug 2：错误信息"裸奔"

**原因**：`int("abc")` 在 if 条件里自己就抛了原始异常，没走到自己 raise 的那行 → 输出英文底层报错，不是"分数格式错误"。

**教训**：底层异常用 except 接住 → 归一化成业务错误再 raise。

### 小建议：函数命名

处理函数别叫 `result`（和"结果变量"混淆），用动词命名：`run_parse` / `handle_score`。

## 五、提问答疑记录

**Q1：else/finally/raise 没出编程题？**
→ 是盲区，已补练习4 综合题覆盖。

**Q2：try 用 return、except 用 print，怎么调用？返回什么？**
→ except 分支只有 print 没有 return → 函数隐式返回 **None**。
→ **设计原则：函数要么全部 return 交结果，要么纯粹 print 演示，别混**——混了调用方拿到的结果不可控。

**Q3：Airtest 抛异常后不往下执行？**
→ 没记错，Airtest 默认 **fail-fast（报错即停）**。
→ 解法：每条用例包 try-except，失败记录后继续跑：
```python
for img in cases:
    try:
        assert_exists(img, msg=f"检查{img}")
    except AssertionError as e:
        print(f"{img}: 失败 - 继续执行")
    # finally: 截图、清状态、回首页
```

**Q4：多个 except 的 e 怎么存？**（见知识点5）

## 六、明日预告（Day11）

**模块与 import、pip 装包**：把代码拆成多个文件互相引用
- `import` / `from ... import ...`
- `pip install` 第三方库
- 测开场景：`pip install requests` 装 HTTP 库（接口自动化第一步）

---

*笔记由 AI 根据当日学习内容整理。*
