#判断题（说理由）：
#1.l = [1,2,3]，执行 l.append(4) 和 l.insert(0, 0) 后，l 是什么？
print('l是[0,1,2,3,4]')
#2.t = (1,2,3)，t[0] = 9 会报什么错？
print('会报错TypeError，元组是不可修改的')
#填空题：
#3. "hello world".split(" ") 的结果是______
print('结果是["hello","world"]')
#4. 字典 d = {"a": 1}，d.get("b", 0) 返回______，d["b"] 会______
print('d.get("b",0)返回0，d["b"]会报错，程序中断')
#5. for i in range(2, 5) 会输出______
print("会输出2 3 4")
#代码题（写完整代码，运行验证）：
#6. 用 f-string 输出：姓名：张三，年龄：27，岗位：手工测试
name="张三"
age=27
job="手工测试"
print(f'姓名：{name}，年龄：{age}，岗位：{job}')
#7. 写一个 if-elif-else：score = 78，>=85 优秀、>=60 及格、否则不及格，输出结果
score=78
if score >=85:
    print("优秀")
elif score>=60:
    print("及格")
else:
    print("不及格")
#8. 用 while 循环打印 1~5（计数器从 1 开始）
count=1
while count<=5:
    print(f"{count}")
    count+=1
#9. 统计列表 codes = [200, 404, 200, 500, 200] 里每个元素出现次数（字典计数）
codes = [200, 404, 200, 500, 200]
result={}
for num in codes:
    result[num]=result.get(num,0)+1
print(result)
#10. 读 api_log.txt，统计共有多少行（只需输出总行数）
count=0
with open("api_log.txt","r",encoding="utf-8") as f:
    for line in f:
        line=line.strip()
        count+=1
print(f"{count}")