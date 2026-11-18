# 练习1：定义变量 name / age / job
# 用 f-string 打印："我是张三，今年27岁，岗位手工测试"
name = "张三"
age = 27
job = "手工测试"
print(f"我是{name}，今年{age}岁，岗位{job}")

# 练习2：s = "testopen-engineer"
# 分别取出 "testopen"、"engineer"、整个字符串倒序，各用一行 print 输出
s = "testopen-engineer"
print(s[0:8])
print(s[9:])
print(s[::-1])

# 练习3：name = "zhangsan"
# 生成并打印 "zhangsan@testopen.com"（提示：可以用 + 拼接，也可以用 f-string）
name = "zhangsan"
print(name+"@testopen.com")
print(f"{name}@testopen.com")

# 2name、my-name、_name、class 哪些合法？不合法原因？
print("_name合法，my-name,2name和class不合法。my-name不合法是因为变量名不能包含-号；2name不合法原因是数字不能做变量开头，\
      class不合法是因为class是已有的类型名")
# s = "hello"，s[1:4] = ？
print("ell")
# price = 99.5，用 f-string 输出 价格：99.5元 的写法？
price = 99.5
print(f"价格：{price}元")
# "a,b,c,d".split(",") = ？
print(['a','b','c','d'])
# "Python" 倒序切片写法？
s="python"
print(s[::-1])