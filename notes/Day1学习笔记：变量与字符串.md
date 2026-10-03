# Day1 学习笔记：环境搭建 + Python 变量与字符串

> 日期：2026-10-03（周六 · 节假日档 3.5h）
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第1月 · Day1
> 状态：✅ 全部完成

---

## 一、今日目标与完成情况

| 目标 | 结果 |
|---|---|
| 环境搭建（Python / VSCode / Git / GitHub） | ✅ 全部就绪 |
| 掌握变量与字符串 | ✅ |
| 练习 3 题 | ✅ 全对 |
| AI 自测 5 题 | ✅ 4 对 1 错（已纠正） |
| 首次 Git 提交 | ✅ push 成功 |

## 二、环境信息（记录备用）

| 工具 | 版本 / 配置 |
|---|---|
| Python | 3.9.13（Anaconda 发行版，装在 D:\anaconda3） |
| pip | 22.2.2 |
| VSCode | 插件：Python、Chinese Language Pack、GitLens |
| Git | 2.54.0，user.name=joringND，user.email=1213198051@qq.com |
| GitHub 仓库 | https://github.com/joringND/testopen-study （Public） |

---

## 三、知识点

### 1. 变量

- Python 变量**不需要声明类型**，直接赋值：`name = "张三"`
- 常见类型：字符串 `"abc"`、整数 `27`、浮点数 `12000.0`、布尔值 `True/False`

**命名三规则（面试常考）：**
1. 只能由**字母、数字、下划线**组成
2. **不能以数字开头**
3. 不能用**关键字**（`if`、`for`、`class`、`def` 等）

```python
# ✅ 合法
_name = 1
my_name = 2
name2 = 3

# ❌ 不合法
2name = 1        # 数字开头
my-name = 1      # 连字符 = 减号，语法错误
class = 1        # 关键字
```

> ⚠️ 踩坑记录：`my-name` 不合法！Python 会把 `-` 当成减号，解析成 `my - name`。

### 2. 字符串

三种写法：`'abc'`、`"abc"`、`'''多行'''`

**f-string（最推荐，Python 3.6+）：**

```python
name = "张三"
age = 27
print(f"我是{name}，今年{age}岁")   # 变量直接放 {} 里
```

**拼接（+ 号，数字要转 str）：**

```python
print("我是" + name + "，今年" + str(age) + "岁")
```

### 3. 切片（重点）

```python
s = "testopen-engineer"
s[起始:结束:步长]
# 关键：结束索引【不包含】
s[0:8]    # testopen（取索引 0~7）
s[9:]     # engineer（索引 9 到最后）
s[::-1]   # reenigne-nepotset（倒序）
len(s)    # 17（长度）
```

### 4. 字符串常用方法

```python
"  hello  ".strip()     # 去首尾空格 -> "hello"
"a,b,c".split(",")      # 按逗号分割 -> ['a', 'b', 'c']
"abc".upper()           # 转大写 -> "ABC"
"test" in "testopen"    # 判断包含 -> True
```

---

## 四、今日练习（批改记录）

### 练习 1：变量 + f-string ✅

```python
name = "张三"
age = 27
job = "手工测试"
print(f"我是{name}，今年{age}岁，岗位{job}")
```

### 练习 2：切片 ✅

```python
s = "testopen-engineer"
print(s[0:8])    # testopen
print(s[9:])     # engineer
print(s[::-1])   # reenigne-nepotset
```

### 练习 3：拼接 vs f-string ✅（两种写法都对，以后优先 f-string）

```python
name = "zhangsan"
print(name + "@testopen.com")     # 拼接
print(f"{name}@testopen.com")     # f-string（推荐）
```

### AI 自测 5 题批改：4/5

| 题 | 判定 | 说明 |
|---|---|---|
| 变量名合法性 | ❌ | `my-name` 不合法（连字符=减号）；`_name` 合法；`2name` 数字开头；`class` 关键字 |
| `s[1:4]` | ✅ | `ell` |
| f-string 输出价格 | ✅ | `f"价格：{price}元"` |
| `split(",")` | ✅ | `['a','b','c','d']` |
| 倒序 | ✅ | `s[::-1]` |

---

## 五、Git 命令速查（今天学的）

```bash
# 克隆仓库
git clone https://github.com/用户名/仓库名.git

# 查看配置
git config --global --list

# 配置身份
git config --global user.name "名字"
git config --global user.email "邮箱"

# 提交三连击（先 cd 进仓库目录！）
cd /d/learn/testopen-study
git add .
git commit -m "提交说明"
git push origin main
```

> ⚠️ 踩坑记录：
> 1. `fatal: not a git repository` = 没在仓库目录里执行，先 `cd` 进仓库
> 2. GitHub 连不上（443 超时）= 国内网络问题，配置代理：
>    `git config --global http.proxy http://127.0.0.1:7897`

---

## 六、明日预告（Day2）

**列表、元组、字典 + 条件判断 if**
- 列表 `[1,2,3]`、字典 `{"key": "value"}` 的增删改查
- `if / elif / else` 分支判断
- 练习：用 if 判断接口返回状态码、用字典管理测试数据

---

*笔记由 AI 根据当日学习内容整理，建议每周日回顾一遍。*
