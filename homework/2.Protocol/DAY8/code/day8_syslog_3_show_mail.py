#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
import sys

# 添加当前脚本所在目录到Python搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from day8_syslog_1_create_db import Syslog, engine
from sqlalchemy import func
from tools.day8_pygal_pie import pygal_pie
from tools.smtp_send_mail_img import qyt_smtp_img
from jinja2 import Template

# 加载环境变量
load_dotenv()

# 文件保存路径
current_dir = os.path.dirname(os.path.realpath(__file__))

# 配置jinja2模板目录
tem_path = os.path.join(current_dir, 'templates')

# jinja2读取邮件HTML模板
with open(os.path.join(tem_path, 'syslog_email.template'), encoding='utf-8') as f:
    syslog_email_template = Template(f.read())


Session = sessionmaker(bind=engine)
session = Session()

# 严重级别名字列表
severity_level_name_list = []

# 严重级别数量列表
severity_level_count_list = []

# 数据库中找到严重级别名字, 严重级别数量的信息, 并写入列表
for level, count in session.query(Syslog.severity_level_name, func.count(Syslog.severity_level_name)).group_by(
        Syslog.severity_level_name).all():
    severity_level_name_list.append(level)
    severity_level_count_list.append(count)

# 发送SYSLOG设备的IP列表
device_ip_list = []

# 设备发送SYSLOG数量列表
device_log_count_list = []

# 数据库中找到发送SYSLOG设备的IP, 设备发送SYSLOG数量的信息, 并写入列表
for ip, count in session.query(Syslog.device_ip, func.count(Syslog.device_ip)).group_by(
        Syslog.device_ip).all():
    device_ip_list.append(ip)
    device_log_count_list.append(count)

# 保存严重级别分析图的文件名
severity_level_filename = 'severity_level'
# 保存主机分析图的文件名
device_ip_filename = 'device_ip'

# 拼接成为保存文件的绝对路径 (放到 outputs 目录下)
outputs_dir = os.path.join(current_dir, 'outputs')
os.makedirs(outputs_dir, exist_ok=True)
save_file_severity_level_file = os.path.join(outputs_dir, f"{severity_level_filename}.png")
save_file_device_ip_file = os.path.join(outputs_dir, f"{device_ip_filename}.png")

# 使用 Pygal 饼状图呈现，并获取 PNG 路径用于内嵌
pygal_pie(severity_level_name_list, severity_level_count_list, 'SYSLOG严重级别分布图', save_file_severity_level_file)
pygal_pie(device_ip_list, device_log_count_list, 'SYSLOG设备分布图', save_file_device_ip_file)

# 严重级别日志总数量
severity_total = sum(severity_level_count_list)

# 把严重级别名称列表、数量列表整理成 Jinja2 可直接渲染的列表
severity_level_count_html_list = []
for level, count in zip(severity_level_name_list, severity_level_count_list):
    percent = round(count / severity_total * 100, 2) if severity_total > 0 else 0
    severity_level_count_html_list.append({
        'name': level,
        'log_count': count,
        'percent': percent,
    })

# 设备发送日志总数量
device_log_total = sum(device_log_count_list)

# 把设备IP列表、日志数量列表整理成 Jinja2 可直接渲染的列表
device_ip_count_html_list = []
for ip, count in zip(device_ip_list, device_log_count_list):
    percent = round(count / device_log_total * 100, 2) if device_log_total > 0 else 0
    device_ip_count_html_list.append({
        'ip': ip,
        'log_count': count,
        'percent': percent,
    })

# 对jinja2模板进行替换, 产生邮件正文中的HTML部分
main_body_html = syslog_email_template.render(severity_level_count_html_list=severity_level_count_html_list,
                                              severity_level_filename=severity_level_filename,
                                              device_ip_count_html_list=device_ip_count_html_list,
                                              device_ip_filename=device_ip_filename)

# 发送HTML邮件 (带内嵌图片)
smtp_user = os.environ.get('SMTPUSER')
smtp_password = os.environ.get('SMTPPASS')
smtp_server = os.environ.get('SMTPSERVER')
smtp_from = os.environ.get('SMTPFROM')
smtp_to = os.environ.get('SMTPTo', '1975141437@qq.com')

qyt_smtp_img(smtp_server,
             smtp_user,
             smtp_password,
             smtp_from,
             smtp_to,
             '乾颐堂NetDevOps Syslog分析',
             main_body_html,
             [save_file_severity_level_file,
              save_file_device_ip_file])

# Pygal 生成的 PNG 饼状图通过 cid: 内嵌在邮件正文中
# 如果需要删除临时图片文件，可以取消下面代码的注释
# if os.path.exists(save_file_severity_level_file):
#     os.remove(save_file_severity_level_file)
#
# if os.path.exists(save_file_device_ip_file):
#     os.remove(save_file_device_ip_file)
