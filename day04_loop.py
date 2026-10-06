# ===== 遍历列表：批量处理测试用例 =====
test_cases=["登录接口","下单接口","支付接口"]
for case in test_cases:
    print(f"正在执行{case}")
# 输出：正在执行：登录接口 / 下单接口 / 支付接口

# ===== 遍历字典 =====
case_info={"name":"登录","method":"POST","expect":200}
for key in case_info:
    print(key)
for key,value in case_info.items():
    print(f"{key}={value}")

for i in range(5):#0 1 2 3 4
    print(i)
for i in range(1,5):#1,2,3,4
    print(i)
for i in range(0,10,2):#0,2,4,6,8
    print(i)
#测开用法：循环N次批量造数据
for i in range(3):
    print(f"testuser{i}@example.com")#testuser0/1/2
# ===== while 基本：计数器 =====
count = 0
while count<3:
    print(f"第{count+1}次")
    count+=1 #必须改变条件，否则死循环

# ===== 测开场景：接口重试机制 =====
# 接口偶发超时/网络抖动，自动重试 3 次
attempt=1
while attempt<=3:
    print(f"第{attempt}次请求接口……")
    #模拟：第3次才成功
    if attempt==3:
        print("请求成功")
        break#成功就跳出循环，不再尝试
    attempt+=1

# break：立即停止整个循环    
for i in range(10):
    if i==5:
        break#遇到5直接结束循环
    print(i)#只打印0 1 2 3 4
# continue：跳过这一次，继续下一次
for i in range(10):
    if i%2==0:
        continue#偶数跳过
    print(i)#只打印奇数1 3 5 7 9

# 模拟批量执行测试用例，统计通过/失败数量
test_cases=["登录","下单","支付","退款"]
passed=0
failed=0

for case in test_cases:
    # 模拟执行结果：前3个通过，最后一个失败
    if case =="退款":
        print(f"{case}:失败")
        failed+=1
    else:
        print(f"{case}:通过")
        passed+=1
print(f"共{len(test_cases)}条用例，通过{passed}条，失败{failed}条")
# 这就是测试报告的雏形       