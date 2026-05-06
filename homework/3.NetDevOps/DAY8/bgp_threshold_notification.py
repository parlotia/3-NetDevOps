#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""
BGP前缀阈值告警脚本 - 运行于IOS-XE Guestshell
由EEM Applet bgp_prefix_threshold_notification调用

EEM action 6.0 调用方式:
  guestshell run python3 /home/guestshell/bgp_threshold_notification.py \
    received from $ipaddr : $current_prefix exceeds limit $max_prefix

EEM传入的参数格式示例:
  received from 10.10.1.201 : 2 exceeds limit 2
"""

import re
import sys
import io
import os
import datetime
from qyt_smtp_attachment import qyt_smtp_attachment

# Guestshell默认ASCII编码, 需强制切换为UTF-8以支持中文输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ==================== SMTP邮件配置 ====================
# QQ邮箱SMTP服务器 (使用SSL端口465)
MAIL_SERVER = 'smtp.qq.com'
MAIL_USER = '1975141437@qq.com'
MAIL_PASS = 'avpjlsuqzmwydjij'
MAIL_FROM = '1975141437@qq.com'
MAIL_TO = '1975141437@qq.com'

# ==================== 主程序 ====================

# 将EEM传入的所有命令行参数拼接为原始字符串
para_raw = ' '.join(sys.argv[1:]).strip()

# EEM传入的参数格式示例:
# received from <BGP邻居IP> : <当前前缀数量> exceeds limit <最大前缀阈值>

# 使用re.match提取BGP邻居IP、当前前缀数量、最大前缀阈值
match = re.match(r'received from ([0-9.]+) : (\d+) exceeds limit (\d+)', para_raw)

if match:
    # 提取正则匹配的三个分组
    bgp_neighbor = match.group(1)        # BGP邻居IP
    current_prefix = match.group(2)      # 当前前缀数量
    max_prefix = match.group(3)          # 最大前缀阈值

    # 拼接邮件主题
    mail_subject = f'BGP前缀阈值告警 - 邻居 {bgp_neighbor}'

    # 拼接邮件正文 (与任务四期望格式一致)
    mail_body = (
        f'Neighbor: {bgp_neighbor}\n'
        f'Now: {current_prefix}\n'
        f'Exceed the limit: {max_prefix}\n'
    )

    # 打印告警信息到Guestshell控制台
    print(f'[!] BGP前缀阈值告警!')
    print(f'    BGP邻居: {bgp_neighbor}')
    print(f'    当前前缀数: {current_prefix}')
    print(f'    最大前缀阈值: {max_prefix}')

    # 调用邮件函数发送告警邮件
    qyt_smtp_attachment(
        mailserver=MAIL_SERVER,
        username=MAIL_USER,
        password=MAIL_PASS,
        from_mail=MAIL_FROM,
        to_mail=MAIL_TO,
        subj=mail_subject,
        main_body=mail_body,
    )

else:
    # 正则匹配失败, 打印调试信息
    print(f'[-] 无法从参数中提取BGP告警信息')
    print(f'    原始参数: {para_raw}')
    print(f'    期望格式: received from <IP> : <当前前缀> exceeds limit <最大阈值>')