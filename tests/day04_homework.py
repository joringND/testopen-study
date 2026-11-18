# 练习1：for 遍历列表
# test_cases = ["登录接口", "下单接口", "支付接口", "退款接口"]
# 遍历打印，并输出序号，格式："第1条：登录接口"
i=0
test_cases = ["登录接口", "下单接口", "支付接口", "退款接口"]
for case in test_cases:    
    i+=1
    print(f"第{i}条：{case}")
# 优化：enumerate 同时拿序号和元素
for i, case in enumerate(test_cases, start=1):
    print(f"第{i}条：{case}")

# 练习2：统计状态码（重点，测试报告雏形）
# status_list = [200, 200, 404, 500, 200, 404]
# 用循环统计每个状态码出现的次数，输出格式：
# 200 出现 3 次 / 404 出现 2 次 / 500 出现 1 次
# （提示：建一个空字典 result = {}，遇到状态码就计数）
status_list = [200, 200, 404, 500, 200, 404]
result={}
for status in status_list:
    if status in result:
        result[status]+=1
    else:
        result[status]=1
print(result)     
#优化写法    
for status in status_list:
    result[status] = result.get(status, 0) + 1
print(result)
# 练习3：while 重试
# 模拟登录，最多尝试 3 次：
# 第 1、2 次输出"登录失败，重试中..."，第 3 次输出"登录成功"并 break 跳出
i=1
while i <=3:
    if i <3:
        i+=1
        print("登录失败，重试中……")
    else:
        print("登录成功")
        break

#for key in dict 遍历字典时，key 拿到的是什么？要同时拿键和值用什么方法？
print("key拿到是的dict字典的键，同时获取键和值可以这样写for key ,value in dict.items()")
#range(3)、range(1, 4)、range(0, 10, 3) 分别输出哪些数字？
print("分别输出0 1 2;1 2 3;0 3 6 9")
#break 和 continue 的区别？
print("break是跳出当前这层循环，对本层循环不再执行；\
      continue是跳过本次循环，如果后续满足条件，会继续执行本层循环")
#while 循环里忘记写 count += 1 会发生什么？为什么？
print("会导致无法跳出循环，因为while是只要符合条件就会持续执行，必须存在能够结束循环的条件")
#写代码：l = [10, 20, 30]，用 for 循环计算总和并打印。
l = [10, 20, 30]
total=0
for num in l:
    total+=num
print(f"{sum}")