# 一、概念题（Q1–Q2，20 分）
# Q1（10 分） Day42 把 conftest 的六个职责拆成哪三个插件？分别装了哪些职责？
print('''conftest的6个职责被拆解成了env_config:存放--env+env_name+base_url;
api_fixtures:client等fixture；reporting：落盘钩子+extras+终端汇总''')
# 为什么 pytest_plugins 只能写在顶层 conftest.py？如果把它挪进 tests/conftest.py，pytest 会报什么？
print('''
pytest_plugins写在非顶层conftest会导致报错；
如果把它挪进 tests/conftest.py，pytest 会报：Defining 'pytest_plugins' in a non-top-level conftest is no longer supported
''')
# Q2（10 分） Day42 那次，support/reporting.py 被改成空文件后，conftest.py 里 logger.info(...) 报 NameError，结果不是 "某条用例失败"，而是整场 INTERNALERROR，连 1 passed 都不输出。
# 请解释：为什么 hook 里抛的异常会升级成整场崩溃，而不是降级成普通失败？这说明了 hook 与 fixture 在 "作用范围" 上的什么区别？
print('''
异常发生在pytest_runtest_makereport这个全局钩子内部，异常冒泡到 wrap_session → pytest 判定框架自身出错 → 整个 session 中断。
为什么不能降级：fixture 崩了还能记成 “用例 error”，hook 崩了连记录容器都没有。
hook作用于整个session，fixture只作用于一条用例
''')
# Q3（10 分） 打开 D:\Desktop\my_python\learn\testopen-study\conftest.py，你会看到里面还留着一个：
# @pytest.fixture
# def client(base_url):
#     return ApiClient(base_url)
# 而 support/api_fixtures.py 里也有一个一模一样的：
# @pytest.fixture
# def client(base_url):
#     return ApiClient(base_url)
# 请回答三个子问题：
# 用例请求 client 时，pytest 实际用的是哪一个？
print('''
pytest实际用的是conftest.py里的client
''')
# 依据是什么（conftest.py 与 pytest_plugins 加载的插件，谁的层级更高）？
print('''conftest.py 与 pytest_plugins 加载的插件,conftest.py的插件层级更高''')
# 这个重复除了 "多余"，还会造成什么实际问题？举一个你以后会踩到的场景。
print('''当两处配置不一致时，会造成混乱
你想给 client 加一个超时参数，改的是 support/api_fixtures.py。跑一遍发现完全没生效，因为根 conftest.py 里那个同名 client 把它盖住了。你会开始怀疑 “插件没加载”“pytest_plugins 写错了”，查半小时，最后发现是两处同名。
这就是重复定义的真实成本：它不会报错，只会让你的修改静默失效
''')
# 三、分层题（Q4–Q6，30 分）
# Q4（10 分） TestApi.__init__ 里那句 super().__init__(base_url)：
# 执行完之后，self 上有哪两批属性？分别是谁放的？
print('''
self上有父类HttpSession.__init__放的属性：base_url / timeout / session / token / last_exchange；
以及子类TestApi.__init__放的user / pwd
''')
# 如果这句删掉，第一个报错会出现在哪里、报什么？为什么不报在 __init__ 里？
print('''删掉 super().__init__(base_url) 后，__init__ 本身不会报任何错。self.user = user、self.pwd = pwd 照样赋值成功，函数正常返回。属性缺失不是语法错误，Python 不会在赋值阶段检查 “你还有没有 self.token”。
所以错误延迟到第一次真正使用父类属性时才炸：client.get_user() → _request() → if not self.token → AttributeError
这就是“错误发生点 ≠ 根因点”。根因在 __init__，报错在 _request，中间隔了两层调用 ''')
# Q5（10 分） 401 自动重登为什么必须放在 TestApi._request，不能下移到 HttpSession.request？
# 从概念归属和依赖方向两个角度各说一句。再补一句：如果硬要放传输层，只能改成什么形式？
print('''
概念归属：“登录”是业务动作，传输层只知道“有一个 token 字符串”
依赖方向：传输层要重登就得知道登录接口路径和账号密码，等于业务逻辑下沉，http_session 要反向依赖业务 → 循环依赖
如果硬放传输层，只能写成“传入一个 on_401 回调”，那也是把业务概念塞进了管道。
''')
# Q6（10 分） Day43 修过一个真实故障：
# TypeError: login() takes 1 positional argument but 3 were given
# 这个错误是怎么产生的（当时的签名 vs 用例的调用）？
print('''用例和 fixture 里是 client.login("test", "123")，我给的 TestApi.login(self) 接不住。
3 were given = self + "test" + "123" ''')
# "签名" 具体指什么？列出至少三项改动会破坏兼容、三项改动不影响兼容的内容。
print('''函数签名（signature）= 函数的对外承诺：叫什么名字、几个参数、什么顺序、有没有默认值
破坏兼容	               不影响兼容
改方法名	               改函数体逻辑
改参数个数（增 / 减）	改注释、docstring
改参数顺序	                 改局部变量名
改参数名（关键字调用时会断）	加日志、加断言
删方法	                   改内部实现（调别的私有方法）
把有默认值的参数改成必填	调整语句顺序（语义不变）
''')
# 四、目录与收集题（Q7–Q9，30 分）
# Q7（10 分） 有人以为 pythonpath = . 里的 . 是 " 执行 pytest 时所在的目录 "。请指出错在哪，并说明：
# . 实际相对谁解析？
# 为什么 pytest.ini 一旦搬进 tests/，pythonpath 就会指向错误的地方？
print('''
. 实际相对相对 rootdir 解析，不是执行命令的当前目录，也不是配置文件所在目录
rootdir 由 pytest.ini 的位置决定
''')
# Q8（10 分） 同一个文件：
# 表格
# 命令	结果
# pytest tests/day37_homework.py	collected 3 items
# pytest tests	collected 0 items
# 请解释这个差异的机制。并回答：python_files 是 "覆盖" 还是 "追加"？只写 python_files = day*_homework.py 会造成什么后果？
print('''
前者显式指定文件，直接收集，不检查命名；后者进入目录后按python_files过滤文件名。python_files 是“覆盖”而不是“追加”
只写 day*_homework.py，以后新建 test_login.py 反而收不到。
''')
# Q9（10 分） Day44 把 bat 从 "11 个文件名" 改成 FILES=tests，收集数从 48 变成 99，还多出 4 条 xfail。
# 清单式回归的三重代价是什么？
print('''
1	要手工维护	新增用例必须记得加进 FILES，忘了就不跑，而且没有任何提示
2	一个笔误拖死整场	file or directory not found 让 pytest 放弃整个收集，你看到的只是 collected 0 items，错误信息离真相很远
3	覆盖范围受限	只跑 “我记得的那批”，仓库里其他用例失败了你永远不知道
''')
# 那 4 条 xfail 是怎么来的（说出它们失败的根因类型即可，不必逐条列）？
print('''
写死旧 token 值	assert data["token"] == "token123"，mock 已改动态 token-N
硬编码认证头	Bearer token123 不是当前 LATEST_TOKEN
依赖 Cookie 认证	mock 只认 Authorization: Bearer，Session 方案不成立
用旧版客户端类	文件内自查那个 ApiClient 不保存 token
''')
# 为什么说 "迁移不会让旧代码变坏，但会让旧代码的坏暴露"？
print('''
清单式：跑的是“我记得的那批”，旧文件永远不会告诉你它坏了
目录式：跑的是“仓库里全部”，坏掉的会自己举牌
从“我以为全绿”到“我知道哪 4 条是红的”，信息量完全不同。这是迁移最实在的收益，比“目录整齐”重要得多
不是因为清单式会漏，是因为清单式让你从来不知道它们坏了。
''')
# 五、综合题（Q10，10 分）
# Q10（10 分） 你接了一个新项目，结构如下：
# shop-api-tests/
# ├── cases/          ← 要放用例
# ├── core/           ← 要放客户端（api 类）
# ├── conf/env.json   ← 环境和地址的映射
# ├── plugins/        ← 要放 conftest 拆出去的插件
# └── data/           ← 测试数据 json
# 请给出能直接落地的方案：
# 目录树（标出哪些文件必须留在项目根）
print('''
shop-api-tests/
├── pytest.ini              ← 留根：决定 rootdir
├── conftest.py             ← 留根：pytest_plugins 只能顶层
├── plugins/                ← 留根：被 import
│   ├── __init__.py
│   ├── paths.py            ← 路径常量唯一出处
│   ├── env_config.py
│   ├── api_fixtures.py
│   └── reporting.py
├── core/                   ← 留根：被 import
│   ├── __init__.py
│   ├── http_session.py
│   └── shop_api.py
├── conf/env.json           ← 留根：被 paths.py 引用
├── data/*.json             ← 留根：被 paths.py 引用
├── artifacts/  logs/       ← 留根：运行时生成
└── cases/                  ← 只放用例
    ├── test_login.py
    └── test_order.py
''')
# pytest.ini 的相关配置（testpaths / pythonpath / python_files 三项）
print('''
testpaths = cases
pythonpath = .
python_files = test_*.py *_test.py 
addopts = -v
markers =
    smoke: 冒烟用例，验证核心链路
    full: 全量回归用例
''')
# conftest.py 的内容（几行就够）
print('''
pytest_plugins = (
    "plugins.env_config",
    "plugins.api_fixtures",
    "plugins.reporting",                            
)
''')
# 用例文件里：import 客户端该怎么写？读 data/xxx.json 该怎么写？（要保证 "从任何目录执行 pytest 都不会错"）
print('''
import 客户端该怎么写:
from core.shop_api import ShopApi
读 data/xxx.json 该怎么写？
# plugins/paths.py（或 core/paths.py）
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")
CONFIG    = os.path.join(BASE_DIR, "conf", "env.json")

# cases/test_login.py
import os
from plugins.paths import DATA_DIR

with open(os.path.join(DATA_DIR, "users.json"), encoding="utf-8") as f:
    cases = json.load(f)
    判断标准很简单：代码里出现 "data/xxx.json" 这种以目录名开头的相对路径，就是隐患。 
    相对路径只允许出现在 “路径常量文件” 里一次，其余地方全部走常量
''')
# 如果要 "只跑冒烟用例"，命令是什么？需要提前做什么？
print('''pytest cases -m smoke  
需要提前在pytest.ini里加入smoke这个markers、给用例打 @pytest.mark.smoke
''')