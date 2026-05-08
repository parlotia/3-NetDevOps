#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""
DAY10 - OSPF状态比较与邮件告警脚本
比较最近两次采集的OSPF状态，如果有差异则发送邮件告警
"""

import os
import sys
import io
from datetime import datetime

from genie.utils.diff import Diff
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 导入数据库模型
from day10_1_create_db import PyatsOSPF, engine

# Guestshell默认ASCII编码, 需强制切换为UTF-8以支持中文输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 邮件配置
MAIL_SERVER = 'smtp.qq.com'
MAIL_USER = '1975141437@qq.com'
MAIL_PASS = 'avpjlsuqzmwydjij'  # QQ邮箱授权码
MAIL_FROM = '1975141437@qq.com'
MAIL_TO = ['1975141437@qq.com']

# 比较中需要被排除的项目
exclude_list = ['(.*age.*)',
                '(.*checksum.*)',
                '(.*seq_num.*)',
                '(.*length.*)',
                '(.*hello_timer.*)',
                '(.*dead_timer.*)',
                '(.*area_scope_lsa_cksum_sum.*)']


def send_email(subject, body):
    """
    发送邮件
    
    Args:
        subject: 邮件主题
        body: 邮件正文
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = MAIL_FROM
        msg['To'] = ', '.join(MAIL_TO)
        msg['Subject'] = subject
        
        # 添加正文
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 连接SMTP服务器并发送
        server = smtplib.SMTP_SSL(MAIL_SERVER, 465)
        server.login(MAIL_USER, MAIL_PASS)
        server.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())
        server.quit()
        
        print(f'[+] 邮件发送成功: {subject}')
        return True
        
    except Exception as e:
        print(f'[!] 邮件发送失败: {e}')
        return False


def get_latest_two_records(device_name):
    """
    获取指定设备最近两条OSPF记录
    
    Args:
        device_name: 设备名称
    
    Returns:
        tuple: (最新记录, 次新记录) 或 None
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        records = session.query(PyatsOSPF).filter(
            PyatsOSPF.device_name == device_name
        ).order_by(PyatsOSPF.record_datetime.desc()).limit(2).all()
        
        if len(records) >= 2:
            return records[0], records[1]
        else:
            print(f'[!] {device_name} 记录不足2条，无法比较')
            return None
            
    except Exception as e:
        print(f'[!] 查询 {device_name} 记录失败: {e}')
        return None
        
    finally:
        session.close()


def compare_ospf_status(device_name, latest, previous):
    """
    比较两次OSPF状态
    
    Args:
        device_name: 设备名称
        latest: 最新记录
        previous: 次新记录
    
    Returns:
        str: 差异文本，如果没有差异返回None
    """
    try:
        # 使用Genie Diff比较
        diff = Diff(latest.ospf_status, previous.ospf_status, exclude=exclude_list)
        diff.findDiff()
        
        if diff:
            # 有差异，生成差异文本
            diff_text = str(diff)
            return diff_text
        else:
            print(f'[+] {device_name} OSPF状态无变化')
            return None
            
    except Exception as e:
        print(f'[!] 比较 {device_name} OSPF状态失败: {e}')
        return None


def main():
    """主函数"""
    print('=' * 60)
    print('DAY10 - OSPF状态比较与邮件告警脚本')
    print(f'执行时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)
    
    # 设备列表
    devices = ['C8Kv1', 'C8Kv2']
    
    alert_count = 0
    
    for device_name in devices:
        print(f'\n[+] 正在检查 {device_name}...')
        
        # 获取最近两条记录
        records = get_latest_two_records(device_name)
        
        if records is None:
            continue
        
        latest, previous = records
        
        # 比较OSPF状态
        diff_text = compare_ospf_status(device_name, latest, previous)
        
        if diff_text:
            # 有差异，发送邮件告警
            subject = f'{device_name}-OSPF 状态改变'
            body = f'''info:
{diff_text}
'''
            if send_email(subject, body):
                alert_count += 1
                print(f'[+] {device_name} 告警邮件已发送')
            else:
                print(f'[!] {device_name} 告警邮件发送失败')
        else:
            print(f'[+] {device_name} 无需告警')
    
    print('\n' + '=' * 60)
    print(f'[+] 检查完成，共发送 {alert_count} 封告警邮件')
    print('=' * 60)


if __name__ == '__main__':
    main()
