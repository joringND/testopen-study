# 练习1：成绩判断
# score = 85
# >=90 输出"优秀"，>=80 输出"良好"，>=60 输出"及格"，否则输出"不及格"
score= 85
if score>=90:
    print("优秀")
elif score>=80:
    print("良好")
elif score>=60:
    print("及格")
else:
    print("不及格")


# 练习2：接口状态码判断
# status_code = 403
# 200→"通过"  401→"未认证"  403→"无权限"  404→"不存在"  500→"服务器错误"  其他→"未知"
# 用 if-elif-else 实现
status_code=403
if status_code==200:
    print("通过")
elif status_code==401:
    print("未认证")
elif status_code==403:
    print("无权限")
elif status_code==404:
    print("不存在")
elif status_code==500:
    print("服务器错误")
else:
    print("未知")

# 练习3：登录判断（用 and / or）
# 用户名 admin、密码 123456 都正确 → "登录成功"
# 用户名对、密码错 → "密码错误"
# 用户名错 → "用户名不存在"
username="admin"
password="123456"
if username=="admin" and password=="123456":
    print("登录成功")
elif username=="admin" and password!="123456":
    print("密码错误")
elif username!="admin":
    print("用户名不存在")
# 优化版：elif 和 else 自动排除前面的情况
if username == "admin" and password == "123456":
    print("登录成功")
elif username == "admin":        # 走到这说明密码已经不对了
    print("密码错误")
else:                            # 走到这说明用户名不对
    print("用户名不存在")

#if 条件后面必须加什么符号？if 下面的代码块靠什么表示归属？
print("if条件后面必须加冒号':',if下面的代码块靠缩进表示归属")
#== 和 = 的区别？
print("==是判断左右两边是否相等或为同一值，=表示将右边的值赋值给左边的变量")
#and 和 or 的区别？举一个生活例子。
print("and表示条件全部满足，or表示只需满足任一条件。比如坐火车，买票和带身份证必须同时满足才能上车，类似条件and\
      进入公司园区时带工卡和刷脸过闸只需满足一个条件即可入园，使用条件or")
#score = 72，用 if-elif-else 判断档次（>=60 及格，>=85 良好，>=90 优秀，否则不及格），并说明判断顺序为什么重要。
score=72
if score>=90:
    print("优秀")
elif score>=85:
    print("良好")
elif score>=60:
    print("及格")
else:
    print("不及格")
print('顺序重要的真正原因是：if-elif 从上往下找 "第一个成立" 的条件，命中就停。\
      如果宽条件写在前面，后面的分支就永远执行不到')
#如果 if 和 elif 都不满足、又没有 else，程序会怎样？
print("如果 if 和 elif 都不满足、又没有 else，程序会继续执行if-elif代码块以外接下来的代码")