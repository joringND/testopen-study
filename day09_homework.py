# 练习1：写函数 sum_all(*nums) 返回所有数字之和
# 调用：sum_all(1, 2, 3) 和 sum_all(10, 20, 30, 40)，打印结果
def sum_all(*nums):
    total=0
    for num in nums:
        total+=num
    return total
print(sum_all(1,2,3))
print(sum_all(10,20,30,40))

# 练习2：写函数 build_case(**kwargs)
# 把传入的 key=value 打包成字典返回（模拟构造测试用例）
# 调用：build_case(name="登录", method="POST", expect=200)，打印返回值
def build_case(**kwargs):
    return kwargs
print(build_case(name="登录", method="POST", expect=200))
# 练习3：写函数 run_cases(env, *case_names)
# env 是环境名，case_names 是不定数量的用例名
# 逐个打印："在[dev]环境执行用例：登录接口"
# 调用两次：run_cases("dev", "登录", "下单") 和 run_cases("test", "登录", "下单", "支付", "退款")
def run_cases(env,*case_names):
    for name in case_names:
        print(f"在【{env}】环境执行用例：{name}")

run_cases("dev", "登录", "下单")
run_cases("test", "登录", "下单", "支付", "退款")

#*args 收到的是什么类型？**kwargs 呢？
print("*args收到的是元组类型，**kwargs收到的是字典类型")
#参数顺序铁律是什么（完整顺序）？
print("参数顺序铁律是def func(a,b=10,*args,**kwargs)，即普通参数，默认参数，位置参数，关键字参数")
#def func(**kwargs) 调用 func(a=1, b=2) 后，kwargs 是什么？
print('此时kwargs是{"a":1,"b":2}')
#写 sum_all(1, 2, 3, 4) 求和的函数（用 *args）。
def sum_all(*args):
    total=0
    for num in args:
        total+=num
    return total
print(sum_all(1,2,3,4))
#写 build_info(**kwargs)，遍历打印所有 key = value。
def build_info(**kwargs):
    for key ,value in kwargs.items():
        print(f'{key}={value}')