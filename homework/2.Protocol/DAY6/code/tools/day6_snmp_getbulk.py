#!/usr/bin/env python3
"""
SNMP GETBULK 批量采集工具
用于批量获取接口数据
"""
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *


async def snmpv2_getbulk(ip, community, oid, max_repetitions=25, port=161):
    """
    SNMPv2 GETBULK 异步批量采集函数
    参数：
        ip: 设备IP地址
        community: SNMP 团体字
        oid: 要采集的OID（表格起始OID）
        max_repetitions: 最大重复次数（接口数量）
        port: SNMP 端口，默认161
    返回：[(OID字符串, 值字符串), ...]
    """
    error_indication, error_status, error_index, var_bind_table = await bulk_cmd(
        SnmpEngine(),
        CommunityData(community),
        await UdpTransportTarget.create((ip, port)),
        ContextData(),
        0,  # non-repeaters
        max_repetitions,
        ObjectType(ObjectIdentity(oid))
    )

    if error_indication:
        print(f"[!] SNMP 错误: {error_indication}")
        return []
    elif error_status:
        print(f"[!] SNMP 错误: {error_status}")
        return []
    else:
        results = []
        # pysnmp v7 的 bulk_cmd 返回扁平的 var_bind_table
        # 每个元素直接是 ObjectType 对象
        for var_bind in var_bind_table:
            if isinstance(var_bind, ObjectType):
                oid_obj = var_bind[0]
                value = var_bind[1]
                
                # 获取OID字符串
                if hasattr(oid_obj, 'prettyPrint'):
                    oid_str = oid_obj.prettyPrint()
                else:
                    oid_str = str(oid_obj)
                
                # 处理不同类型的返回值
                if hasattr(value, 'prettyPrint'):
                    value_str = value.prettyPrint()
                elif isinstance(value, bytes):
                    try:
                        value_str = bytes.fromhex(value[2:].decode('utf-8')).decode('utf-8', errors='ignore')
                    except:
                        value_str = str(value)
                else:
                    value_str = str(value)
                
                # 对于接口名称，从完整OID中提取
                # OID: 1.3.6.1.2.1.2.2.1.2.X -> 应该返回 GigabitEthernetX
                if '1.3.6.1.2.1.2.2.1.2' in oid_str and value_str.isdigit():
                    # 这是接口索引，需要从另一个OID获取名称
                    pass
                
                results.append((oid_str, value_str))
        
        return results


if __name__ == "__main__":
    # 测试代码
    ip_address = "10.10.1.200"
    community = "qytangro"
    
    # 测试获取接口名称
    print("=== 测试SNMP GETBULK采集接口数据 ===")
    print("获取接口名称 (ifDescr):")
    results = asyncio.run(snmpv2_getbulk(ip_address, community, "1.3.6.1.2.1.2.2.1.2"))
    for oid, value in results[:5]:  # 只显示前5个
        print(f"  {oid} = {value}")
