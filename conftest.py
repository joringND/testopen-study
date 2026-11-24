# ===== conftest.py：pytest 自动加载，fixture 全局共享 =====
"""根 conftest：只做装配，不承载实现。

职责已拆到 support/ 下三个插件：
  env_config   -> --env 参数 + env_name / base_url
  api_fixtures -> client / check_client / make_token
  reporting    -> 失败落盘 + 报告内嵌 + 终端汇总
"""

pytest_plugins = (
    "support.env_config",
    "support.api_fixtures",
    "support.reporting",
)