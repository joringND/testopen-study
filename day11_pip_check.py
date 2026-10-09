# ===== 新建 day11_pip_check.py =====
import requests
print(requests.__version__)
# requests 是 HTTP 库——第 6 月做接口自动化全靠它
# 快速试一下（可选）：
resp = requests.get("https://www.baidu.com",timeout=5)
print(resp.status_code)

#import math 和 from math import sqrt 有什么区别？各自怎么调用？
print("import math 是导入整个模块，用 math.sqrt() 调用；from math import sqrt 只导入一个名字，直接用 sqrt()")
#import math as m 的 as 是干什么的？
print("as用于将math简写成m，后续调用math的方法可以简写成m.func()")
#if __name__ == "__main__": 的作用是什么？为什么工具模块要加它？
print('作用是区别被直接运行文件以及被import调用的情况，\
      当被import调用时不会执行if __name__ == "__main__":下的内容')
#pip install requests 装的包放在哪里（目录）？
print("Lib下site-packages文件夹（Python 安装目录下）")
#写代码：import math 并打印 math.sqrt(25)。
import math
print(math.sqrt(25))