# 练习1：列表
# 建一个列表，存 3 个工作里你测过的功能/接口名
s=['status-report','batch-query','jiekou']

# append 加一个，然后打印：列表长度、第一个元素、最后一个元素、"登录" 是否在列表中
s.append('登录')
print(len(s))#列表长度
print(s[0])#第一个元素
print(s[-1])#最后一个元素
print("登录" in s)#"登录" 是否在列表中

# 练习2：字典
# 建一个字典描述"登录接口"用例：name / method / url / expect
dict1={
    'name':"root",
    'method':"POST",
    'url':"/v1/agent/agent_id/status-report",
    'expect':"200",
}
# 依次完成：取值打印 → 新增一个 key（如 headers）→ 修改 expect → 删除一个 key
# → 用 for 循环遍历打印所有 key
print(dict1['name'])
dict1["header"]={"Content-Type":"Application/JSON"}
dict1["expect"]="ERROR"
dict1.pop("method")

for key in dict1:
    print(key)

# 练习3：元组
# 定义 status = (200, 201, 204)
status = (200,201,204)
# 打印 200 是否在元组里
print(200 in status)
# 尝试 status[0] = 404 运行，把报错信息原样记下来（理解"不可变"）
#status[0]=404

#列表和元组的本质区别？什么场景用元组？
print("本质区别在于列表可变，元组不可变。元组用于储存不可修改的场景，如接口的状态码")
#字典取值 d["key"] 和 d.get("key") 区别？哪个更安全、为什么？
print('区别在于d.get("key")会先判断key是否在字典中，不在的话会返回指定报错，因此更安全')
#遍历字典打印 key 和 value，写两种写法。
print("for key in case:" \
"print(key)")

print("for key,value in case.items()"\
      "print(key,value)")

#l = [1,2,3]，依次执行 l.append(4) 和 l.insert(0, 0) 后，l 是什么？
print([0,1,2,3,4])
#判断字典 case 里有没有 "timeout" 这个 key，怎么写？
print("timeout" in dict1)
print(dict1.get("timeout","NO"))