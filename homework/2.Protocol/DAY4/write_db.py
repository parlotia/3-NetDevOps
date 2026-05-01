import sys
import asyncio
from pathlib import Path

# 【关键】把当前脚本所在目录加入Python搜索路径，确保Crond能正确导入模块
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 导入工具函数
from get import snmpv2_get
from create_db import RouterMonitor, Session

# 思科设备关键OID（和你测试代码完全一致）
OID_CPU = '1.3.6.1.4.1.9.9.109.1.1.1.1.6.7'    # CPU 5秒平均利用率
OID_MEM_USE = '1.3.6.1.4.1.9.9.109.1.1.1.1.12.7' # 已用内存（字节）
OID_MEM_FREE = '1.3.6.1.4.1.9.9.109.1.1.1.1.13.7' # 空闲内存（字节）

# 【关键修改】设备列表：添加两台路由器进行对比
DEVICE_LIST = [
    {'ip': '10.10.1.200', 'community': 'qytangro'},  # 第一台设备
    {'ip': '10.10.1.201', 'community': 'qytangro'},  # 第二台设备（改成你实际的IP）
]


async def collect_and_save(device):
    """
    采集单台设备的数据并写入数据库
    参数：device: 字典，包含ip和community
    返回：True=成功，False=失败
    """
    ip = device['ip']
    community = device['community']

    try:
        # 1. 调用SNMP函数采集数据
        _, cpu_str = await snmpv2_get(ip, community, OID_CPU)
        _, mem_use_str = await snmpv2_get(ip, community, OID_MEM_USE)
        _, mem_free_str = await snmpv2_get(ip, community, OID_MEM_FREE)

        # 2. 安全转换数据类型：处理None和非数字情况
        cpu = int(cpu_str) if cpu_str and cpu_str.isdigit() else 0
        mem_use = int(mem_use_str) if mem_use_str and mem_use_str.isdigit() else 0
        mem_free = int(mem_free_str) if mem_free_str and mem_free_str.isdigit() else 0

        # 3. 打印采集结果
        print(f"[+] 设备{ip}: CPU={cpu}%, MEM_Used={mem_use}, MEM_Free={mem_free}")

        # 4. 写入数据库
        with Session() as session:
            # 创建记录对象
            record = RouterMonitor(
                device_ip=ip,
                cpu_useage_percent=cpu,
                mem_use=mem_use,
                mem_free=mem_free
            )
            # 添加到会话
            session.add(record)
            # 提交事务
            session.commit()

        return True

    except Exception as e:
        print(f"[!] 设备{ip}采集失败: {e}")
        return False


async def main():
    """主函数：并发采集所有设备的数据"""
    # 创建所有采集任务
    tasks = [collect_and_save(device) for device in DEVICE_LIST]
    # 等待所有任务完成
    results = await asyncio.gather(*tasks)
    
    # 统计成功写入的记录数
    success_count = sum(results)
    print(f"[*] 共写入 {success_count} 条记录")


if __name__ == '__main__':
    asyncio.run(main())