#!/usr/bin/env python3
"""
SNMP采集路由器CPU和内存信息，写入InfluxDB
用于Crond定时调度
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from influxdb import InfluxDBClient

# 添加项目路径到Python模块搜索路径
BASE_DIR = Path(__file__).resolve().parent.parent / 'DAY4'
sys.path.insert(0, str(BASE_DIR))

# 导入DAY4的SNMP采集函数
from get import snmpv2_get

# InfluxDB连接配置
INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_USER = 'qytdbuser'
INFLUXDB_PASSWORD = 'Cisc0123'
INFLUXDB_DB = 'qytdb'

# SNMP配置
DEVICE_LIST = [
    {'ip': '10.10.1.200', 'community': 'qytangro'},
    {'ip': '10.10.1.201', 'community': 'qytangro'},
]

# 思科设备OID
OID_CPU = '1.3.6.1.4.1.9.9.109.1.1.1.1.6.7'
OID_MEM_USE = '1.3.6.1.4.1.9.9.109.1.1.1.1.12.7'
OID_MEM_FREE = '1.3.6.1.4.1.9.9.109.1.1.1.1.13.7'


async def collect_device_data(device):
    """
    采集单台设备的SNMP数据
    返回：设备数据字典
    """
    ip = device['ip']
    community = device['community']
    
    try:
        # 采集CPU利用率
        _, cpu_str = await snmpv2_get(ip, community, OID_CPU)
        cpu = int(cpu_str) if cpu_str and cpu_str.isdigit() else 0
        
        # 采集内存信息
        _, mem_use_str = await snmpv2_get(ip, community, OID_MEM_USE)
        _, mem_free_str = await snmpv2_get(ip, community, OID_MEM_FREE)
        
        mem_use = int(mem_use_str) if mem_use_str and mem_use_str.isdigit() else 0
        mem_free = int(mem_free_str) if mem_free_str and mem_free_str.isdigit() else 0
        
        # 计算内存利用率
        total_mem = mem_use + mem_free
        mem_percent = round((mem_use / total_mem * 100), 2) if total_mem > 0 else 0
        
        print(f"[+] {ip}: CPU={cpu}%, MEM={mem_percent}%")
        
        return {
            'ip': ip,
            'cpu': cpu,
            'mem_use': mem_use,
            'mem_free': mem_free,
            'mem_percent': mem_percent,
            'success': True
        }
        
    except Exception as e:
        print(f"[!] {ip} 采集失败: {e}")
        return {
            'ip': ip,
            'success': False
        }


def write_to_influxdb(data_list):
    """
    将采集数据写入InfluxDB
    """
    try:
        # 创建InfluxDB客户端
        client = InfluxDBClient(
            host=INFLUXDB_HOST,
            port=INFLUXDB_PORT,
            username=INFLUXDB_USER,
            password=INFLUXDB_PASSWORD,
            database=INFLUXDB_DB
        )
        
        # 构建写入数据
        json_body = []
        for data in data_list:
            if not data.get('success'):
                continue
                
            point = {
                "measurement": "router_monitor",
                "tags": {
                    "device_ip": data['ip']
                },
                "fields": {
                    "cpu_percent": data['cpu'],
                    "mem_use": data['mem_use'],
                    "mem_free": data['mem_free'],
                    "mem_percent": data['mem_percent']
                }
            }
            json_body.append(point)
        
        if json_body:
            # 写入InfluxDB
            client.write_points(json_body)
            print(f"[*] 成功写入 {len(json_body)} 条数据到 InfluxDB")
        else:
            print("[!] 没有成功采集的数据")
            
    except Exception as e:
        print(f"[!] 写入InfluxDB失败: {e}")


async def main():
    """主函数：并发采集所有设备数据并写入InfluxDB"""
    print(f"\n{'='*60}")
    print(f"SNMP采集开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 并发采集所有设备
    tasks = [collect_device_data(device) for device in DEVICE_LIST]
    results = await asyncio.gather(*tasks)
    
    # 写入InfluxDB
    write_to_influxdb(results)
    
    print(f"{'='*60}\n")


if __name__ == '__main__':
    asyncio.run(main())
