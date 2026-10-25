# Day26 学习笔记：第 4 周复盘（接口框架深化毕业考）

> 日期：2026-10-25
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 4 周 · Day26
> 成绩：✅ 9/10（1 题概念错，错题回顾后毕业）
> 里程碑：**第 4 周毕业——接口测试框架完整成型**

---

## 一、第 4 周全景（Day21~26 接口框架深化）

```
Day21 请求基础 → Day22 封装 → Day23 框架 → Day24 数据驱动 → Day25 工程化 → Day26 复盘
```

主线：会发请求 → 用类封装重复逻辑 → 收进框架自动认证 → 数据驱动分离用例与数据 → 工程化配置可交付。

## 二、毕业考批改记录（10 题）

| 题 | 判定 | 要点 |
|---|---|---|
| 1 session 自动带凭证 | ✅ | session 内部 cookie jar，Set-Cookie 后自动携带 |
| 2 token vs cookie | ✅ | cookie=浏览器侧自动带；token=凭证放 Authorization 头（框架走 Authorization） |
| 3 懒登录 | ✅ | `self.token is None` → 先 login |
| 4 fixture 默认作用域 | ❌ | **function = 每个用例重新创建**（不是"第一个函数"） |
| 5 `-m "not smoke"` | ✅ | 其他标记 + 无标记用例全选中 |
| 6 base_url fixture | ✅ | 读 env.json 完整可跑 |
| 7 数据驱动参数化 | ✅ | 3 组数据断言 code |
| 8 Calculator 类 | ✅ | self 使用正确（Day22 坑愈合） |
| 9 mock 重启 | ✅ | serve_forever 跑启动时代码 |
| 10 加接口改三处 | ✅ | api_client + mock + 用例/数据 |

## 三、错题回顾（唯一失分点）

**fixture 作用域**（必背）：

| scope | 含义 | 影响 |
|---|---|---|
| `function`（默认） | 每个测试函数各自创建 | 用例独立、不串数据 |
| `class` | 每个测试类一次 | 同类共享 |
| `module` | 每个模块一次 | 同文件共享 |
| `session` | 整个会话一次 | 全共享（登录态互相污染） |

**记法**：fixture 默认"每个用例都换新"——安全第一。接口测试的 client 用 function 是正确的选择。

## 四、第 4 周资产清单（简历级产出）

```
api_client.py   自动认证（懒登录+401重试）客户端
conftest.py     client/base_url fixture（多环境查表）
data/cases.json 场景化数据驱动（一行=一个场景）
mock_server.py  v4 靶场（token 过期机制 + vip 区分）
pytest.ini      项目配置（testpaths/markers/addopts）
config/env.json 测试/预发环境一键切换
```

## 五、第 4 周高频坑复盘（进入第 5 周的预防针）

| 坑 | 教训 |
|---|---|
| mock 改完没重启（×3 次） | 改 mock → 重启 → 再跑 |
| elif 链分支嵌错层级 | 接口分支兄弟平级，认证判断在内层 |
| 框架方法里硬断言 | 方法管怎么做、用例管对不对（分层） |
| JSON 语法三雷 | 双引号/无尾逗号/小写值 |
| 断言变量名复制漏改 | 变量名和字段名一起核对 |

## 六、第 5 周预告（Day27 起：pytest 高级 + 框架落地）

- fixture 进阶：参数化 fixture、作用域实战（module/session 何时用）
- xfail（预期失败）与断言技巧
- 框架工程落地：把四件套整合成"第一个完整接口自动化项目"（真实可交付）
- 报告与 CI 集成基础（pytest-html + 自动化触发）

---

*笔记由 AI 根据当日学习内容整理。*
