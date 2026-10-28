# day30_homework.py —— 标记体系：冒烟 vs 全量
import pytest
import requests

@pytest.mark.smoke #核心链路
def test_smoke_login():
    resp=requests.post("http://127.0.0.1:8000/login",
                       json={"user":"test","pwd":"123"},timeout=5)
    print("\nURL:", resp.url)          # ← 加上：请求到底发到哪了
    print("TEXT:", resp.text)          # ← 加上：404 的 body 是什么
    assert resp.status_code==200

@pytest.mark.smoke #冒烟登录后查用户
def test_smoke_get_user():
    s = requests.Session()
    resp=s.post("http://127.0.0.1:8000/login",
           json={"user": "test", "pwd": "123"}, timeout=5)
    token = resp.json()["token"]                                  # ① 从登录返回拿 token
    resp2 = s.get("http://127.0.0.1:8000/get_user",
                  headers={"Authorization": f"Bearer {token}"}, timeout=5)   # ② 手动带头
    assert resp2.json()["name"] == "张三"

def test_full_get_order():
    s = requests.Session()
    resp = s.post("http://127.0.0.1:8000/login",
                  json={"user": "test", "pwd": "123"}, timeout=5)
    token = resp.json()["token"]
    resp2 = s.get("http://127.0.0.1:8000/get_order",
                  headers={"Authorization": f"Bearer {token}"}, timeout=5)
    assert resp2.json()["order_id"] == "ORD-1001"

# 日常回归：   python -m pytest dayXX*.py -v --tb=short
# 冒烟测试：   python -m pytest dayXX*.py -m smoke -q
# 全量交付：   run_tests.bat（一键 + 报告）

#项目分层解决的核心问题是什么？（一句话）
print("改数据不动用例、改框架不动用例、改用例不动配置——一处改动只影响一类文件")
#冒烟测试是什么？-m smoke 跑的什么？
print('冒烟测试是核心功能的 "过一遍就跑"。-m smoke跑的是标记为冒烟的用例')
#一键运行脚本（run_tests.bat）解决什么问题？set PYTHON=... 那行是干嘛的？
print('把 "标准跑法" 固化成一个脚本。set PYTHON=...是用来指定解释器')
#报告为什么带时间戳？不带会怎样？
print('用来对测试活动进行留痕。不带会用新的测试报告替换旧的')
#写代码：run_tests.bat 完整内容（全量 + 报告 + 打开，含注释）
print('''
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
