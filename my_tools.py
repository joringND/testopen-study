# ===== my_tools.py：我的工具箱 =====
def check_status(status_code):
    """状态码判断工具"""
    if status_code == 200:
        return "通过"
    elif status_code == 404:
        return "接口不存在"
    elif status_code == 500:
        return "服务器错误"
    else:
        return "其他异常"

def cal_pass_rate(passed, total):
    """通过率计算工具"""
    return round(passed / total * 100, 1)

if __name__=="__main__":
    # 只有"直接运行本文件"时才执行这里
    # 被别的文件 import 时，这里的代码不会跑
    print(check_status(200))
    print(cal_pass_rate(3, 5))