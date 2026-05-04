"""
任务二: 使用NETCONF获取CPU利用率
YANG路径: Cisco-IOS-XE-process-cpu-oper > cpu-usage > cpu-utilization
"""

from ncclient import manager
import xml.etree.ElementTree as ET

# YANG命名空间
CPU_OPER_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-process-cpu-oper"

# monitor_type 到 YANG叶子节点的映射
MONITOR_TYPE_MAP = {
    '5s': 'five-seconds',
    '1m': 'one-minute',
    '5m': 'five-minutes',
}


def monitor_cpu(device_ip, username, password, monitor_type='5s'):
    """
    通过NETCONF获取Cisco IOS-XE设备的CPU利用率

    Args:
        device_ip (str): 设备IP地址
        username (str): NETCONF用户名
        password (str): NETCONF密码
        monitor_type (str): 监控类型, '5s'=5秒, '1m'=1分钟, '5m'=5分钟

    Returns:
        int: CPU利用率百分比(0-255), 失败返回None
    """
    if monitor_type not in MONITOR_TYPE_MAP:
        print(f"[!] 不支持的monitor_type: {monitor_type}, 支持: {list(MONITOR_TYPE_MAP.keys())}")
        return None

    yang_leaf = MONITOR_TYPE_MAP[monitor_type]

    # 构造NETCONF <get> RPC的filter
    filter_xml = f"""
    <cpu-usage xmlns="{CPU_OPER_NS}">
      <cpu-utilization>
        <{yang_leaf}/>
      </cpu-utilization>
    </cpu-usage>
    """

    try:
        with manager.connect(
            host=device_ip,
            port=830,
            username=username,
            password=password,
            hostkey_verify=False,
            device_params={'name': 'iosxe'},
            timeout=30,
        ) as m:
            reply = m.get(filter=("subtree", filter_xml))

            # 解析XML响应
            root = ET.fromstring(str(reply))
            ns = {'ns': CPU_OPER_NS}

            # 查找CPU利用率节点
            cpu_node = root.find(f".//ns:cpu-utilization/ns:{yang_leaf}", namespaces=ns)

            if cpu_node is not None and cpu_node.text is not None:
                cpu_value = int(cpu_node.text)
                print(f"[+] {device_ip} CPU利用率({monitor_type}): {cpu_value}%")
                return cpu_value
            else:
                print(f"[-] {device_ip} 未找到CPU利用率数据({monitor_type})")
                # 调试: 打印原始响应
                print(f"    原始响应: {str(reply)[:500]}")
                return None

    except Exception as e:
        print(f"[!] {device_ip} NETCONF连接或获取失败: {e}")
        return None


if __name__ == '__main__':
    # 设备连接信息
    DEVICE_IP = '10.10.1.200'
    USERNAME = 'admin'
    PASSWORD = 'Cisc0123'

    print("=" * 50)
    print("NETCONF CPU利用率采集测试")
    print("=" * 50)

    # 测试三种监控类型
    for m_type in ['5s', '1m', '5m']:
        result = monitor_cpu(DEVICE_IP, USERNAME, PASSWORD, monitor_type=m_type)
        if result is not None:
            print(f"    -> {m_type} CPU利用率: {result}%")
        print()
