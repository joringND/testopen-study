import pytest


def assert_structure(data, schema):
    assert set(data.keys()) == set(schema.keys()), \
        f"字段不符: 实际={sorted(data.keys())} 期望={sorted(schema.keys())}"
    for k, t in schema.items():
        assert isinstance(data[k], t), \
            f"{k} 类型错: 实际 {type(data[k]).__name__} 期望 {t.__name__}"


# ✅ client 从 conftest.py 的 fixture 注入（已含 base_url，懒登录）
def test_user_structure(client):
    data = client.get_user().json()
    assert_structure(data, {"code": int, "name": str, "age": int})
    assert data["name"] == "张三"


def test_order_structure(client):
    data = client.get_order().json()
    assert_structure(data, {"code": int, "order_id": str, "amount": float})


def test_echo_nested(client):
    data = client.echo({"user": "test", "level": 3}).json()
    assert data["code"] == 0
    assert isinstance(data["echo"], dict)
    assert set(data["echo"].keys()) == {"user", "level"}
    assert isinstance(data["echo"]["level"], int)


SCHEMAS = [
    ("get_user",  {"code": int, "name": str, "age": int}),
    ("get_order", {"code": int, "order_id": str, "amount": float}),
    ("get_vip",   {"code": int, "is_vip": bool}),
]


# ✅ fixture 管环境 + parametrize 管数据——两个一起用
@pytest.mark.parametrize("method,schema", SCHEMAS)
def test_schema_ddt(client, method, schema):
    data = getattr(client, method)().json() # getattr 按名字动态调方法
    assert_structure(data, schema)

# 思考：为什么 assert set(data.keys()) == {...} 比 assert "code" in data.keys() 严格？一句话
print('因为集合相等，多一个少一个都失败')
# 思考：断 is_vip 时如果写 isinstance(data["is_vip"], int)，True 会过吗？为什么？（bool 陷阱）
print('会过，bool是int的子类')
# 只断状态码 + 一个字段值，会漏什么类型的 bug？（举一种）
print('漏 “没断的字段” = 没测的字段。\
      前几层断言只验证 “你写出来的那几个条件”，而结构断言验证 “整张返回的骨架”。结构变了没人告诉你，只有结构断言能抓。')
# 怎么断言 "key 不多不少"？
print('assert set(data.keys())=={……}')
# isinstance(True, int) 结果是什么？断 bool 字段要注意什么？
print('结果是True。断 bool 字段要用isinstance(x,bool)或type(x) is bool')
# 嵌套结构 {"code":0,"echo":{"user":"test"}} 怎么断言内层？
print('先断言isinstance(data["echo"],dict),再断言set(data["echo"].keys()) == {"user"} ，\
      最后断言isinstance(data["echo"]["user"], str) ')
# 写代码：assert_structure(data, schema) 完整实现（key 集合 + 类型）
def assert_structure(data, schema):
    assert set(data.keys())==set(schema.keys()),f'字段不符: 实际={sorted(data.keys())} 期望={sorted(schema.keys())}'
    for k,t in schema.items():
        assert isinstance(data[k],t),\
            f'{k} 类型错: 实际 {type(data[k]).__name__} 期望 {t.__name__}'