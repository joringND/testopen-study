import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
BASE="http://127.0.0.1:8000"

#手动重试：/flaky前2次500，第3次200
def test_manual_retry():
    resp=None
    for i in range(3):
        resp=requests.get(f"{BASE}/flaky",timeout=5)
        if resp.status_code==200:
            break
    assert resp.status_code==200,f"重试3次仍失败：{resp.status_code}"

#HTTPAdapter Retry：官方重试（带退避）
def test_adapter_retry():
    s=requests.Session()
    retry=Retry(total=3,# 总共重试 3 次
                backoff_factor=0.1,# 每次等 0.1×2^n 秒再试（退避）
                status_forcelist=[500])# 只有 500 才重试
    s.mount("http://",HTTPAdapter(max_retries=retry))
    resp=s.get(f"{BASE}/flaky",timeout=5)
    assert resp.status_code==200

#超时：/slow 要 2 秒，timeout=1 就应放弃
def test_timeout_expected():
    try:
        requests.get(f"{BASE}/slow", timeout=1)
        raise AssertionError("应该超时却没超时！")     # 没超时 = 用例失败
    except requests.exceptions.ReadTimeout:
        pass                                           # 预期超时 → 通过

# 思考：/flaky 第 4 次再请求会怎样？为什么？（想想 FLAKY_COUNT 只增不减）
print('/flaky 第 4 次再请求会上报code 200，因为代码中FLAKY_COUNT[0]此时大于3')
# 思考：登录密码错（401）为什么不能无脑重试？一句话
print('因为功能问题重试100次还是会错，只有网络波动才值得重试')
# Session 复用解决什么问题？api_client 里对应哪个属性？
print("Session复用解决连接复用、提高连接速度以及cookie自动管理的问题，对应api_client的self.session")
# 不设 timeout 会怎样？timeout=(5, 10) 什么意思？
print('不设置timeout，接口挂了会一直等，测试卡死。timeout=(5,10)意思是连接5秒，读取10秒')
# 手动重试和 HTTPAdapter Retry 的区别？
print('手动重试更直观，能自己控制；HTTPAdapter Retry带退避\
手动重试     = 命令式：每个请求自己写 for 循环，谁用谁写 \
HTTPAdapter  = 声明式：配一次挂到 Session，整个 Session 所有请求自动生效\
框架里推荐 Adapter——一处配置，全局生效')
# 什么情况该重试？什么情况不该？（各举一个）
print('网络波动需要重新连接该重试；登录密码错误不该重试')
# 写代码：HTTPAdapter + Retry (total=3, backoff_factor=0.1, status_forcelist=[500]) 完整可跑
def test_adapter_retry_homework():
    s=requests.Session()
    retry=Retry(total=3,backoff_factor=0.1,status_forcelist=[500])
    s.mount("http://",HTTPAdapter(max_retries=retry))
    resp=s.get(f"{BASE}/flaky",timeout=5)
    assert resp.status_code==200