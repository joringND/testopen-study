# Day32 题（2 分）
# Q1. requests 上传文件用哪个参数？为什么不是 file=？上传成功后通常断言哪三样？
print('使用files=参数，file是参数而非参数名。上传成功后要断言data["code"]==0,断言data["filename"]=="hello.txt"\
    以及断言data["size"]==11')
# Q2. 下载大文件为什么要 stream=True？iter_content() 是干什么的？
print('使用流式读，大文件不占内存，iter_content代表每块多少字节')
# Day33 题（3 分）
# Q3. Session 复用解决哪两层问题？之前说 "Session 要慎用"，慎的是什么？和 "每个用例都用 Session" 矛盾吗？
print('Session复用解决连接复用、提高连接速度以及cookie自动管理的问题。慎用的是“共享”而非“使用”。\
      连接层每个用例都用Session完全没有问题')
# Q4. timeout=(5, 10) 的两个数字分别是什么？完全不设 timeout 会发生什么？
print('timeout(5,10)代表连接5秒，读取10秒。完全不设 timeout 会导致接口挂了会一直等，测试卡死')
# Q5. 什么情况该重试、什么不该（各举一例）？Retry(status_forcelist=[500]) 是什么意思？
print('网络波动需要重新连接该重试；登录密码错误不该重试。\
      Retry(status_forcelist=[500])意思是当状态码为500时触发重试')
# Day34 题（2 分）
# Q6. @pytest.mark.parametrize 的数据（如 load_cases()）在哪个阶段执行？数据文件不存在会怎样？
print('会在用例的收集阶段执行。数据文件不存在会报错')
# Q7. 把 load_cases() 放进用例内部 for 循环，和 parametrize 的本质区别是什么？说出三个后果。
print('for 循环 = 1 条用例跑 N 遍（失败即停、无法定位）；parametrize = N 条独立用例（隔离、逐条报告）\
      先挂先停：第 1 组数据断言失败 → 整个函数抛错终止 → 后面 3 组测不到\
      报告无法定位：失败了显示 test_login_loop 一行，看不出是哪组数据挂的（[case2] admin 还是 [case3] wrong？）\
      脏了状态，影响后面')
# Day35 题（2 分）
# Q8. 断言四层分别是什么？只断状态码会漏什么类型的 bug（举一例）？
print('断言的四层分别是状态码、业务码、字段值、结构。只断状态码会漏业务码、字段值和结构的bug比如字段值或key缺失')
# Q9. isinstance(True, int) 结果是什么？断 is_vip 该怎么写？key 集合断言为什么必须 set(data.keys())？
print('isinstance(True, int)是True。isinstance(data["is_vip"],bool)\
      set(data.keys())是对集合做判断而集合相等，多一个少一个都失败')
# 综合代码题（1 分）
# Q10. 写一条完整用例：用 client fixture + parametrize 2 组数据 + assert_structure，
# 断言 /get_order 的结构（code: int, order_id: str, amount: float）。
# 数据可以是 2 组不同的请求头场景（比如 "正常 token" 和 "篡改 token 期望 401"）—— 写出你的思路即可，能跑通加分。
import pytest
import requests
from api_client import ApiClient

BASE="http://127.0.0.1:8000"

def assert_structure(data,schema):
    assert set(data.keys())==set(schema.keys()),\
        f"字段不符: 实际={sorted(data.keys())} 期望={sorted(schema.keys())}"
    for k,t in schema.items():
        assert isinstance(data[k],t),\
            f"{k} 类型错: 实际 {type(data[k]).__name__} 期望 {t.__name__}"
        
@pytest.mark.parametrize("scene,schema", [
    ("normal",   {"code": int, "order_id": str, "amount": float}),
    ("tampered", {"code": int, "msg": str}),        # 401 的返回体结构
])
def test_order_scene(client,scene,schema):
    if scene =="normal":
        data=client.get_order().json()
    else:
        resp=requests.get(f"{BASE}/get_order",
                          headers={"Authorization": "Bearer bad-token"},
                          timeout=5)
        assert resp.status_code==401
        data=resp.json()
    assert_structure(data,schema)

