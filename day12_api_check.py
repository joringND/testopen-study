urls = [
    "https://www.baidu.com",                  # 200 → 通过
    "https://www.bing.com",                   # 200 → 通过
    "https://httpbin.org/status/404",         # 404 → 接口不存在
    "https://httpbin.org/status/500",         # 500 → 服务器错误
    "https://nonexistent-domain-abc123.com",  # 请求失败 → 异常分支
]
# ===== day12_api_check.py =====
import requests
from my_tools import check_status 
# 写函数 check_one(url)：
# - requests.get(url, timeout=5)
# - 用 check_status(resp.status_code) 判断
# - 打印：接口名 + 状态码 + 结果
# - 容错：请求失败时打印"请求失败：xxx"，程序不崩（try-except 包
def check_one(url):
    try:
        resp= requests.get(url,timeout=5)
        res=check_status(resp.status_code)
        return f"{url} {resp.status_code} {res}"
    except Exception as e:
        return f"请求失败：{e}"
#print(check_one("https://httpbin.org/status/404"))

# 改造 check_one → check_api(url, **kwargs)
# **kwargs 直接传给 requests.get：
#   requests.get(url, **kwargs)
# 这样能支持 timeout=5、params=...、headers=... 等任何 requests 参数
# 验证：check_api("https://www.baidu.com", timeout=3)
def check_api(url,**kwargs):
    try:
        resp=requests.get(url,**kwargs)
        return {"url": url, "status": resp.status_code,
                "result": check_status(resp.status_code)}
    except Exception as e:
        return {"url": url, "status": "ERR", "result": f"请求失败：{e}"}
#print(check_one("https://www.baidu.com",timeout=3))

# 写函数 check_all_apis(*urls):
# - 遍历每个 URL，逐个调用 check_api（各自 try-except，互不影响）
# - 统计：通过数、失败数、通过率（沿用 Day5 报告格式）
# - 收集失败接口名，报告末尾打印失败清单
# - 输出示例：
#   ===== 接口检测报告 =====
#   https://www.baidu.com: 通过
#   https://httpbin.org/status/404: 接口不存在
#   ...
#   共检测 5 个接口
#   通过 2 个，失败 3 个
#   通过率 40.0%
#   失败接口：[...]  
def check_all_apis(*urls):
    report = {"通过": 0, "失败": 0, "失败接口": []}
    print("===== 接口检测报告 =====")
    for url in urls:
        res = check_api(url)              # 字典，不用 split
        print(f"{url}: {res['result']}")
        if res["result"] == "通过":
            report["通过"] += 1
        else:
            report["失败"] += 1
            report["失败接口"].append(url)
    return report                          # 报告是函数"交出来的成品"

report = check_all_apis(*urls)             # 用全局列表展开，一处维护
pass_rate=round(report["通过"]/len(urls)*100,1)
print(f"共检测{len(urls)}个接口\n通过{report['通过']}个，失败{report['失败']}个\n通过率{pass_rate}%\n失败接口:\
      {report['失败接口']}")

#为什么每个接口都要单独 try-except？（如果整个循环包一个 try 会怎样？）
print("正确（我们的写法）：try 在循环【里面】→ 每个接口隔离，错误：try 在循环【外面】→ 第一个异常直接跳出整个循环")
#check_api(url, **kwargs) 里 **kwargs 传给了谁？和 Day9 的 build_case 思路有什么相同？
print('**kwargs 传给了 requests.get()—— 准确说是原样打包转发（透传）;\
      和 Day9 build_case 的相同点：都用 **kwargs 做 "通用接收"—— 一个装参数，一个转发参数，思路同源。')
#这次报告统计用到的 result.get() 和 Day6 日志统计有什么相同？类型注意什么？  
print("统计相同点在于使用字典存储统计的信息，\
      注意元组不可变，无法累计—— 计数必须用可变容器（字典 / 列表），这正说明字典是计数的正解")     
            
        


    