#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""Day 9 - 初始化测试设备清单"""

import os
import sys
import uuid

# crond 调度时当前工作目录不固定, 需要把 day9 代码目录加入搜索路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from day9_1_model import Device  # noqa: E402
from day9_1_model import Session  # noqa: E402


TEST_DEVICES = [
    {
        'device_name': 'C8Kv1',
        'ip': '10.10.1.200',
        'username': 'admin',
        'password': 'Cisc0123',
        'enable_password': 'Cisc0123',
        'transport': 'ssh',
    },
    {
        'device_name': 'C8Kv2',
        'ip': '10.10.1.201',
        'username': 'admin',
        'password': 'Cisc0123',
        'enable_password': 'Cisc0123',
        'transport': 'ssh',
    },
]


def seed_devices():
    """把 Day 9 验证所需的测试设备写入数据库。"""
    session = Session()

    try:
        for device_info in TEST_DEVICES:
            device_obj = session.query(Device).filter_by(ip=device_info['ip']).first()

            if device_obj is None:
                device_obj = Device(
                    id=uuid.uuid4().hex,
                    device_name=device_info['device_name'],
                    ip=device_info['ip'],
                    username=device_info['username'],
                    password=device_info['password'],
                    enable_password=device_info['enable_password'],
                    transport=device_info['transport'],
                )
                session.add(device_obj)
                print(f"[+] 新增设备: {device_info['device_name']} {device_info['ip']}")
            else:
                device_obj.device_name = device_info['device_name']
                device_obj.username = device_info['username']
                device_obj.password = device_info['password']
                device_obj.enable_password = device_info['enable_password']
                device_obj.transport = device_info['transport']
                print(f"[*] 更新设备: {device_info['device_name']} {device_info['ip']}")

        session.commit()
        print(f'[+] 共处理 {len(TEST_DEVICES)} 台测试设备')
    finally:
        session.close()


if __name__ == '__main__':
    seed_devices()
