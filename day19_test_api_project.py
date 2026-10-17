# 需求：
# 1. fixture 提供接口清单（5 个接口：路径 + 期望状态码）
#    清单：
#    - /status/200 → 期望 200
#    - /status/201 → 期望 201
#    - /status/404 → 期望 404
#    - /status/500 → 期望 500
#    - /status/404 → 期望 200  ← 故意失败（模拟"期望和实际不符"的 bug）

# 2. 参数化批量执行：1 个用例定义跑 5 组数据

# 3. 每条用例：
#    - requests.get(base_url + path, timeout=5)
#    - check_status(resp.status_code)（复用 my_tools）
#    - assert resp.status_code == expect

# 4. 生成报告：--html=report.html --self-contained-html

# 5. 汇总打印（可以用一个普通脚本函数或 pytest 之外的统计）：
#    共检测 5 个接口、通过 4 个、失败 1 个、通过率 80.0%
#    （通过率用 my_tools.cal_pass_rate）

# 接口清单 = fixture 交 list（Day18 笔记补充过：交 list 就遍历）
# 5 组数据批量 = @pytest.mark.parametrize（Day16）
# 环境地址 = conftest 的 base_url（Day18）
# 状态码转文字 = check_status（Day12）
# 通过率 = cal_pass_rate（Day5/12）
# 报告失败排查 = pytest -s（Day16）
import pytest
import requests
from my_tools import check_status,cal_pass_rate

pass_count={}
@pytest.mark.parametrize("path,expect",[
    ("/status/200",200),
    ("/status/201",201),
    ("/status/404",404),
    ("/status/500",500),
    ("/status/404",200), #故意失败（模拟"期望和实际不符"的 bug）
])
def test_check_status(base_url,path,expect):
    resp=requests.get(base_url+path,timeout=5)
    print(f"{path} → {resp.status_code}")        # 想看输出加 -s
    assert resp.status_code==expect

# 为什么接口清单用 fixture 提供，而不是直接写死在用例里？
print("fixture 提供接口清单：数据集中管理、改一处全局生效、所有文件共用")
# 参数化的数据 和 fixture 的数据，各自解决什么问题？
print("参数化 vs fixture：参数化给同一条用例传多组数据（批量）；fixture 提供通用环境 / 准备（复用）")
# 报告里出现 failed 用例，你怎么排查？（说说步骤）
print("配合 pytest 报告：assert X==Y、where 来源、Captured stdout")
# 写代码：从接口清单里找出 "期望状态码 ≠ 实际状态码" 的接口（打印出来）
@pytest.mark.parametrize("path,expect",[
    ("/status/200",200),
    ("/status/201",201),
    ("/status/404",404),
    ("/status/500",500),
    ("/status/404",200), #故意失败（模拟"期望和实际不符"的 bug）
])
def test_check_status(base_url,path,expect):
    resp=requests.get(base_url+path,timeout=5)
    if resp.status_code!=expect:
        print(f"异常接口：{path}，期望 {expect}，实际 {resp.status_code}")  # ✅ 在用例内
    assert resp.status_code == expect
# 思考题（不写代码）：这个项目如果以后接入 CI（比如你用的 Jenkins），哪几步可以自动化？
print("参数化那里可以自动化传入，报告应该也可以自动化")