# ===== 定义函数 =====函数要先定义、后调用。参数 name 是 "占位符"，调用时传什么就是什么
def greet(name):            #def+函数名+(参数)+冒号
    print(f"你好，{name}")  #函数体（缩进！）

# ===== 调用函数 =====
greet("张三")# 输出：你好，张三
greet("李四")# 输出：你好，李四
# ===== 函数计算并返回结果 =====
def add(a,b):
    return a+b  # return：把结果"交出去"

result=add(3,5) # result 拿到 8
print(result)   # 8
# 没有 return 的函数，调用后得到 None
def no_return():
    print("我啥也不返回")

print(no_return())#None
#return 三件事：① 交回结果 ② 立即结束函数（后面代码不执行）③ 没有 return 默认返回 None。

# ===== 默认参数：调用时可省 =====
def login(username,password="123456"):
    if username=='admin' and password=='123456':
        return "登录成功"
    return "登录失败"

print(login('admin'))          #密码用默认值-登录成功
print(login('admin','888888')) #覆盖默认值，登录失败

#铁律：默认参数必须放在普通参数后面
#def func(a,b=10):     正确
#def func(a=10,b):     语法错误，默认参数不能再普通参数前面

# ===== 状态码判断函数（以后天天用） =====
def check_status(status_code):
    if status_code==200:
        return "通过"
    elif status_code==404:
        return "接口不存在"
    elif status_code==500:
        return "服务器错误"
    else:
        return "其他异常"

print(check_status(200))#通过
print(check_status(404))#接口不存在

# ===== 通过率计算函数 =====
def cal_pass_rate(passed,total):
    return round(passed/total*100,1) #round保留一位小数

print(cal_pass_rate(3,5))#60.0