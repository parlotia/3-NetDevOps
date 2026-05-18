import asyncio
from pysnmp.hlapi.v3arch.asyncio import *


async def snmpv2_get(ip, community, oid, port=161):
    """
    SNMPv2 GET 异步采集函数
    参数：
        ip: 设备IP地址
        community: SNMP 团体字（只读）
        oid: 要采集的OID
        port: SNMP 端口，默认161
    返回：(OID字符串, 解码后的值字符串)
    """
    # 执行 SNMP GET 操作
    error_indication, error_status, error_index, var_binds = await get_cmd(
        SnmpEngine(),
        CommunityData(community),  # 配置只读团体字
        await UdpTransportTarget.create((ip, port)),  # 配置目标地址和端口
        ContextData(),
        ObjectType(ObjectIdentity(oid))  # 指定要读取的OID
    )

    # 错误处理
    if error_indication:
        print(f"[!] SNMP 错误: {error_indication}")
    elif error_status:
        print(f"[!] SNMP 错误: {error_status} at {error_index and var_binds[int(error_index) - 1][0] or '?'}")
    else:
        # 获取第一个返回结果
        var_bind = var_binds[0]
        value = var_bind[1]
        
        # 处理字节类型的返回值（如系统描述）
        if isinstance(value, bytes):
            result_str = bytes.fromhex(value[2:].decode('utf-8')).decode('utf-8', errors='ignore')
        else:
            result_str = str(value)
        
        # 返回OID和值
        return var_bind[0].prettyPrint(), result_str

# 测试代码：运行此文件可直接测试SNMP连通性
if __name__ == "__main__":
    ip_address = "10.10.1.200"
    community = "qytangro"

    print("=== 测试SNMP采集 ===")
    print("系统描述:", asyncio.run(snmpv2_get(ip_address, community, "1.3.6.1.2.1.1.1.0")))
    print("CPU 5秒利用率:", asyncio.run(snmpv2_get(ip_address, community, "1.3.6.1.4.1.9.9.109.1.1.1.1.6.7")))
    print("已用内存:", asyncio.run(snmpv2_get(ip_address, community, "1.3.6.1.4.1.9.9.109.1.1.1.1.12.7")))
    print("空闲内存:", asyncio.run(snmpv2_get(ip_address, community, "1.3.6.1.4.1.9.9.109.1.1.1.1.13.7")))