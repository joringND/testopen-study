# ===== test_first.py =====
# 命名规则：文件 test_ 开头，函数 test_ 开头
def test_add():
    assert 1+1==2

def test_string():
    assert "hello" in "hello world"

def test_list():
    assert len([1,2,3])==3

def test_status():
    status=200
    assert status==200

# ✅ pytest（机器自动判定）：常见断言写法
def test_api():
    result =0
    data=[1,2,3]
    assert 1+1==2              #相等
    assert "abc" in "abcdef"   #包含
    assert result is True      #是True  FAILED test_first.py::test_api - assert 0 is True自动指出失败原因
    assert 200!=400            #不相等
    assert len(data)>0         #大于，非空
