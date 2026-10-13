# Day15 学习笔记：pytest 入门

> 日期：2026-10-13
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第3周 · Day15
> 状态：✅ 全部完成（pytest 8.4.2 装好、4 passed、练习+自测通过）

---

## 一、pytest 是什么

**自动化测试的"裁判系统"**：你只管写"用例 + 断言"，pytest 负责收集、执行、判定、出报告。企业自动化测试 90% 用它。

**工作流**：写用例（test_ 开头）→ pytest 自动收集 → assert 判定 → 输出报告（passed/failed）

## 二、核心知识点

### 1. 命名规则（pytest 自动收集的约定）

- 文件：`test_` 开头（如 `test_first.py`）
- 函数：`test_` 开头（如 `test_add`）

### 2. assert 断言 vs 以前的 if+print

```python
# ❌ 以前（人肉看输出）：
if resp.status_code == 200:
    print("通过")

# ✅ pytest（机器自动判定）：
def test_api():
    assert resp.status_code == 200   # 挂了自动标红

# 常见断言：
assert 1 + 1 == 2          # 相等
assert "abc" in "abcdef"   # 包含
assert result is True      # 是 True
assert len(data) > 0       # 非空
```

### 3. 异常断言 pytest.raises

```python
import pytest

def test_safe_divide_error():
    with pytest.raises(ZeroDivisionError):
        safe_divide(10, 0)   # 这行抛异常 → 用例通过
```

### 4. 运行命令

```powershell
cd D:\Desktop\my_python\learn\testopen-study        # 先进项目目录！
& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pytest test_first.py -v
```

| 参数 | 作用 |
|---|---|
| `-v` | 详细：每个用例一行 PASSED/FAILED |
| `-q` | 简洁：每个用例一个点 `.`，失败显示 `F` |

## 三、今日错误复盘（重点）

### 🐛 坑1：目录不对 → "file or directory not found"

- 现象：在 `C:\Users\lenovo` 跑 pytest，报 `file or directory not found: test_first.py`
- 原因：文件在项目目录，命令在用户目录执行
- 修法：**先 `cd D:\Desktop\my_python\learn\testopen-study` 再跑**（和 git 同理：命令要在文件所在目录执行）

### 🐛 坑2：假通过（最危险！）

```python
def test_safe_divide_ok():
    safe_divide(10, 2) == 5   # ❌ 没有 assert！结果被丢弃
```

- 没有 assert 的用例：**只要不抛异常就算 PASS** → 假通过（比真失败更危险，你以为测了其实没测）
- 修法：`assert safe_divide(10, 2) == 5`
- **pytest 铁律：每个测试用例里必须有 assert**
- 验证：故意把期望值改成错的，用例还过 = 假通过 = 有 bug

### ⚠️ 坑3：-q 的理解

- `-q` 不是"只显示失败用例"，是**简洁模式**（每个用例一个点，失败仍显示详情）

## 四、练习批改记录

| 项目 | 判定 |
|---|---|
| 练习1 基础断言×3 | ✅ |
| 练习2 check_status×3（import my_tools） | ✅ 工具箱正式进入 pytest |
| 练习3 safe_divide | ⚠️→✅（补 assert，消除假通过） |
| 自测 5 题 | ✅（-q 概念修正） |

## 五、明日预告（Day16）

**fixture 夹具 + 参数化**
- fixture：测试前的准备/清理（造数据、初始化客户端）
- `@pytest.mark.parametrize`：一组数据跑多次用例（接口测试必用）
- 把 Day12 的接口检测改成 pytest 参数化版本

---

*笔记由 AI 根据当日学习内容整理。*
