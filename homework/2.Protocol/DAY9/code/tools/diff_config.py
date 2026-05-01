#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""Day 9 - 配置差异比较工具"""

import os
from difflib import Differ


def diff_file(file1, file2):
    """比较两个文本文件的逐行差异。"""
    with open(file1, 'r', encoding='utf-8') as txt1_file:
        txt1 = txt1_file.readlines()

    with open(file2, 'r', encoding='utf-8') as txt2_file:
        txt2 = txt2_file.readlines()

    result = Differ().compare(txt1, txt2)
    return os.linesep.join(list(result))


def diff_txt(txt1, txt2):
    """比较两段文本的逐行差异。"""
    txt1_list = txt1.splitlines()
    txt2_list = txt2.splitlines()
    result = Differ().compare(txt1_list, txt2_list)
    return os.linesep.join(list(result))


if __name__ == '__main__':
    sample_old = 'hostname C8Kv1\ninterface Loopback0\n ip address 1.1.1.1 255.255.255.255'
    sample_new = 'hostname C8Kv1\ninterface Loopback0\n ip address 1.1.1.2 255.255.255.255'
    print(diff_txt(sample_old, sample_new))
