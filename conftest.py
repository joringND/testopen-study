# ===== conftest.py：pytest 自动加载，fixture 全局共享 =====
import os
import datetime
import logging
import json
import pytest
import requests
from api_client import ApiClient
from pytest_html import extras
import html as html_lib
"""
根 conftest：只做装配，不承载实现。
按职责拆到 support/ 下的三个插件：
  env_config    -> --env 参数 + env_name / env_config / base_url
  api_fixtures  -> client 等客户端 fixture
  reporting     -> 失败落盘 + 报告内嵌 + 终端汇总
"""

pytest_plugins = (
    "support.env_config",
    "support.api_fixtures",
    "support.reporting",                            
)
