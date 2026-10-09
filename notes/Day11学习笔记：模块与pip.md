# Day11 学习笔记：模块与 import、pip 装包

> 日期：2026-10-09
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第2周 · Day11
> 状态：✅ 全部完成（模块跑通、requests 装好、自测5题全对）

---

## 一、核心概念：模块化

**一个 .py 文件 = 一个模块 = 一个工具箱**
- 工具（函数）放在工具文件里，主程序 import 拿来用
- 代码从此可以拆分、复用、协作

## 二、知识点

### 1. import 三种写法

| 写法 | 调用方式 | 适用 |
|---|---|---|
| `import math` | `math.sqrt(16)` | 导入整个模块，不污染命名空间 |
| `from math import sqrt` | `sqrt(16)` | 只拿需要的名字，直接用 |
| `import math as m` | `m.sqrt(16)` | 名字太长起别名 |

### 2. 自己写模块（两步）

**my_tools.py（工具箱：只放函数定义）**

```python
def check_status(status_code):
    """状态码判断工具"""
    if status_code == 200:
        return "通过"
    elif status_code == 404:
        return "接口不存在"
    elif status_code == 500:
        return "服务器错误"
    else:
        return "其他异常"

def cal_pass_rate(passed, total):
    """通过率计算工具"""
    return round(passed / total * 100, 1)

if __name__ == "__main__":
    # 只有直接运行时才执行，被 import 时不执行
    print(check_status(200))
```

**day11_use_tools.py（使用方）**

```python
from my_tools import check_status, cal_pass_rate
print(check_status(200))     # 通过
print(cal_pass_rate(3, 5))   # 60.0
```

### 3. `__name__ == "__main__"` 保护

- 直接运行时：`__name__` = `"__main__"` → if 内代码执行
- 被 import 时：`__name__` = 文件名 → if 内代码不执行
- **作用**：工具模块的测试代码只在直接运行时跑，import 时不打扰

### 4. pip 装第三方包

```powershell
# PowerShell 写法（推荐与运行代码同一窗口）
& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" -m pip install requests

# cmd 写法（去掉 &）
"C:\Users\lenovo\AppData\Local\Programs\Python\Python39\python.exe" -m pip install requests

# 装包位置：Python 安装目录下的 Lib\site-packages
```

慢/失败加清华镜像：`-i https://pypi.tuna.tsinghua.edu.cn/simple`

## 三、实战成果：接口自动化最小闭环

```python
import requests
from my_tools import check_status

resp = requests.get("https://www.baidu.com", timeout=5)
print(resp.status_code)          # 200
print(check_status(resp.status_code))   # 通过
```

**request（发请求）→ response（拿结果）→ check_status（判结果）**——测开接口测试的最小骨架，第 6 月放大成框架。

## 四、Response 对象属性速查（提问补充）

`resp.status_code` 不是"参数"，是 **Response 对象自带的属性**：

| 属性 | 是什么 | 用途 |
|---|---|---|
| `resp.status_code` | HTTP 状态码 | 判断返回 |
| `resp.text` | 响应体文本 | 看内容 |
| `resp.json()` | 转成字典/列表 | **接口断言核心** |
| `resp.headers` | 响应头 | Content-Type 等 |
| `resp.ok` | 是否成功（<400） | 快速判断 |
| `resp.elapsed` | 请求耗时 | 性能测试 |

## 五、今日错误复盘（两个经典大坑）

### 🐛 坑1：改完没保存就跑 → ImportError

- 现象：`ImportError: cannot import name 'check_status' from 'my_tools'`
- 原因：**Python 运行的是磁盘上的文件，不是编辑器里看着的内容**。VSCode 标签页有白点 = 未保存
- 解决：Ctrl+S 保存 → 重跑
- 自查命令：`python -c "import my_tools; print(dir(my_tools))"` 列出模块所有名字

### 🐛 坑2：双 Python 环境装错包 → ModuleNotFoundError

- 现象：`ModuleNotFoundError: No module named 'requests'`，但明明 `pip install` 过
- 原因：电脑上有**两个 Python**：
  - Anaconda（`d:\anaconda3`）← 裸 `pip` 命令指向它
  - 官方版 Python39（`C:\Users\lenovo\...\Python39`）← 跑代码用的是它
  - 包装进了 Anaconda，代码在 Python39 跑 → 找不到
- 解决：**用运行代码的那个 python 装包**：`python39.exe -m pip install requests`
- 固定写法：装包永远用 `<跑代码的python.exe> -m pip install <包名>`

### 🐛 坑3：cmd 里用了 PowerShell 语法

- `& "路径"` 是 PowerShell 语法，cmd 里报"此时不应有 &"
- cmd 直接写路径；PowerShell 才需要 `&`

## 六、自测批改

| 题 | 判定 |
|---|---|
| import 两种写法区别 | ✅ |
| as 起别名 | ✅ |
| `__name__=="__main__"` 作用 | ✅ 满分 |
| pip 装包位置 | ✅（Lib\site-packages） |
| sqrt(25) | ✅ → 5.0 |

## 七、明日预告（Day12）

**本周综合练习**：把函数 + 可变参数 + 异常 + 模块 + requests 串起来——做一个"接口状态检测小工具"，检验第 2 周全部所学。

---

*笔记由 AI 根据当日学习内容整理。*
