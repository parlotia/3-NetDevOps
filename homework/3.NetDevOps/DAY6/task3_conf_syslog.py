"""
任务三: 使用NETCONF配置SYSLOG (host与trap level)
YANG路径: Cisco-IOS-XE-native > native > logging

注意: 此设备的edit_config方法存在YANG校验问题,
需使用dispatch + lxml构建XML节点的方式发送edit-config RPC
"""

from ncclient import manager
from ncclient.xml_ import new_ele, sub_ele
from lxml import etree
import xml.etree.ElementTree as ET

# YANG命名空间
NATIVE_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-native"
NATIVE_NS_FULL = f"{{{NATIVE_NS}}}"  # lxml格式: {namespace}

# severity级别映射 (数字 -> YANG枚举字符串)
SEVERITY_MAP = {
    0: 'emergencies',
    1: 'alerts',
    2: 'critical',
    3: 'errors',
    4: 'warnings',
    5: 'notifications',
    6: 'informational',
    7: 'debugging',
}


def conf_syslog(device_ip, username, password, severity, hostip):
    """
    通过NETCONF配置Cisco IOS-XE设备的SYSLOG (trap level与host)

    Args:
        device_ip (str): 设备IP地址
        username (str): NETCONF用户名
        password (str): NETCONF密码
        severity (int): trap severity级别 (0=emergencies ~ 7=debugging)
        hostip (str): SYSLOG服务器IP地址

    Returns:
        bool: 配置成功返回True, 失败返回False
    """
    if severity not in SEVERITY_MAP:
        print(f"[!] 不支持的severity: {severity}, 支持: 0-7")
        return False

    sev_name = SEVERITY_MAP[severity]

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
            # 使用dispatch + lxml构建edit-config RPC
            # (直接使用edit_config在此设备上会触发YANG校验错误)
            edit_config_node = new_ele('edit-config')
            sub_ele(edit_config_node, 'target').append(new_ele('running'))
            config_node = sub_ele(edit_config_node, 'config')

            # native > logging
            native_node = etree.SubElement(config_node, f"{NATIVE_NS_FULL}native")
            logging_node = etree.SubElement(native_node, f"{NATIVE_NS_FULL}logging")

            # logging > trap > severity
            trap_node = etree.SubElement(logging_node, f"{NATIVE_NS_FULL}trap")
            severity_node = etree.SubElement(trap_node, f"{NATIVE_NS_FULL}severity")
            severity_node.text = sev_name

            # logging > host > ipv4-host-list > ipv4-host
            host_node = etree.SubElement(logging_node, f"{NATIVE_NS_FULL}host")
            ipv4_list_node = etree.SubElement(host_node, f"{NATIVE_NS_FULL}ipv4-host-list")
            ipv4_host_node = etree.SubElement(ipv4_list_node, f"{NATIVE_NS_FULL}ipv4-host")
            ipv4_host_node.text = hostip

            reply = m.dispatch(edit_config_node)

            if "<ok/>" in str(reply):
                print(f"[+] {device_ip} SYSLOG配置成功:")
                print(f"    trap severity: {severity} ({sev_name})")
                print(f"    syslog server: {hostip}")
                return True
            else:
                print(f"[-] {device_ip} SYSLOG配置可能失败")
                print(f"    响应: {str(reply)[:500]}")
                return False

    except Exception as e:
        print(f"[!] {device_ip} NETCONF连接或配置失败: {e}")
        return False


def verify_syslog(device_ip, username, password):
    """
    通过NETCONF验证设备的SYSLOG配置

    Args:
        device_ip (str): 设备IP地址
        username (str): NETCONF用户名
        password (str): NETCONF密码

    Returns:
        dict: 包含severity和hostip信息, 失败返回None
    """
    filter_xml = f"""
    <native xmlns="{NATIVE_NS}">
      <logging/>
    </native>
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
            root = ET.fromstring(str(reply))
            ns = {'ns': NATIVE_NS}

            result = {}

            # 提取severity
            sev_node = root.find(".//ns:trap/ns:severity", namespaces=ns)
            if sev_node is not None and sev_node.text is not None:
                result['severity_str'] = sev_node.text
                # 反查数字级别
                for num, name in SEVERITY_MAP.items():
                    if name == sev_node.text:
                        result['severity'] = num
                        break

            # 提取hostip (简写字段)
            host_node = root.find(".//ns:logging/ns:hostip", namespaces=ns)
            if host_node is not None and host_node.text is not None:
                result['hostip'] = host_node.text

            # 也提取ipv4-host-list
            ipv4_node = root.find(".//ns:ipv4-host", namespaces=ns)
            if ipv4_node is not None and ipv4_node.text is not None:
                result['ipv4_host'] = ipv4_node.text

            if result:
                print(f"[+] {device_ip} 当前SYSLOG配置:")
                if 'severity' in result:
                    print(f"    trap severity: {result['severity']} ({result.get('severity_str', '')})")
                if 'hostip' in result:
                    print(f"    syslog server: {result['hostip']}")
                return result
            else:
                print(f"[-] {device_ip} 未找到SYSLOG配置")
                print(f"    原始响应: {str(reply)[:500]}")
                return None

    except Exception as e:
        print(f"[!] {device_ip} NETCONF连接或查询失败: {e}")
        return None


if __name__ == '__main__':
    # 设备连接信息
    DEVICE_IP = '10.10.1.200'
    USERNAME = 'admin'
    PASSWORD = 'Cisc0123'
    # SYSLOG服务器地址 (本机)
    SYSLOG_SERVER_IP = '10.10.1.205'
    # trap severity级别 (7=debug)
    SEVERITY = 7

    print("=" * 50)
    print("NETCONF SYSLOG配置测试")
    print("=" * 50)

    # 1. 配置SYSLOG
    print("\n--- 配置SYSLOG ---")
    result = conf_syslog(DEVICE_IP, USERNAME, PASSWORD,
                         severity=SEVERITY, hostip=SYSLOG_SERVER_IP)
    print(f"    配置结果: {'成功' if result else '失败'}")

    # 2. 验证配置
    print("\n--- 验证SYSLOG配置 ---")
    verify_syslog(DEVICE_IP, USERNAME, PASSWORD)
