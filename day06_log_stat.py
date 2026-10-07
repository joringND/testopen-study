"""
读取 api_log.txt
逐行处理，用 split() 提取每行的状态码（最后一个元素）
用字典统计每个状态码出现次数（Day4 的 get 计数）
加分：统计每个接口（如 /api/login）的请求次数。
输出报告：
===== 状态码统计 =====
200: 10 次
201: 1 次
404: 2 次
500: 2 次
=====================
总请求数：15
200 占比：66.7%
"""
result={}
total=0
with open("api_log.txt","r",encoding="utf-8") as f:
    for line in f:
        line=line.strip()
        parts=line.split()# ['2026-10-07', '10:00:01', 'GET', '/api/login', '200']
        status=parts[-1]
        result[status]=result.get(status,0)+1
print(f"===== 状态码统计 =====")
for key,value in result.items():
    total+=value
    print(f"{key}: {value}次")
pass_rate=(result.get("200",0)/total)*100
print("=====================")
print(f"""总请求数：{total}
200占比：{pass_rate:.1f}%
""")
#统计每个接口的数量
url_count={}
with open("api_log.txt","r",encoding="utf-8")as f:
    for line in f:
        line=line.strip()
        parts=line.split()
        url=parts[-2]
        url_count[url]=url_count.get(url,0)+1
print(f"===== 接口统计 =====")     
for key,value in url_count.items():
    print(f"{key}: {value}次")  
# with open 的好处？
print("with open的好处是用完文件后会自动关闭，无需手动close")
# for line in f 的 line 末尾带什么？怎么去？
print('line的末尾带换行符，使用line=line.strip()去除')
# UnicodeDecodeError 怎么解决？
print('在 with open()中指定encoding="utf-8"')
# 那行日志 split() 的结果？取状态码用哪个下标？
print('split()的结果是["2026-10-07", "10:00:01", "GET", "/api/login", "200"]\
      取状态码使用part=line.split(),part[-1]')
# 读文件打印所有含 500 的行
with open("api_log.txt","r",encoding="utf-8")as f:
    for line in f:
        line=line.strip()
        parts=line.split()
        if parts[-1]=="500":
            print(line)

    
     




