"""
任务三: 使用RESTCONF配置SYSLOG (host与trap level)
YANG路径: Cisco-IOS-XE-native > native > logging
APIFOX 接口: PUT /restconf/data/Cisco-IOS-XE-native:native/logging
"""

import requests
import urllib3

# 禁用SSL证书警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def conf_syslog(device_ip, username, password, severity, hostip):
    """
    通过RESTCONF配置Cisco IOS-XE设备的SYSLOG (trap level与host)

    Args:
        device_ip (str): 设备IP地址
        username (str): RESTCONF用户名
        password (str): RESTCONF密码
        severity (int): trap severity级别 (0=emergencies ~ 7=debugging)
        hostip (str): SYSLOG服务器IP地址

    Returns:
        bool: 配置成功返回True, 失败返回False
    """
    url = f"https://{device_ip}/restconf/data/Cisco-IOS-XE-native:native/logging"
    headers = {
        'Content-Type': 'application/yang-data+json',
        'Accept': 'application/yang-data+json',
    }

    # 构造请求体 (与APIFOX中Body一致)
    payload = {
        "Cisco-IOS-XE-native:logging": {
            "trap": {
                "severity": severity
            },
            "hostip": hostip
        }
    }

    try:
        response = requests.put(
            url,
            auth=(username, password),
            headers=headers,
            json=payload,
            verify=False,
            timeout=30,
        )
        response.raise_for_status()

        # RESTCONF PUT成功通常返回 204 No Content
        if response.status_code == 204:
            print(f"[+] {device_ip} SYSLOG配置成功 (204 No Content):")
            print(f"    trap severity: {severity}")
            print(f"    syslog server: {hostip}")
            return True
        else:
            print(f"[+] {device_ip} SYSLOG配置成功 (状态码: {response.status_code}):")
            print(f"    trap severity: {severity}")
            print(f"    syslog server: {hostip}")
            if response.text:
                print(f"    响应内容: {response.text[:500]}")
            return True

    except requests.exceptions.HTTPError as e:
        print(f"[!] {device_ip} HTTP请求失败: {e}")
        print(f"    响应状态码: {response.status_code}")
        print(f"    响应内容: {response.text[:500]}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"[!] {device_ip} 连接失败: {e}")
        return False
    except Exception as e:
        print(f"[!] {device_ip} RESTCONF请求异常: {e}")
        return False


def verify_syslog(device_ip, username, password):
    """
    通过RESTCONF验证设备的SYSLOG配置

    Args:
        device_ip (str): 设备IP地址
        username (str): RESTCONF用户名
        password (str): RESTCONF密码

    Returns:
        dict: 包含severity和hostip信息, 失败返回None
    """
    url = f"https://{device_ip}/restconf/data/Cisco-IOS-XE-native:native/logging"
    headers = {
        'Accept': 'application/yang-data+json',
    }

    try:
        response = requests.get(
            url,
            auth=(username, password),
            headers=headers,
            verify=False,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()

        result = {}
        logging_data = data.get("Cisco-IOS-XE-native:logging", {})

        # 提取trap severity
        trap_data = logging_data.get("trap", {})
        if "severity" in trap_data:
            result['severity'] = trap_data["severity"]

        # 提取hostip
        if "hostip" in logging_data:
            result['hostip'] = logging_data["hostip"]

        if result:
            print(f"[+] {device_ip} 当前SYSLOG配置:")
            if 'severity' in result:
                print(f"    trap severity: {result['severity']}")
            if 'hostip' in result:
                print(f"    syslog server: {result['hostip']}")
            return result
        else:
            print(f"[-] {device_ip} 未找到SYSLOG配置")
            print(f"    原始响应: {data}")
            return None

    except requests.exceptions.HTTPError as e:
        print(f"[!] {device_ip} HTTP请求失败: {e}")
        print(f"    响应状态码: {response.status_code}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[!] {device_ip} 连接失败: {e}")
        return None
    except Exception as e:
        print(f"[!] {device_ip} RESTCONF请求异常: {e}")
        return None


if __name__ == '__main__':
    # 设备连接信息 (请根据实际情况修改)
    DEVICE_IP = '10.10.1.200'
    USERNAME = 'admin'
    PASSWORD = 'Cisc0123'
    # SYSLOG服务器地址 (请根据实际情况修改)
    SYSLOG_SERVER_IP = '10.10.1.205'
    # trap severity级别 (7=debugging, 请根据实际情况修改)
    SEVERITY = 7

    print("=" * 50)
    print("RESTCONF SYSLOG配置测试")
    print("=" * 50)

    # 1. 配置SYSLOG
    print("\n--- 配置SYSLOG ---")
    result = conf_syslog(DEVICE_IP, USERNAME, PASSWORD,
                         severity=SEVERITY, hostip=SYSLOG_SERVER_IP)
    print(f"    配置结果: {'成功' if result else '失败'}")

    # 2. 验证配置
    print("\n--- 验证SYSLOG配置 ---")
    verify_syslog(DEVICE_IP, USERNAME, PASSWORD)
