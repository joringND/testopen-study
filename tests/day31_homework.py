# Day27 部分
# 1. @pytest.fixture(params=["test","vip","admin"]) 被一条用例引用，这条用例会跑几次？（一句话）
print('这条用例跑3次')
# 2. 写代码：一个 logged_client fixture—— 先登录 test/123，yield client，用例后清 token（完整可跑，含装饰器）
import pytest
import requests
from api_client import ApiClient
@pytest.fixture
def logged_client(client):        # ① 参数注入 conftest 的 client
    client.login("test", "123")   # ② setup：登录（不接返回值）
    yield client                  # ③ 把已登录的 client 交给用例
    client.token = None           # ④ teardown：清登录态
# 3. fixture 默认作用域是____；"会被用例改的准备" 用____作用域，"只读且昂贵（读大文件 / 起服务）" 用____作用域
print('fixture的默认作用域是函数，\
      会被用例改→ function（每次新建，安全！）\
      只读且昂贵→ module（每文件一次，省资源）')
# Day28 部分
# 4. xfail 和 skip 的区别？（一句话）
print('xfail是执行后预期失败不报错，skip是跳过不执行')
# 5. 断言 "先挂先停"：一个函数里两条 assert，第一条失败，第二条会执行吗？为什么？（一句话）
print('不会执行.assert 失败 = 抛 AssertionError = 函数立即中断，后面代码不执行')
# 6. 写代码：断言 data["code"] == 0，失败时提示 "登录失败" 并附带实际返回 data（一行）
print('assert data["code"]==0,f"登录失败,{data}"')
# Day29 部分
# 7. -k "not smoke" 和 -m "not smoke" 的区别？（各一句话）
print('-k "not smoke"是筛选名称中不包含smoke，-m "not smoke"是筛选标签中不包含smoke')
# 8. 生成可分享的 HTML 报告，命令是什么？为什么能分享？（简短）
print('"C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe" \
      -m pytest day28_homework.py --html=report_day28_homework.html --self-contained-html\
      之所以能分享，是因为--self-contained-html把所有格式内嵌到报告文件中')
# 9. --tb=no、--tb=short、--tb=long 分别显示什么？
print('--tb=no不显示报错、--tb=short显示关键报错、--tb=long显示所有报错信息')
# Day30 部分
# 10. 写代码 / 命令：你接手一个测试项目，第一件事是什么？理由一句话。
# 然后写出项目里 "全量交付" 的标准命令（含报告、简洁报错）
print('''第一件事是查看项目结构。
@echo off
REM ============================================
REM testopen-study one-click: full tests + HTML report
REM Usage: double-click or type run_tests.bat
REM Prereq: mock_server.py running on port 8000
REM ============================================
set PYTHON=C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe

for /f %%i in ('powershell -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i

echo [1/2] Running all tests...
%PYTHON% -m pytest day25_homework.py day27_homework.py day28_homework.py day30_homework.py -v --tb=short --html=report_%TS%.html --self-contained-html

echo [2/2] Done. Report: report_%TS%.html
start report_%TS%.html
pause
''')