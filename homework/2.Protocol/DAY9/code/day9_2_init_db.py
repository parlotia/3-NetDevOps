#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""Day 9 - 初始化配置备份数据库"""

import os
import sys

# crond 调度时当前工作目录不固定, 需要把 day9 代码目录加入搜索路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from day9_1_model import Base  # noqa: E402
from day9_1_model import engine  # noqa: E402


def init_database():
    """创建 Day 9 使用的全部数据表。"""
    Base.metadata.create_all(engine, checkfirst=True)
    print('[+] Day 9 数据库表已经创建完成')


if __name__ == '__main__':
    init_database()
