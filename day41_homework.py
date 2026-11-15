# Day37 配置分离（20 分）
# Q1.（10 分）三层配置模型是哪三层，各层职责是什么？
# 如果一条用例里写 if env_name == "pre": pytest.skip(...)，算不算破坏这个模型？应该怎么做才正确？
print('''
三层配置分别是代码层：只认base_url这个名字，不出现具体地址；配置层：存储test/pre各套地址，供运维修改；
最后是用例层：只写测什么（数据+断言），不知道环境的存在。
一条用例里写 if env_name == "pre": pytest.skip(...)属于破坏模型，只有两个地方正确：
pytestmark = pytest.mark.skipif(env != "test", reason="只在 test 环境跑真实请求")   # 声明式

@pytest.fixture
def real_client(base_url, env_name):
    if env_name != "test":
        pytest.skip(f"{env_name} 是占位环境")      # fixture 里主动跳过
用例体里不出现任何 if env_name
''')
# Q2.（10 分）执行 --env prod 时出现的是 1 failed + 2 errors。请回答：
# FAILED 和 ERROR 在这一轮分别由什么引起？
# 为什么白名单要写成 assert env_name in cfg 而不是 assert env_name in ("test","pre","prod")？
print('''FAILED是由于用例跑起来了，断言不成立；Error是base_url fixture 准备阶段就挂了，用例根本没执行
白名单要写成 assert env_name in cfg,能够提高用例的有效性和可维护性。
''')
# Day38 日志体系（30 分）
# Q3.（10 分）三层日志分工是哪三层，各写什么？为什么请求日志要写在 api_client._log() 里，而不是写在各条用例里？
print('''
日志分工包括：用例执行日志：写准备了什么，拿到了什么
请求响应日志：写实际发了什么，回了什么
失败现场：写挂的那一刻变量是什么
请求日志写在 api_client._log()，在每条用例执行时都会记录请求日志，更加减少代码工作量且便于维护
''')
# Q4.（10 分）caplog 是从哪个模块 import 的？为什么必须写 caplog.set_level(logging.INFO, logger="api_client")？
# 抓到的日志存在哪里，是不是 logs/run.log？
print('''
caplog来自pytest模块，写set_level 只做一件事：在日志源头提高级别门槛。
抓到的日志存在内存中，不是logs/run.log
''')
# Q5.（10 分）日志有两道过滤：logger 级别和 handler 级别。分别在哪一端生效？
# 如果 pytest.ini 里配了 log_file=logs/run.log，但 caplog 抓不到某条日志，最可能是哪一道拦住了？
print('''
logger级别在源头生效，handler在出口（控制台、文件、caplog各一道）生效；
可能是在源头被拦住了
''')
# Day39 失败落盘（20 分）
# Q6.（10 分）@pytest.hookimpl(hookwrapper=True) 为什么必须加？
# report.when 的三个值分别代表什么阶段，为什么只在 call 阶段落盘？
print('''
要等 pytest 把 report 造好才能读 failed / longrepr；直接 return 会被框架覆盖
report.when三阶段：setup（fixture 准备阶段）/ call（用例体执行）/ teardown（清理阶段）
setup 挂 = fixture 问题（没发请求可存）；teardown 挂 = 用例本身其实过了
''')
# Q7.（10 分）两个细节：
# item.name 为什么要过滤 [ ] /
# str(req.body)[:500] 里那个 str() 是防什么的？
print('''
方括号在 Windows 路径里非法。必须过滤 [ ] /
str() 是防上传/表单请求的 body 是 bytes，json.dump 遇 bytes 抛 TypeError
''')
# Day40 报告装配（30 分）
# Q8.（10 分）extras.text 和 extras.html 的本质区别是什么？
# 为什么在 --self-contained-html 下 text 看不到？另外，extras.html 为什么不支持 name= 参数？
print('''
4.0 起 text / json / image 类 extras 被存成 assets 目录下的独立文件，报告里只放链接；
--self-contained-html 下这些外部文件不内联 → 看不到。html 类型是 Raw HTML，直接内嵌.
extras.text(..., name="失败现场") 有标题，extras.html(...) 没有，
所以标题要自己写在 HTML 里（<strong>失败现场</strong>）
''')
# Q9.（10 分）带 @pytest.mark.xfail 的用例真失败时，report.failed 是什么值？
# 这对我们的 hook 意味着什么？如果想让 xfail 用例也留下证据，条件该怎么改？
print('''
report.failed是False，hook直接return，可以做如下修改：
if report.when != "call":
    return
if not (report.failed or getattr(report, "wasxfail", False)):
    return
''')
# Q10.（10 分，综合代码）写出这套链路的三个关键片段，并说明验收点：
# run_tests.bat 里的环境分流那一行（非 test 只跑配置类用例）
print('''
if not "%ENV%"=="test" set FILES=day37_homework.py
''')
# conftest.py 里 hook 的失败判断那一段（含 xfail 兼容的可选写法，用注释标出）
print('''
if report.when != "call":
    return
if not report.failed:
    return
''')
# conftest.py 里把证据内嵌进报告的那三行（含转义）
print('''
extra_list = getattr(report, "extras", [])
escaped = html_lib.escape(json.dumps(exchange, ensure_ascii=False, indent=2))
extra_list.append(extras.html(
    "<div style='font-size:12px;'>"
    "<strong>失败现场</strong>"
    f"<pre style='white-space:pre-wrap;margin:6px 0 0 0;'>{escaped}</pre>"
    "</div>"
))

report.extras = extra_list      # ← 缺这行，记录会被丢弃
''')