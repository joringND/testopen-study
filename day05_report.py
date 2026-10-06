#组织测试数据（定义列表，每条用例是字典）
test_cases = [
    {"name": "登录接口", "status": 200},
    {"name": "下单接口", "status": 200},
    {"name": "支付接口", "status": 500},
    {"name": "退款接口", "status": 404},
    {"name": "查询接口", "status": 200},
]
#2. 遍历 + 判断 + 统计：for 循环遍历，status == 200 判为通过，否则失败；统计通过数、失败数。
pass_count=0
failed_cases = []                    # 收集失败用例名
print("===== 测试报告 =====")
for case in test_cases:
    case_name=case.get("name",None)
    result="失败"
    if case["status"]==200:
        result="通过"
        pass_count+=1
    else:
        failed_cases.append(case["name"])
    print(f"{case_name}:{result}")
print("====================")
fail_count=len(test_cases)-pass_count
pass_rate=(pass_count/len(test_cases))*100
print(f"共执行{len(test_cases)}条用例")
print(f"通过{pass_count}条，失败{fail_count}条")
print(f"通过率{pass_rate}%")
# 报告最后：
print(f"失败用例：{failed_cases}")
'''
===== 测试报告 =====
登录接口：通过 ✅
下单接口：通过 ✅
支付接口：失败 ❌
退款接口：失败 ❌
查询接口：通过 ✅
====================
共执行 5 条用例
通过 3 条，失败 2 条
通过率：60.0%
'''
#"hello world".split(" ") 结果？"hello"[-1] 是？
print('"hello world".split(" ") 结果：["hello", "world"]  ← 一个列表！;"hello"[-1]是"o"')
#d = {"a": 1}，d.get("b", 0) 返回？d["b"] 会怎样？
print('d.get("b", 0)返回0;d["b"]会直接报错，程序中断')
#x = 5，x > 3 and x < 10 结果是？
print("结果是True")
#for i in range(3, 7) 输出哪些数？
print('输出3 4 5 6')
#l = [1, 2, 3]，append(4) 再 pop() 后 l 是什么？
print('l是[1,2,3]')
#元组能修改吗？报什么错？
print('元组不能修改，报TypeError')
#"abc".upper() 结果？
print('"abc".upper()结果是"ABC"')
#break 和 continue 区别（一句话）？
print("break跳出当前所在循环，continue跳过本次所在循环")
#写代码：n = 7 判断奇偶输出。
n=7
if n%2==0:
    print("偶数")
else:
    print("奇数")
#写代码：遍历 d = {"a": 1, "b": 2} 打印 key 和 value。
d = {"a": 1, "b": 2} 
for key ,value in d.items():
    print(f"{key}:{value}")