# 练习1：过滤打印
# 读 api_error_log.txt，打印所有包含 "ERROR" 的行，带行号
# 输出格式：第3行: 2026-10-11 09:00:03 ERROR 支付接口 服务器内部错误 500
with open("api_error_log.txt","r",encoding="utf-8")as f:
    for num ,line in enumerate(f,1): #从1开始编号
        if "ERROR" in line:
            print(f"第{num}行，：{line.strip()}")

# 练习2：错误类型统计（字典计数）
# 统计日志里这些关键词出现次数：500 / 404 / timeout
# 输出格式：
# 500: 2次
# 404: 1次
# timeout: 2次
error_count={}
with open("api_error_log.txt","r",encoding="utf-8")as f:
    for line in f:
        line=line.strip()
        if "500" in line:
            error_count["500"]=error_count.get("500",0)+1
        elif "404" in line:
            error_count["404"]=error_count.get("404",0)+1
        elif "timeout" in line:
            error_count["timeout"]=error_count.get("timeout",0)+1
for key,value in error_count.items():
    print(f'{key}:{value}次')


# 练习3：综合分析报告（综合）
# 输出一份完整报告：
# ===== 日志分析报告 =====
# 总行数：10
# ERROR 行数：5
# 错误率：50.0%
# ===== 错误类型分布 =====
# 500: 2次 / 404: 1次 / timeout: 2次
# ===== ERROR 行清单 =====
# 第1行: ... / 第3行: ...（带行号列出所有 ERROR 行）
with open("api_error_log.txt", "r", encoding="utf-8") as f:
    error_count = {}
    error_list = []
    total = 0
    for num, line in enumerate(f, 1):
        total = num
        line = line.strip()
        if "ERROR" in line:
            error_list.append(f"第{num}行：{line}")
        # 关键词统计：每个关键词独立判断（口径：500/404/timeout 出现次数）
        for keyword in ["500", "404", "timeout"]:
            if keyword in line:
                error_count[keyword] = error_count.get(keyword, 0) + 1

error_rate = round(len(error_list) / total * 100, 1)
print("===== 日志分析报告 =====")
print(f"总行数：{total}")
print(f"ERROR 行数：{len(error_list)}")
print(f"错误率：{error_rate}%")
print("===== 错误类型分布 =====")
for key, value in error_count.items():
    print(f"{key}: {value}次")
print("===== ERROR 行清单 =====")
for item in error_list:
    print(item)

#"ERROR" in line 判断的是什么？区分大小写吗？
print("判断是的ERROR是否在这行，区分大小写")
#enumerate(f, 1) 的作用？第二个参数 1 是什么意思？
print("作用是读取文件f时，枚举行数和每行；第二个参数1表示从1开始计数")
#读日志时 line.strip() 为什么要做？
print("line.strip()可以去除每行的换行符和首尾空格")
#写代码：读文件打印所有含 "500" 的行。
with open("api_error_log.txt","r",encoding="utf-8")as f:
    for line in f:
        line=line.strip()
        if "500" in line:
            print(f"{line}")
#写代码：统计 "ERROR" 出现的次数（字典计数）。
with open("api_error_log.txt","r",encoding="utf-8")as f:
    error_count={}
    for line in f:
        line=line.strip()
        if "ERROR" in line:
            error_count["ERROR"]=error_count.get("ERROR",0)+1
print(error_count["ERROR"]) 