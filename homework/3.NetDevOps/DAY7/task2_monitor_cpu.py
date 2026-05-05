"""
任务二: 使用RESTCONF获取CPU利用率
YANG路径: Cisco-IOS-XE-process-cpu-oper > cpu-usage > cpu-utilization
APIFOX 接口: GET /restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization/five-seconds
"""

import requests
import urllib3

# 禁用SSL证书警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# monitor_type 到 RESTCONF URL路径的映射
MONITOR_TYPE_MAP = {
    '5s': 'five-seconds',
    '1m': 'one-minute',
    '5m': 'five-minutes',
}


def monitor_cpu(device_ip, username, password, monitor_type='5s'):
    """
    通过RESTCONF获取Cisco IOS-XE设备的CPU利用率

    Args:
        device_ip (str): 设备IP地址
        username (str): RESTCONF用户名
        password (str): RESTCONF密码
        monitor_type (str): 监控类型, '5s'=5秒, '1m'=1分钟, '5m'=5分钟

    Returns:
        int/float: CPU利用率百分比, 失败返回None
    """
    if monitor_type not in MONITOR_TYPE_MAP:
        print(f"[!] 不支持的monitor_type: {monitor_type}, 支持: {list(MONITOR_TYPE_MAP.keys())}")
        return None

    yang_leaf = MONITOR_TYPE_MAP[monitor_type]
    url = f"https://{device_ip}/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization/{yang_leaf}"
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

        # 从JSON响应中提取CPU利用率值
        # 响应格式: {"Cisco-IOS-XE-process-cpu-oper:five-seconds": 0}
        key = f"Cisco-IOS-XE-process-cpu-oper:{yang_leaf}"
        cpu_value = data.get(key)

        if cpu_value is not None:
            print(f"[+] {device_ip} CPU利用率({monitor_type}): {cpu_value}%")
            return cpu_value
        else:
            print(f"[-] {device_ip} 未找到CPU利用率数据({monitor_type})")
            print(f"    原始响应: {data}")
            return None

    except requests.exceptions.HTTPError as e:
        print(f"[!] {device_ip} HTTP请求失败: {e}")
        print(f"    响应状态码: {response.status_code}")
        print(f"    响应内容: {response.text[:500]}")
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

    print("=" * 50)
    print("RESTCONF CPU利用率采集测试")
    print("=" * 50)

    # 测试三种监控类型
    for m_type in ['5s', '1m', '5m']:
        result = monitor_cpu(DEVICE_IP, USERNAME, PASSWORD, monitor_type=m_type)
        if result is not None:
            print(f"    -> {m_type} CPU利用率: {result}%")
        print()
