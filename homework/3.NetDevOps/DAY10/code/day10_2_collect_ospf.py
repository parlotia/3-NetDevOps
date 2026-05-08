#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""
DAY10 - OSPF状态采集脚本
通过PYATS连接设备，学习OSPF状态和路由表信息，并写入SQLite数据库
"""

import os
import sys
import json
import io
from datetime import datetime

# 禁用 PYATS CLI 日志文件生成
os.environ['PYATS_LOGGING'] = 'CRITICAL'

from genie.testbed import load
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 导入数据库模型
from day10_1_create_db import PyatsOSPF, engine

# Guestshell默认ASCII编码, 需强制切换为UTF-8以支持中文输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 当前文件目录
current_dir = os.path.dirname(os.path.realpath(__file__))

# 加载testbed数据
testbed = load(f'{current_dir}{os.sep}device_info.yaml')


def collect_ospf_status(device_name, device_obj):
    """
    连接设备并采集OSPF状态和路由表信息
    
    Args:
        device_name: 设备名称 (如 'C8Kv1')
        device_obj: PYATS设备对象
    
    Returns:
        dict: 包含ospf_status和route_table_status的字典
    """
    print(f'[+] 正在连接设备: {device_name}')
    
    try:
        # 连接设备（PYATS 会自动处理 enable，只要在 testbed 中配置了 enable credentials）
        device_obj.connect(
            learn_hostname=True,
            log_stdout=False,
            ssh_options='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null',
            connection_timeout=30,
            init_exec=True,
            init_config=True
        )
        print(f'[+] 设备 {device_name} 连接成功')
        
        # 学习OSPF详细信息
        print(f'[+] 正在学习 {device_name} 的OSPF状态...')
        ospf_data = device_obj.learn('ospf').to_dict()
        
        # 学习路由表详细信息
        print(f'[+] 正在学习 {device_name} 的路由表...')
        route_data = device_obj.parse('show ip route')
        
        # 断开连接
        device_obj.disconnect()
        
        return {
            'ospf_status': ospf_data,
            'route_table_status': route_data
        }
        
    except Exception as e:
        print(f'[!] 采集 {device_name} 失败: {e}')
        return None


def save_to_database(device_name, device_ip, ospf_status, route_table_status):
    """
    将采集的数据保存到数据库
    
    Args:
        device_name: 设备名称
        device_ip: 设备IP
        ospf_status: OSPF状态字典
        route_table_status: 路由表状态字典
    """
    # 创建Session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 创建新记录
        record = PyatsOSPF(
            device_name=device_name,
            device_ip=device_ip,
            ospf_status=ospf_status,
            route_table_status=route_table_status
        )
        
        session.add(record)
        session.commit()
        print(f'[+] {device_name} 数据已保存到数据库')
        
    except Exception as e:
        session.rollback()
        print(f'[!] 保存 {device_name} 数据失败: {e}')
        
    finally:
        session.close()


def main():
    """主函数"""
    print('=' * 60)
    print('DAY10 - OSPF状态采集脚本')
    print(f'采集时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)
    
    # 设备列表
    devices = [
        {'name': 'C8Kv1', 'ip': '10.10.1.201'},
        {'name': 'C8Kv2', 'ip': '10.10.1.202'}
    ]
    
    for device_info in devices:
        device_name = device_info['name']
        device_ip = device_info['ip']
        
        # 获取设备对象
        device_obj = testbed.devices[device_name]
        
        # 采集OSPF状态
        result = collect_ospf_status(device_name, device_obj)
        
        if result:
            # 保存到数据库
            save_to_database(
                device_name=device_name,
                device_ip=device_ip,
                ospf_status=result['ospf_status'],
                route_table_status=result['route_table_status']
            )
        else:
            print(f'[!] 跳过 {device_name} 的数据保存')
        
        print('-' * 60)
    
    print('[+] 采集任务完成')


if __name__ == '__main__':
    main()
