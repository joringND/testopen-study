# 练习1：基础断言 3 个用例
# test_one: assert 10 / 2 == 5
# test_two: assert "test" in "testopen-engineer"
# test_three: assert [1, 2, 3][0] == 1
def test_one():
    assert 10/2==5

def test_two():
    assert "test" in "testopen-engineer"

def test_three():
    assert [1,2,3][0]==1    

# 练习2：结合你的工具箱（import my_tools）
# test_check_status_200: check_status(200) == "通过"
# test_check_status_404: check_status(404) == "接口不存在"
# test_check_status_500: check_status(500) == "服务器错误"
from my_tools import check_status

def test_check_status_200():
    assert check_status(200)=="通过"

def test_check_status_404():
    assert check_status(404)=="接口不存在"

def test_check_status_500():
    assert check_status(500)=="服务器错误" 

# 练习3：异常断言 pytest.raises
# import pytest
# def safe_divide(a, b):
#     if b == 0:
#         raise ZeroDivisionError("除数不能为0")
#     return a / b
# test_safe_divide_ok: safe_divide(10, 2) == 5
# test_safe_divide_error: 用 pytest.raises(ZeroDivisionError) 断言除零会抛异常
import pytest 

def safe_divide(a, b):
    if b == 0:
        raise ZeroDivisionError("除数不能为0")
    return a / b

def test_safe_divide_ok():
    assert safe_divide(10,2)==5

def test_safe_divide_error():
    with pytest.raises(ZeroDivisionError):
        safe_divide(10,0)   # 这行会抛异常 → 用例通过

# pytest 会自动收集什么格式的文件和函数？
print("pytest会自动收集test_开头的文件和函数")
# assert 和 if + print 判断的根本区别？
print("assert是自动判断，if+print需要人眼判断")
# pytest -v 和 pytest -q 的区别？（试一下）
print("""pytest -v    # 详细模式：每个用例一行，逐条显示 PASSED / FAILED
        pytest -q    # 简洁模式：每个用例显示一个点 .，失败的显示 F""")
# 写一个用例：assert 3 in [1, 2, 3]
def test_3_in_list():
    assert 3 in [1,2,3]
# 写一个用例：用 pytest.raises(ValueError) 断言 int("abc") 抛异常
def test_raises_error():
    with pytest.raises(ValueError):
        int("abc")