#Day1:变量与字符串 示例代码
#1.变量：直接赋值 不用声明类型
name = "张三"
age = 27
salary = 12000.0
is_tester = True

#2.f-string格式化输出（最常用，记住）
print(f"我是{name}，今年{age}岁，岗位手工测试，月薪{salary}")
#3.字符串拼接（+号，数字要转成str）
print("我是"+name+",今年"+str(age)+"岁")

#切片 s[起始:结束:步长]，结束索引不包含
s = "testopen-engineer"
print(s[0:8])#testopen
print(s[9:])#engineer
print(s[::-1])#reenigne-nepotset(整个倒序)
print(len(s))#17

#5.字符串的常用方法
print("   hello   ".strip())#去掉首尾空格，hello
print("a,b,c".split(","))#按逗号分隔['a','b','c']
print(s.upper)#转大写
print("test" in s)#判断是否包含 True
