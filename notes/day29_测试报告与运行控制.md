# Day29 学习笔记：测试报告与运行控制

> 日期：2026-10-28
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 5 周 · Day29
> 状态：✅ 自测 4/5（1 题关键概念错已回顾）；HTML 报告实践
> 里程碑：结果能"发出去给人看"了 + 运行控制五件套

---

## 一、今日目标

1. pytest-html 生成 HTML 测试报告（能发给别人看）
2. 运行控制：`-k` 选用例、`--tb` 报错模式、`-q` 安静、`--maxfail` 止损、addopts 固化

## 二、今日涉及文件

| 操作 | 文件 | 改动 |
|---|---|---|
| 【新建】 | `day29_homework.py` | 练习（若写用例） |
| 【生成】 | `report.html` | pytest-html 产物 |
| 【修改】 | `pytest.ini` | addopts 固化常用参数 |

## 三、知识点 1：HTML 测试报告（pytest-html）

```powershell
... -m pytest day28_homework.py --html=report.html --self-contained-html
```

- 环境已装 **pytest-html 4.2.0**（pytest 输出 plugins 里可见）
- 报告含：用例列表（名/状态/耗时）、通过率统计、失败详情（含断言语义化提示）
- `--self-contained-html`：**样式内嵌进单个文件** → 复制给同事/放 CI，对方打开就能看，不依赖本机样式

## 四、知识点 2：运行控制五件套

| 参数 | 作用 | 例子 |
|---|---|---|
| `--html=xx.html` | 出 HTML 报告 | `--html=report.html` |
| `--self-contained-html` | 单文件内嵌样式 | 配上面用 |
| `-k "关键字"` | **按用例名字符串**筛选（支持 and/or/not） | `-k "get_user or echo"` / `-k "not vip"` |
| `--maxfail=1` | 第一个失败即停（回归止损） | `--maxfail=1` |
| `-q` | 安静模式（只显示 . 和 F） | `-q` |
| `--tb=no/short/long` | 报错堆栈长度 | short=日常最常用 |

**--tb 三档**：long=完整堆栈（默认）；short=关键几行（日常）；no=只看谁挂。

## 四.5 补充：-v / -q / -s 输出详略对比（答疑补录）

**两个维度**：`-v / -q` 管 pytest 自身报告详略（同一维度的两端）；`-s` 管是否显示用例代码里的 print（另一个维度）。

| 组合 | 效果 | 场景 |
|---|---|---|
| （默认） | 一行进度字符（. F x s）+ 总结 | 快速看结果 |
| `-q` | 只显示进度字符 + 总结（最短） | CI 里少刷屏 |
| `-v` | 每条用例一行详情（文件名::函数名 + 状态） | **日常最常用** |
| `-s` | 显示用例内 print（默认被 pytest 捕获吞掉） | 调试/看输出 |
| `-v -s` | 详情 + print | 当前标准姿势 ✅ |
| `-q -s` | 进度字符 + print | 又安静又能看 print |

**输出形态对比**（同批 2 passed 1 xfailed）：
- 默认：`day28_homework.py ..x.` + 总结一行
- `-q`：`..x.` + 总结（无文件名）
- `-v`：`day28_homework.py::test_get_orders XFAIL` 每条一行
- `-s`：print 内容夹在用例名和 PASSED 之间显示

**记忆**：`-v`=verbose 详细、`-q`=quiet 安静、`-s`=show 显示 print。

## 五、知识点 3：pytest.ini addopts 固化

```ini
[pytest]
markers =
    smoke: 冒烟测试
    full: 全量测试
addopts = -v --tb=short
```

addopts 里的参数自动叠加到每次运行；命令行参数接在后面。

## 六、⚠️ 今日关键纠错：`-k`（名字）≠ `-m`（标记）

```
-k "smoke"  → 按【用例名字符串】匹配（函数名/节点名里含 "smoke"）
-m "smoke"  → 按【标记 marker】匹配（带 @pytest.mark.smoke）——Day25 学的
```

关键反例：

```python
@pytest.mark.smoke
def test_login_normal():        # 有 smoke 标记但名字不含 smoke
# -m "smoke" → ✅ 选中；-k "smoke" → ❌ 不选中
```

**记忆口诀**：`-k` 管名字（函数名），`-m` 管标签（@pytest.mark 装饰器）——两套独立的筛选系统。

## 七、自测批改记录（4/5）

| 题 | 判定 | 要点 |
|---|---|---|
| 1 HTML 报告命令/self-contained | ✅ | 命令完整；样式内嵌单文件、分享/CI 不依赖本机 |
| 2 `-k "not smoke"` | ❌ | 名字匹配非标记匹配（错题回顾见六） |
| 3 `--tb=no` vs short | ✅ | no=不显示；short=关键几行 |
| 4 `--maxfail=1` | ✅ | 遇错即停，回归止损 |
| 5 addopts 配置 | ✅ | markers+addopts 格式正确 |

## 八、明日预告（Day30）

**框架工程化整合**（第 5 周"框架落地"收尾）：
- 把 5 周所学整合成一个小测试框架：项目分层（用例/客户端/配置分离）+ 一键运行脚本
- 标记体系 + 数据驱动 + 报告生成组合成"标准跑法"
- 预告题：你的项目里"跑测试"的标准姿势应该是什么？

---

*笔记由 AI 根据当日学习内容整理。*
#（注：内容由AI生成）
