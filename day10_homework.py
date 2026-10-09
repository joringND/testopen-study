# 练习1：写函数 safe_divide(a, b)
# 除零时返回"除数不能为0"，否则返回结果（用 try-except 捕获 ZeroDivisionError）
# 调用：safe_divide(10, 2) 和 safe_divide(10, 0)，打印结果
def safe_divide(a, b):
    try:
        return a/b
    except ZeroDivisionError as e:
        return "除数不能为0"
print(safe_divide(10,2))
print(safe_divide(10,0))    

# 练习2：写函数 read_first_line(file_path)
# 文件不存在时返回"文件不存在"，存在时返回第一行内容（捕获 FileNotFoundError）
# 调用：read_first_line("api_log.txt") 和 read_first_line("no_file.txt")
def read_first_line(file_path):
    try:
        with open(file_path,"r",encoding="utf-8")as f:
            return f.readline()
    except FileNotFoundError as e:
        return '文件不存在'
print(read_first_line("api_log.txt"))
print(read_first_line("no_file.txt"))

# 练习3：写函数 parse_int(text)
# 能转成 int 就返回数字，否则返回"无法转换"（捕获 ValueError）
# 调用：parse_int("123") 和 parse_int("abc")，打印结果
def parse_int(text):
    try:
        return int(text)
    except ValueError as e:
        return "无法转换"
    
print(parse_int("123"))
print(parse_int("abc"))    

#try-except 的作用？程序报错不 try 会怎样？
print("try-except的作用是捕获异常，确保程序不中断执行。程序报错不try会导致程序中断")
#except KeyError as e 里的 KeyError 是什么？as e 有什么用？
print("KeyError是错误类型的名字（缺字典key），as e用来把错误信息存进变量 e，方便打印 / 记录。")
#else 和 finally 分别在什么时候执行？
print("else在无报错时执行，finally无论是否报错都执行")
#写 safe_divide(10, 0) 的除零保护函数。
def safe_divide(a,b):
    try:
        return a/b
    except ZeroDivisionError as e:
        return "除数不能为0"
print(safe_divide(10,0))
#写代码：打开不存在的文件，用 try-except 捕获 FileNotFoundError 并打印 "文件不存在"。
def read_first_line(file_path):
    try:
        with open(file_path,"r",encoding="utf-8")as f:
            return f.readline()
    except FileNotFoundError as e:
        return "文件不存在"
print(read_first_line("no_file.txt"))

# 练习4（补）：解析分数，覆盖 else / finally / raise
# 1. 写函数 parse_score(text)：
#    - 能转成 int 且 >= 0 → return 分数
#    - 不能转换 → raise ValueError("分数格式错误")
# 2. 调用方用 try-except-else-finally 处理：
#    try:    score = parse_score(text)
#    except ValueError as e:  print(f"出错：{e}")
#    else:   print(f"解析成功：{score}")
#    finally: print("本次解析结束")
# 3. 分别传 "85" 和 "abc" 验证两次输出
def parse_score(text):
    try:
        score= int(text)
    except ValueError as e:              # 转换失败 → 抛 ValueError（原始错误）
        raise ValueError("分数格式错误")  # 归一化：换成业务错误
    if score<0:                          # 负数单独判断
        raise ValueError("分数格式错误")
    return score
    
def run_parse(text):    
    try:
        score=parse_score(text)
    except ValueError as e:  
        print(f"出错：{e}")
    else:
        print(f"解析成功:{score}")
    finally:
        print("本次解析结束")

run_parse("85")
run_parse("abc")
    