#判断题（说理由）：
#1.def func(a, b=10, *args, **kwargs) 合法吗？顺序规则是什么？
print("合法，正确的顺序是普通参数-默认参数-位置参数-关键字参数")
# 2.函数没有 return，调用后返回什么？
print("没有return，调用后返回的是None")
# 3.def f(*args): 调用 f(1, 2, 3) 后，args 是什么？类型？
print("此时args是1,2,3;是元组类型;**kwargs：任意多个关键字参数 → 字典")
# 填空题：
# 4. try 里没异常时，else 和 finally 都会执行吗？
print("try无异常时候，else会执行\
      else 的名字就是 正常分支：没报错走 else，报错走 except，finally不论是否有异常都会执行")
# 5. import math 和 from math import sqrt 分别怎么调用？
print("import math时，调用math.sqrt();from math import sqrt直接调用sqrt()")
# 代码题（写完整代码，运行验证）：
# 6. 写 is_even(n)，偶数返回 True，奇数返回 False
def is_even(n):
    if n%2==0:
        return True
    else:
        return False
# 7. 写 safe_get(data, key)，KeyError 时返回 "缺字段"
def safe_get(data,key):
    try:
        return data[key]
    except KeyError as e:
        return "缺字段"
print(safe_get({"name": "张三"}, "name"))   # 张三（不是"name"）
print(safe_get({"name": "张三"}, "age"))    # 缺字段
# 8. 读 api_error_log.txt，打印所有含 "timeout" 的行（带行号）
with open("api_error_log.txt","r",encoding="utf-8")as f:
    for num,line in enumerate(f,1):
        line=line.strip()
        if "timeout" in line:
            print(f"第{num}行，{line}")

# 9. 用 requests 请求 https://www.baidu.com，打印状态码
import requests
resp=requests.get("https://www.baidu.com",timeout=5)
print(resp.status_code)
# 10. 写 count_words(text)："hello world hello python" 用字典统计每个单词出现次数
def count_words(text):
    word_count={}
    parts=text.split()
    for part in parts:
        word_count[part]=word_count.get(part,0)+1
    for key,value in word_count.items():
        print(f"{key}:{value}次")
count_words("hello world hello python")