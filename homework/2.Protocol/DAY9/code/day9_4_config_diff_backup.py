#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""Day 9 - 获取路由器配置、备份配置、比较异常邮件通知"""

import asyncio
import hashlib
import os
import re
import sys
import uuid

# crond 调度时当前工作目录不固定, 需要把当前目录加入搜索路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from day9_1_model import ConfigBackup  # noqa: E402
from day9_1_model import Device  # noqa: E402
from day9_1_model import Session  # noqa: E402
from tools.diff_config import diff_txt  # noqa: E402
from tools.smtp_send_mail_attachment import qyt_smtp_attachment  # noqa: E402
from tools.ssh_client_netmiko import netmiko_show_cred  # noqa: E402


SHOW_COMMAND = 'show run'


def normalize_config(config_text):
    """提取 hostname 行及其以下的配置内容。"""
    match = re.search(r'(?:^|\n)(hostname\s+\S+\n.*)$', config_text, re.S)

    if match:
        return match.group(1).strip()

    return config_text.strip()


def calculate_md5(config_text):
    """计算配置文本的 MD5 值。"""
    md5_obj = hashlib.md5()
    md5_obj.update(config_text.encode('utf-8'))
    return md5_obj.hexdigest()


def load_mail_config():
    """从环境变量中加载 SMTP 配置。"""
    from_mail = os.getenv('SMTPFROM', '')
    return {
        'mailserver': os.getenv('SMTPSERVER', ''),
        'username': os.getenv('SMTPUSER', ''),
        'password': os.getenv('SMTPPASS', ''),
        'from_mail': from_mail,
        'to_mail': '1975141437@qq.com',
    }


def mail_config_ready(mail_config):
    """检查 SMTP 配置是否完整。"""
    return all(mail_config.values())


async def async_netmiko_show(task_id, device_obj, cmd):
    """在线程池中异步执行 Netmiko show 命令。"""
    loop = asyncio.get_running_loop()
    print(f'[*] 任务 {task_id} 开始采集 {device_obj.device_name} {device_obj.ip}')

    result = await loop.run_in_executor(
        None,
        netmiko_show_cred,
        device_obj.ip,
        device_obj.username,
        device_obj.password,
        cmd,
        device_obj.enable_password,
        device_obj.transport == 'ssh',
    )

    print(f'[*] 任务 {task_id} 完成采集 {device_obj.device_name} {device_obj.ip}')
    return device_obj, result


async def collect_all_configs(device_list, cmd):
    """并发采集所有设备的配置。"""
    tasks = []

    for task_id, device_obj in enumerate(device_list, start=1):
        tasks.append(asyncio.create_task(async_netmiko_show(task_id, device_obj, cmd)))

    return await asyncio.gather(*tasks)


def send_diff_alert(device_obj, last_backup, current_config, mail_config):
    """当配置发生变化时发送差异邮件。"""
    if not mail_config_ready(mail_config):
        print(f'[~] {device_obj.ip} 配置已变化, 但未配置 SMTP 环境变量, 跳过发信')
        return

    diff_result = diff_txt(last_backup.config_text, current_config)
    subject = f'设备 {device_obj.device_name}({device_obj.ip}) 配置发生变化'

    qyt_smtp_attachment(
        mail_config['mailserver'],
        mail_config['username'],
        mail_config['password'],
        mail_config['from_mail'],
        mail_config['to_mail'],
        subject,
        diff_result,
    )


def save_backup(session, device_obj, config_text, config_md5):
    """把本次配置备份写入数据库。"""
    backup_obj = ConfigBackup(
        id=uuid.uuid4().hex,
        device_id=device_obj.id,
        config_text=config_text,
        config_md5=config_md5,
    )
    session.add(backup_obj)
    session.commit()


def process_backup_results(session, collected_results, mail_config):
    """处理采集结果, 执行差异比较、邮件告警和入库。"""
    changed_count = 0
    saved_count = 0

    for device_obj, raw_result in collected_results:
        if raw_result is None:
            print(f'[-] {device_obj.ip} 采集失败, 本次跳过入库')
            continue

        device_config_raw, host = raw_result
        device_config = normalize_config(device_config_raw)
        md5_value = calculate_md5(device_config)

        last_backup = (
            session.query(ConfigBackup)
            .filter_by(device_id=device_obj.id)
            .order_by(ConfigBackup.backup_time.desc(), ConfigBackup.id.desc())
            .first()
        )

        if last_backup is None:
            print(f'[+] {host} 首次备份配置')
        elif last_backup.config_md5 != md5_value:
            changed_count += 1
            print(f'[!] {host} 配置发生变化, 准备发送告警')
            send_diff_alert(device_obj, last_backup, device_config, mail_config)
        else:
            print(f'[*] {host} 配置未发生变化')

        save_backup(session, device_obj, device_config, md5_value)
        saved_count += 1

    return changed_count, saved_count


def run_backup_workflow():
    """执行 Day 9 配置备份与差异检测工作流。"""
    session = Session()
    mail_config = load_mail_config()

    try:
        # ★★★★★★ 请在这里查询设备清单, 按设备名称排序 ★★★★★★
        device_list = session.query(Device).order_by(Device.device_name).all()

        # ★★★★★★ 请在这里判断设备清单是否为空, 为空则提示并退出 ★★★★★★
        if not device_list:
            print('[-] 数据库中没有任何设备, 请先运行 day9_3_seed_devices.py 初始化设备清单')
            return

        # ★★★★★★ 请在这里补齐主流程: 打印设备数量、并发采集配置、处理比对结果、输出汇总信息 ★★★★★★
        print(f'[*] 本次共需要采集 {len(device_list)} 台设备')
        collected_results = asyncio.run(collect_all_configs(device_list, SHOW_COMMAND))
        changed_count, saved_count = process_backup_results(session, collected_results, mail_config)
        print(f'[+] 本次完成 {saved_count} 台设备备份, 配置变化 {changed_count} 台')
    finally:
        session.close()


if __name__ == '__main__':
    run_backup_workflow()
