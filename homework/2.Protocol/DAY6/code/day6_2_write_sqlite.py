#!/usr/bin/env python3
"""
任务2: 使用SNMP采集接口数据并写入SQLite数据库
支持多个设备、多个接口
通过Crond调度执行
"""
import sys
import os
import asyncio
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.day6_snmp_getbulk import snmpv2_getbulk
from day6_1_create_db import InternfaceMonitor, engine
from sqlalchemy.orm import sessionmaker

# SNMP配置 - 至少两个设备
DEVICE_LIST = [
    {'ip': '10.10.1.200', 'community': 'qytangro'},
    {'ip': '10.10.1.201', 'community': 'qytangro'},
]

# IF-MIB OID
OID_IF_DESCR = '1.3.6.1.2.1.2.2.1.2'      # 接口名称
OID_IF_IN_OCTETS = '1.3.6.1.2.1.2.2.1.10'  # 入向字节数
OID_IF_OUT_OCTETS = '1.3.6.1.2.1.2.2.1.16' # 出向字节数


async def collect_interface_data(device):
    """
    采集单个设备的接口数据
    返回：[(interface_name, in_bytes, out_bytes), ...]
    """
    ip = device['ip']
    community = device['community']
    
    try:
        # 批量获取接口名称
        descr_results = await snmpv2_getbulk(ip, community, OID_IF_DESCR, max_repetitions=25)
        
        # 批量获取入向字节数
        in_results = await snmpv2_getbulk(ip, community, OID_IF_IN_OCTETS, max_repetitions=25)
        
        # 批量获取出向字节数
        out_results = await snmpv2_getbulk(ip, community, OID_IF_OUT_OCTETS, max_repetitions=25)
        
        # 解析接口索引和名称的映射
        interfaces = {}
        for oid, value in descr_results:
            # 只处理ifDescr OID (1.3.6.1.2.1.2.2.1.2.X)
            # 检查OID是否以.2结尾或包含.2.1.2.2.1.2.
            if 'mib-2.2.2.1.2.' in oid or '.2.1.2.2.1.2.' in oid:
                parts = oid.split('.')
                if parts:
                    idx = parts[-1]
                    # 只保存第一次出现的（接口名称），避免被后续OID覆盖
                    if idx not in interfaces:
                        interfaces[idx] = {'name': value, 'in_bytes': 0, 'out_bytes': 0}
        
        # 解析入向字节数 (严格匹配 ifInOctets OID: mib-2.2.2.1.10.X)
        for oid, value in in_results:
            if 'mib-2.2.2.1.10.' in oid:
                idx = oid.split('.')[-1]
                if idx in interfaces:
                    interfaces[idx]['in_bytes'] = int(value)
        
        # 解析出向字节数 (严格匹配 ifOutOctets OID: mib-2.2.2.1.16.X)
        for oid, value in out_results:
            if 'mib-2.2.2.1.16.' in oid:
                idx = oid.split('.')[-1]
                if idx in interfaces:
                    interfaces[idx]['out_bytes'] = int(value)
        
        # 过滤掉没有名称的接口，只保留物理接口
        interface_data = []
        for idx, data in interfaces.items():
            if data['name'] and data['name'] not in ['NULL0', 'Virtual-Access1', 'Virtual-Template1']:
                interface_data.append((data['name'], data['in_bytes'], data['out_bytes']))
                print(f"[+] {ip} {data['name']:<35} IN={data['in_bytes']:>12}  OUT={data['out_bytes']:>12}")
        
        return interface_data
        
    except Exception as e:
        print(f"[!] {ip} 采集失败: {e}")
        return []


def write_to_sqlite(all_data):
    """
    将采集数据写入SQLite数据库
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    total_records = 0
    
    try:
        for device_ip, interface_data in all_data:
            for interface_name, in_bytes, out_bytes in interface_data:
                # 创建记录
                record = InternfaceMonitor(
                    device_ip=device_ip,
                    interface_name=interface_name,
                    in_bytes=in_bytes,
                    out_bytes=out_bytes,
                    record_datetime=datetime.now()
                )
                session.add(record)
                total_records += 1
        
        # 提交事务
        session.commit()
        print(f"[*] 共写入 {total_records} 条记录")
        
    except Exception as e:
        session.rollback()
        print(f"[!] 写入数据库失败: {e}")
    finally:
        session.close()


async def main():
    """主函数：并发采集所有设备接口数据并写入SQLite"""
    print(f"\n{'='*70}")
    print(f"SNMP接口数据采集开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    # 并发采集所有设备
    tasks = [collect_interface_data(device) for device in DEVICE_LIST]
    results = await asyncio.gather(*tasks)
    
    # 组合数据：[(device_ip, interface_data), ...]
    all_data = []
    for device, interface_data in zip(DEVICE_LIST, results):
        if interface_data:
            all_data.append((device['ip'], interface_data))
    
    # 写入SQLite
    if all_data:
        write_to_sqlite(all_data)
    else:
        print("[!] 没有采集到数据")
    
    print(f"{'='*70}\n")


if __name__ == '__main__':
    asyncio.run(main())
