# ===== 1. 打开文件读取（推荐写法：with） =====
with open("api_log.txt","r",encoding="utf-8") as f:
    content=f.read()#一次性读完整个文件（小文件用）
    print(content)
# ===== 2. 逐行读取（大日志推荐，不占内存） =====
with open("api_log.txt","r",encoding="utf-8") as f:
    for line in f:
        print(line.strip())
# ===== 3. 读取模式 =====
# "r" 读  / "w" 写（覆盖） / "a" 追加
# 写文件：with open("out.txt", "w", encoding="utf-8") as f: f.write("内容")

# ===== 4. 编码（Windows 最容易踩的坑） =====
# 不加 encoding="utf-8"，读含中文的文件可能报 UnicodeDecodeError