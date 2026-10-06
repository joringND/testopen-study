#比较运算符：==（等于）!=（不等于）>（大于）<（小于）>=（大于等于）<=（小于等于）
#逻辑运算符：and（且，都要满足）,or（或，满足一个）,not（取反）

print(200==200)#True
print(200!=404)#True
print(200>300)#False

# ===== 结构1：if 单分支 =====
status_code=200
if status_code==200:
    print("接口调用成功")

# ===== 结构2：if-else 二选一 =====
if status_code==200:
    print("接口调用成功")
else:
    print("接口调用失败")    
# ===== 结构3：if-elif-else 多分支（今天重点） =====
status_code=404
if status_code==200:
    print("接口调用成功")
elif status_code==404:
    print("接口不存在")
elif status_code==500:
    print("服务器错误")
else:
    print("其他异常")

if status_code==200:
    print("接口调用成功")# ← 必须缩进4个空格，表示"if 里面的代码"
print("这行不在if里")    # ← 不缩进，任何情况都执行

# 场景A：两个条件同时满足（and）
username="admin"
password="123456"
if username =="admin" and password =="123456":
    print("登录成功")
elif username !="admin":
    print("用户名不存在")
else:
    print("密码错误")

# 场景B：多个条件满足一个即可（or）——测试用例里很常见   
env="dev"
if env=="dev" or env=="test":
    print("这是测试环境，可以随意造数据") 
else:
    print("这是生产环境，小心操作")
        