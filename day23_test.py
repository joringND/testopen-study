import json
import pytest
with open("data/users.json","r",encoding="utf-8") as f:
    USERS=json.load(f)

@pytest.mark.parametrize("case",USERS)
def test_login_cases(client,case):
    resp=client.login(case["user"],case["pwd"])
    assert resp.json()["code"]==case["expect_code"]