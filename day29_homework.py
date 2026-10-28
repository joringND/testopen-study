#生成day28_homework.py的报告
print('& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" \
      -m pytest day28_homework.py --html=report_day28_homework.html --self-contained-html')

#--self-contained-html的用途：样式全部内嵌进单个文件 ——
# 复制给同事/放CI里，对方打开就能看，不依赖你本机的样式文件

#-k 原理：按用例名做关键字匹配（支持 and/or/not），-k "get_user or echo" 是 " 名字含 get_user 或 echo 的都跑 "
# 只跑名字里含 get_user 的用例
print('& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" \
      -m pytest day28_homework.py -k "get_user" -v') 

# 跑除了 raises 以外的（排除）
print('& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" \
      -m pytest day28_homework.py -k "not raises" -v') 

# 第一个失败就停（回归止损）
print('& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" \
 -m pytest day28_homework.py --maxfail=1')

# 安静模式（只看结果不看过程）
print('& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" \
-m pytest day28_homework.py -q')

#报错显示--tb
#long    完整堆栈            深度排障
#short   只显示出错关键几行   日常常用
#no      不显示堆栈          只看谁挂了
print('& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" \
-m pytest day28_homework.py --tb=short')

#pytest.ini的addopt规则命令行参数会叠加在 addopts 后面
print("""
[pytest]
markers=
    smoke:冒烟测试
    full:全量测试
addopts = -v --tb=short
""")

# AI 自测 5 题（做完发我批改）
# 生成可分享的 HTML 报告，命令是什么？--self-contained-html 解决了什么问题？
print('命令：& "C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe"-m pytest \
      day28_homework.py --html=report_day28_homework.html --self-contained-html。\
      --self-contained-html实现了样式全部嵌入单个文件，方便复制给同事和放在CI里，不依赖本机样式')
# -k "not smoke" 会跑哪些用例？
print("会跑所有名字不含 smoke 的用例用例,与标记无关")
# --tb=no 和 --tb=short 的区别？
print('--tb=no只返回结果，不展示失败报错信息；--tb=short只展示关键的几行失败报错信息')
# --maxfail=1 什么场景用？
print("--maxfail=1在用例执行时需要遇错就停的时候用")
# 写代码：在 pytest.ini 里加 addopts = -q --tb=short（完整配置块）
print("""
[pytest]
markers=
    smoke:冒烟
    full:全量
addopts = -q --tb=short
""")
