"""所有路径常量的唯一出处"""
import os
#support/的上一级=项目根目录
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_PATH=os.path.join(BASE_DIR,"config","env.json")
ARTIFACT_DIR=os.path.join(BASE_DIR,"artifacts")
LOG_DIR=os.path.join(BASE_DIR,"logs")
#为什么用绝对路径：原来写 "config/env.json" 是相对当前工作目录，只有 “在项目根目录下执行 pytest” 才有效。
# 用 BASE_DIR 拼出来，从任何目录跑都不会找错文件。
