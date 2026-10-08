# ===== 基本：接收不定个数参数 =====*args：任意多个位置参数 → 元组
def print_all(*args):
    print(args)#('a','b','c')元组

print_all("a","b","c")#传3个
print_all("a")#传1个也可以

# ===== 测开场景：任意数量数字求和 =====
def get_sum(*nums):
    total=0
    for n in nums:
        total+=n
    return total

print(get_sum(1,2,3))#6
print(get_sum(1,2,3,4,5,6))#21

# ===== 基本 =====**kwargs：任意多个关键字参数 → 字典
def print_info(**kwargs):
    for key ,value in kwargs.items():
        print(f"{key}={value}")

print_info(name="zhangsan",age=27,job="手工测试")
#name=张三
#age=27
#job=手工测试

# 不同接口需要传不同的 params / headers / timeout，用 **kwargs 通吃
def send_request(url,method="GET",**kwargs):
    print(f"请求：{method}{url}")
    print(f"附加参数：{kwargs}")#有什么收什么

send_request(
    "/api/login",
    method="POST",
    params={"username":"admin","password":"123456"},
    headers={"Content-Type":"application/json"},
    timeout=10,
)
#输出：
#请求：POST /api/login
#附加参数{'params':{……},'headers':{……},'timeout':10}

#参数顺序铁律（面试高频）
def func(a,b=10,*args,**kwargs): #唯一正确顺序：位置参数 → 默认参数 → *args → **kwargs
    pass
