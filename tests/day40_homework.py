# 报告里加一行摘要：在 extras 里再塞一条 extras.text(f"{exchange['method']} {exchange['path']} -> {exchange['status']} {exchange['cost_ms']}ms", name="请求摘要")
# bat 换环境：跑 .\run_tests.bat pre，观察 day37 的行为变化（哪条 skipped？其他用例是否受影响？）
# 统计证据数量：用 pytest_terminal_summary 钩子在末尾打印本次生成多少个 artifacts（提示：len(os.listdir("artifacts"))）

# pytest-html 里往报告塞额外内容用哪个 API？为什么不能直接 report.extras.append(...)？
# pytest_plugins = ("pytest_html",) 这行是干什么的，不放会怎样？
# run_tests.bat 里为什么要逐条列文件名，而不是直接 pytest？
# set ENV=%1 里的 %1 是什么？不传参数时会怎样？
# 全量跑之前为什么要重启 mock_server？不重启会出现什么现象？