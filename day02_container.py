#===== 列表：有序、可变 =====
test_cases=["登录接口","下单接口","支付接口"]

#增
test_cases.append("退款接口")#末尾追加
test_cases.insert(1,"注册接口")#插入到索引1

#删
test_cases.remove("登录接口")#按值删除
last= test_cases.pop()#弹出最后一个，并拿到它

#改
test_cases[0]="登录接口v2"

#查
print(test_cases[0])  #索引取值（从0开始）
print(len(test_cases))#长度
print("下单接口" in test_cases)#判断是否包含

# ===== 元组：有序、不可变 =====
#场景：接口允许的状态码集合、数据库的连接配置，定了就不能改
status_codes =(200,201,204)

print(status_codes[0]) #200
print(200 in status_codes)#True
print(len(status_codes))#3

# status_codes[0] = 404 #运行会报错TypeError

# ===== 字典：键值对 =====
#场景：一个测试用例的全部信息/接口请求头/JSON响应
case={
    "name":"登录接口-正确密码",
    "method":"POST",
    "url":"/api/login",
    "expect":200,
}
#查：两种取值方式
print(case["name"])#按key取值：key不存在会报错
print(case.get("timeout",30))#get取值，key不存在会返回默认值30（推荐，更安全）
print("name" in case)#判断key是否存在True

#增：直接赋值新key
case["headers"]={"Content_Type":"application/json"}
#改：给已有的key重新赋值
case["expect"]=201
#删
case.pop("headers")#删除指定key
#遍历
for key in case:
    print(key)
for key,value in case.items():
    print(key,value)