# ===== 没有 try：程序直接崩 =====
#print(10/0) #ZeroDivisionError，脚本中断

# ===== 有 try：接住异常，程序继续 =====
try:
    result=10/0
    print(result)               #这行不会执行
except ZeroDivisionError as e:
    print(f"出错啦：{e}")        #出错啦：devision by zero

print("程序继续跑")              #关键：不崩溃
#except ZeroDivisionError = 只接这一种异常；as e = 把错误信息存进变量 e，方便打印 / 记录

# ===== 字典缺字段 → KeyError =====
def get_status(case):
    try:
        return case["status"]
    except KeyError as e:
        return f"缺少字段{e}"

print(get_status({"status":200}))  #200
print(get_status({"name":"登录"})) #缺少字段'status'

# ===== 文件不存在 → FileNotFoundError =====
def read_log(file_path):
    try:
        with open(file_path,"r",encoding="utf-8")as f:
            return f.readline()
    except FileNotFoundError:
        return "文件不存在"

print(read_log("api_log.txt")) #第一行内容
print(read_log("no_such.txt")) #文件不存在

#常见异常速查：KeyError 缺字典 key、FileNotFoundError 文件找不到
# ValueError 值不对、ZeroDivisionError 除零、TypeError 类型不对

#else+finally
try:
    num= int("123")
except ValueError as e:
    print("不是数字")
else:
    print("转换成功")      #没异常才执行
finally:
    print("收尾，必定执行") #有没有异常都执行
    
#raise ValueError(...) = 主动抛异常。测开里 "数据有问题" 就 raise，让 except 统一处理。
test_cases = [
    {"name": "登录", "data": "admin"},
    {"name": "下单", "data": None},      # 这条数据有问题
    {"name": "支付", "data": "100元"},
]

for case in test_cases:
    try:
        if case["data"] is None:
            raise ValueError(f"{case['name']}数据为空") #主动抛出异常
        print(f"{case['name']}:执行通过")
    except ValueError as e:
        print(f"{case['name']}执行失败-{e}")
# 输出：
# 登录: 执行通过
# 下单: 执行失败 - 下单 数据为空      ← 记录失败，不中断
# 支付: 执行通过                      ← 后面的照常执行        