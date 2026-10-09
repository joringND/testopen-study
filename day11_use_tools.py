# ===== import 整个模块 =====
import math
print(math.sqrt(16))          # 4.0（用"模块.函数"的方式）

# ===== from 只拿需要的 =====
from math import sqrt, pi
print(sqrt(9))                # 3.0（直接用函数名）
print(pi)                     # 3.141592653589793

# ===== as 起别名（名字太长时） =====
import math as m
print(m.floor(3.7))           # 3

# ===== day11_use_tools.py：使用我的工具箱 =====
from my_tools import check_status,cal_pass_rate

print(check_status(200))#通过
print(check_status(500))#服务器错误
print(cal_pass_rate(3,5))#60.0

# ===== 新建 day11_pip_check.py =====
import requests
print(requests.__version__)

