# 练习1：写函数 show_case(case_name)
# 打印"正在执行用例：xxx"，然后依次调用 3 次（传不同用例名）
def show_case(case_name):
    print(f"正在执行用例：{case_name}")

show_case("test01")
show_case("test02")
show_case("test03")
# 练习2：写函数 check_status(status_code)
# 200→"通过"，404→"不存在"，500→"服务器错误"，其他→"其他异常"（return 返回）
# 调用 4 次验证
def check_status(status_code):
    if status_code==200:
        return "通过"
    elif status_code==404:
        return "不存在"
    elif status_code==500:
        return "服务器错误"
    else:
        return "其他异常"
print(check_status(200))
print(check_status(404))
print(check_status(500))
print(check_status(403))

# 练习3：写函数 get_avg(total, count, unit="条")
# 返回平均值（total / count，保留 2 位小数），unit 是默认参数用于打印格式
# 调用：get_avg(150, 5) 和 get_avg(150, 5, "个")
def get_avg(total,count,unit='条'):
    result= round(total/count,2)
    return f'{result}{unit}'
print(get_avg(150,5))
print(get_avg(150,5,'个'))

#函数定义用什么关键字？函数名后面必须跟什么符号？函数体靠什么表示归属？
print('函数定义用关键词def，函数名后必须跟冒号“:”,函数体靠缩进表示归属')
#return 的作用？函数没有 return，调用后返回什么？
print("return的作用是返回函数的结果方便后续调用，如果没有return，调用时返回None")
#默认参数必须放在什么位置？为什么不能反过来？
print("默认参数必须放在普通参数后，否则会出现语法错误")
#写函数 say_hi(name)，调用输出 "你好，name"。
def say_hi(name):
    return f"你好，{name}"
print(say_hi("张三"))
#写函数 get_sum(a, b) 返回两数之和，调用 get_sum(7, 8) 并打印结果。
def get_sum(a,b):
    return a+b
print(get_sum(7,8))