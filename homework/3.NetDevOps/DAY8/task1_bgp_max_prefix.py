"""
=================================================================
NetDevOps DAY8 任务一: 配置BGP邻居与maximum-prefix阈值
=================================================================
场景: 两台C8KV路由器建立eBGP邻居关系, 当R1收到的前缀数量
      达到maximum-prefix阈值时, IOS-XE产生%BGP-4-MAXPFX SYSLOG日志

环境信息:
  R1 (C8KV-1): 10.10.1.200  AS 65001  配置maximum-prefix
  R2 (C8KV-2): 10.10.1.201  AS 65002  发布多个前缀触发告警
  Linux主机:   10.10.1.205

BGP规划:
  R1: network 1.1.1.0/24 (Loopback0: 1.1.1.1/24)
      neighbor 10.10.1.201 remote-as 65002
      neighbor 10.10.1.201 ebgp-multihop 255
      neighbor 10.10.1.201 maximum-prefix 2 warning-only

  R2: network 2.2.2.0/24 (Loopback0: 2.2.2.2/24)
      network 22.2.2.0/24 (Loopback1: 22.2.2.2/24)
      neighbor 10.10.1.200 remote-as 65001
      neighbor 10.10.1.200 ebgp-multihop 255

触发日志格式:
  %BGP-4-MAXPFX: Number of prefixes received from 10.10.1.201
  reaches <当前前缀数量>, max 2

配置方式: RESTCONF (Cisco-IOS-XE-native YANG模型)
=================================================================
"""

import requests
import urllib3
import time
import json

# 禁用SSL证书警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== 设备信息 ====================
R1_IP = '10.10.1.200'       # C8KV-1
R2_IP = '10.10.1.201'       # C8KV-2
USERNAME = 'admin'
PASSWORD = 'Cisc0123'

# BGP参数
R1_ASN = 65001
R2_ASN = 65002
MAX_PREFIX_LIMIT = 2         # maximum-prefix阈值

# RESTCONF通用Headers
HEADERS = {
    'Content-Type': 'application/yang-data+json',
    'Accept': 'application/yang-data+json',
}


# ==================== RESTCONF工具函数 ====================

def restconf_request(device_ip, method, path, payload=None):
    """
    发送RESTCONF请求的通用函数

    Args:
        device_ip: 设备IP地址
        method: HTTP方法 ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')
        path: RESTCONF数据路径 (不包含 /restconf/data/ 前缀)
        payload: 请求体 (dict, 仅用于POST/PUT/PATCH)

    Returns:
        成功返回响应数据(dict)或True, 失败返回None或False
    """
    url = f"https://{device_ip}/restconf/data/{path}"
    try:
        kwargs = {
            'auth': (USERNAME, PASSWORD),
            'headers': HEADERS if payload else {'Accept': 'application/yang-data+json'},
            'verify': False,
            'timeout': 30,
        }
        if payload:
            kwargs['json'] = payload

        response = getattr(requests, method.lower())(url, **kwargs)

        # 204 No Content 表示操作成功但无返回内容
        if response.status_code == 204:
            print(f"[+] {device_ip} RESTCONF {method}成功 (204 No Content)")
            return True if method != 'GET' else None

        # 200 OK
        if response.status_code == 200:
            if method == 'GET':
                try:
                    return response.json()
                except json.JSONDecodeError:
                    print(f"[-] {device_ip} 响应非JSON格式")
                    return None
            else:
                print(f"[+] {device_ip} RESTCONF {method}成功 (200)")
                return True

        # 201 Created
        if response.status_code == 201:
            print(f"[+] {device_ip} RESTCONF {method}成功 (201 Created)")
            return True

        # 错误处理
        print(f"[-] {device_ip} RESTCONF {method}失败: {response.status_code}")
        print(f"    路径: {path}")
        if response.text:
            print(f"    响应: {response.text[:500]}")
        return None if method == 'GET' else False

    except requests.exceptions.ConnectionError:
        print(f"[!] {device_ip} 连接失败, 请检查设备可达性和RESTCONF服务")
        return None if method == 'GET' else False
    except Exception as e:
        print(f"[!] {device_ip} RESTCONF请求异常: {e}")
        return None if method == 'GET' else False


def restconf_patch(device_ip, path, payload):
    """发送RESTCONF PATCH请求 (合并配置)"""
    return restconf_request(device_ip, 'PATCH', path, payload)


def restconf_get(device_ip, path):
    """发送RESTCONF GET请求 (查询配置)"""
    return restconf_request(device_ip, 'GET', path)


def restconf_delete(device_ip, path):
    """发送RESTCONF DELETE请求 (删除配置)"""
    return restconf_request(device_ip, 'DELETE', path)


# ==================== Loopback接口配置 ====================

def configure_loopback_r1():
    """
    配置R1的Loopback0接口: 1.1.1.1/24
    用于BGP network 1.1.1.0/24 的路由通告
    """
    print("\n[*] 配置R1 Loopback0 (1.1.1.1/24)...")
    payload = {
        "Cisco-IOS-XE-native:interface": {
            "Loopback": [
                {
                    "name": "0",
                    "description": "BGP network source",
                    "ip": {
                        "address": {
                            "primary": {
                                "address": "1.1.1.1",
                                "mask": "255.255.255.0"
                            }
                        }
                    }
                }
            ]
        }
    }
    result = restconf_patch(R1_IP, "Cisco-IOS-XE-native:native/interface", payload)
    if not result:
        print("    [!] RESTCONF配置失败, 请手动执行以下CLI命令:")
        print("    interface Loopback0")
        print("     description BGP network source")
        print("     ip address 1.1.1.1 255.255.255.0")
    return result


def configure_loopback_r2():
    """
    配置R2的Loopback0和Loopback1接口
    Loopback0: 2.2.2.2/24   -> BGP network 2.2.2.0/24
    Loopback1: 22.2.2.2/24  -> BGP network 22.2.2.0/24
    """
    print("\n[*] 配置R2 Loopback0 (2.2.2.2/24) 和 Loopback1 (22.2.2.2/24)...")
    payload = {
        "Cisco-IOS-XE-native:interface": {
            "Loopback": [
                {
                    "name": "0",
                    "description": "BGP network source 1",
                    "ip": {
                        "address": {
                            "primary": {
                                "address": "2.2.2.2",
                                "mask": "255.255.255.0"
                            }
                        }
                    }
                },
                {
                    "name": "1",
                    "description": "BGP network source 2",
                    "ip": {
                        "address": {
                            "primary": {
                                "address": "22.2.2.2",
                                "mask": "255.255.255.0"
                            }
                        }
                    }
                }
            ]
        }
    }
    result = restconf_patch(R2_IP, "Cisco-IOS-XE-native:native/interface", payload)
    if not result:
        print("    [!] RESTCONF配置失败, 请手动执行以下CLI命令:")
        print("    interface Loopback0")
        print("     description BGP network source 1")
        print("     ip address 2.2.2.2 255.255.255.0")
        print("    interface Loopback1")
        print("     description BGP network source 2")
        print("     ip address 22.2.2.2 255.255.255.0")
    return result


# ==================== BGP配置 ====================

def delete_bgp(device_ip, asn):
    """
    删除设备上已有的BGP配置 (避免配置冲突)
    """
    print(f"\n[*] 清除 {device_ip} 上已有的BGP AS {asn}配置...")
    path = f"Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp={asn}"
    result = restconf_delete(device_ip, path)
    if result:
        print(f"[+] {device_ip} BGP AS {asn} 已清除")
    else:
        print(f"[*] {device_ip} BGP AS {asn} 无需清除或不存在")
    return result


def configure_bgp_r1():
    """
    配置R1的BGP AS 65001:
      - bgp log-neighbor-changes
      - network 1.1.1.0 mask 255.255.255.0
      - neighbor 10.10.1.201 remote-as 65002
      - neighbor 10.10.1.201 ebgp-multihop 255
      - neighbor 10.10.1.201 maximum-prefix 2 warning-only
    """
    print(f"\n[*] 配置R1 BGP AS {R1_ASN} (maximum-prefix {MAX_PREFIX_LIMIT} warning-only)...")
    payload = {
        "Cisco-IOS-XE-bgp:bgp": [
            {
                "id": R1_ASN,
                "bgp": {
                    "log-neighbor-changes": {}
                },
                "neighbor": [
                    {
                        "id": R2_IP,
                        "remote-as": R2_ASN,
                        "ebgp-multihop": {
                            "max-hop": 255
                        },
                        "maximum-prefix-v": {
                            "prefix-limit": MAX_PREFIX_LIMIT,
                            "warning-only": {}
                        }
                    }
                ],
                "address-family": {
                    "ipv4": [
                        {
                            "af-name": "unicast",
                            "network": [
                                {
                                    "number": "1.1.1.0",
                                    "mask": "255.255.255.0"
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    result = restconf_patch(R1_IP, "Cisco-IOS-XE-native:native/router", payload)
    if not result:
        print("    [!] RESTCONF配置失败, 请手动执行以下CLI命令:")
        print_cli_r1()
    return result


def configure_bgp_r2():
    """
    配置R2的BGP AS 65002:
      - bgp log-neighbor-changes
      - network 2.2.2.0 mask 255.255.255.0
      - network 22.2.2.0 mask 255.255.255.0
      - neighbor 10.10.1.200 remote-as 65001
      - neighbor 10.10.1.200 ebgp-multihop 255
    """
    print(f"\n[*] 配置R2 BGP AS {R2_ASN} (发布多个前缀触发R1告警)...")
    payload = {
        "Cisco-IOS-XE-bgp:bgp": [
            {
                "id": R2_ASN,
                "bgp": {
                    "log-neighbor-changes": {}
                },
                "neighbor": [
                    {
                        "id": R1_IP,
                        "remote-as": R1_ASN,
                        "ebgp-multihop": {
                            "max-hop": 255
                        }
                    }
                ],
                "address-family": {
                    "ipv4": [
                        {
                            "af-name": "unicast",
                            "network": [
                                {
                                    "number": "2.2.2.0",
                                    "mask": "255.255.255.0"
                                },
                                {
                                    "number": "22.2.2.0",
                                    "mask": "255.255.255.0"
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    result = restconf_patch(R2_IP, "Cisco-IOS-XE-native:native/router", payload)
    if not result:
        print("    [!] RESTCONF配置失败, 请手动执行以下CLI命令:")
        print_cli_r2()
    return result


# ==================== CLI参考命令 ====================

def print_cli_r1():
    """打印R1的BGP CLI配置命令"""
    print("\n" + "=" * 60)
    print("R1 (10.10.1.200) CLI配置命令:")
    print("=" * 60)
    print("""!
! ---- 配置Loopback0接口 ----
interface Loopback0
 description BGP network source
 ip address 1.1.1.1 255.255.255.0
!
! ---- 配置BGP ----
router bgp 65001
 bgp log-neighbor-changes
 network 1.1.1.0 mask 255.255.255.0
 neighbor 10.10.1.201 remote-as 65002
 neighbor 10.10.1.201 ebgp-multihop 255
 neighbor 10.10.1.201 maximum-prefix 2 warning-only
!""")


def print_cli_r2():
    """打印R2的BGP CLI配置命令"""
    print("\n" + "=" * 60)
    print("R2 (10.10.1.201) CLI配置命令:")
    print("=" * 60)
    print("""!
! ---- 配置Loopback0接口 ----
interface Loopback0
 description BGP network source 1
 ip address 2.2.2.2 255.255.255.0
!
! ---- 配置Loopback1接口 ----
interface Loopback1
 description BGP network source 2
 ip address 22.2.2.2 255.255.255.0
!
! ---- 配置BGP ----
router bgp 65002
 bgp log-neighbor-changes
 network 2.2.2.0 mask 255.255.255.0
 network 22.2.2.0 mask 255.255.255.0
 neighbor 10.10.1.200 remote-as 65001
 neighbor 10.10.1.200 ebgp-multihop 255
!""")


# ==================== 验证函数 ====================

def verify_bgp_neighbors(device_ip):
    """
    通过RESTCONF查询BGP邻居状态

    Args:
        device_ip: 设备IP地址

    Returns:
        list: BGP邻居信息列表, 失败返回None
    """
    print(f"\n[*] 查询 {device_ip} BGP邻居状态...")
    data = restconf_get(device_ip, "Cisco-IOS-XE-bgp-oper:bgp-state-data/neighbors")
    if data is None:
        print(f"[-] {device_ip} 无法获取BGP邻居状态")
        print(f"    请手动执行: show ip bgp summary")
        return None

    neighbors = data.get('Cisco-IOS-XE-bgp-oper:neighbors', {}).get('neighbor', [])
    if not neighbors:
        print(f"[-] {device_ip} 未发现BGP邻居")
        return []

    print(f"[+] {device_ip} BGP邻居状态:")
    for nbr in neighbors:
        nbr_id = nbr.get('neighbor-id', 'N/A')
        state = nbr.get('state', 'N/A')
        prefixes_received = nbr.get('prefixes-accepted', 0)
        # 连接状态描述
        state_desc = {
            'idle': 'Idle',
            'connect': 'Connect',
            'active': 'Active',
            'opensent': 'OpenSent',
            'openconfirm': 'OpenConfirm',
            'established': 'Established',
        }.get(str(state).lower(), str(state))

        print(f"    邻居: {nbr_id}")
        print(f"      状态: {state_desc}")
        print(f"      接受前缀数: {prefixes_received}")

        # 检查是否触发了maximum-prefix告警
        if device_ip == R1_IP and nbr_id == R2_IP:
            if isinstance(prefixes_received, int) and prefixes_received >= MAX_PREFIX_LIMIT:
                print(f"      >>> 前缀数({prefixes_received})已达到maximum-prefix阈值({MAX_PREFIX_LIMIT})!")
                print(f"      >>> R1应已产生 %BGP-4-MAXPFX SYSLOG日志")

    return neighbors


def verify_bgp_config(device_ip):
    """
    通过RESTCONF查询BGP运行配置, 验证maximum-prefix配置

    Args:
        device_ip: 设备IP地址
    """
    asn = R1_ASN if device_ip == R1_IP else R2_ASN
    print(f"\n[*] 查询 {device_ip} BGP AS {asn} 配置...")
    data = restconf_get(device_ip, f"Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp={asn}")
    if data is None:
        print(f"[-] {device_ip} 无法获取BGP配置")
        print(f"    请手动执行: show running-config | section router bgp")
        return None

    print(f"[+] {device_ip} BGP配置:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def verify_loopback(device_ip, loopback_name="0"):
    """
    通过RESTCONF查询Loopback接口配置

    Args:
        device_ip: 设备IP地址
        loopback_name: Loopback编号
    """
    print(f"\n[*] 查询 {device_ip} Loopback{loopback_name} 配置...")
    data = restconf_get(device_ip, f"Cisco-IOS-XE-native:native/interface/Loopback={loopback_name}")
    if data is None:
        print(f"[-] {device_ip} 无法获取Loopback{loopback_name}配置")
        print(f"    请手动执行: show running-config interface Loopback{loopback_name}")
        return None

    print(f"[+] {device_ip} Loopback{loopback_name} 配置:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


# ==================== 主程序 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("DAY8 任务一: 配置BGP邻居与maximum-prefix阈值")
    print("=" * 60)
    print(f"R1: {R1_IP}  AS {R1_ASN}  (配置maximum-prefix {MAX_PREFIX_LIMIT} warning-only)")
    print(f"R2: {R2_IP}  AS {R2_ASN}  (发布多个前缀触发告警)")

    # ===== Step 1: 配置Loopback接口 =====
    print("\n" + "=" * 60)
    print("Step 1: 配置Loopback接口 (为BGP network命令提供路由)")
    print("=" * 60)
    configure_loopback_r1()
    configure_loopback_r2()

    # ===== Step 2: 清除已有BGP配置(可选) =====
    print("\n" + "=" * 60)
    print("Step 2: 清除已有BGP配置 (避免配置冲突)")
    print("=" * 60)
    delete_bgp(R1_IP, R1_ASN)
    delete_bgp(R2_IP, R2_ASN)

    # ===== Step 3: 配置BGP =====
    print("\n" + "=" * 60)
    print("Step 3: 配置BGP")
    print("=" * 60)
    bgp_r1_ok = configure_bgp_r1()
    bgp_r2_ok = configure_bgp_r2()

    # ===== Step 4: 等待BGP邻居建立 =====
    print("\n" + "=" * 60)
    print("Step 4: 等待BGP邻居建立 (30秒)")
    print("=" * 60)
    for i in range(30, 0, -5):
        print(f"    等待中... {i}秒")
        time.sleep(5)

    # ===== Step 5: 验证BGP配置和邻居状态 =====
    print("\n" + "=" * 60)
    print("Step 5: 验证BGP配置和邻居状态")
    print("=" * 60)
    verify_loopback(R1_IP, "0")
    verify_loopback(R2_IP, "0")
    verify_loopback(R2_IP, "1")
    verify_bgp_config(R1_IP)
    verify_bgp_config(R2_IP)
    verify_bgp_neighbors(R1_IP)
    verify_bgp_neighbors(R2_IP)

    # ===== 输出CLI参考命令 =====
    print("\n" + "=" * 60)
    print("CLI参考命令 (如RESTCONF配置失败, 请手动在设备上执行)")
    print("=" * 60)
    print_cli_r1()
    print_cli_r2()

    # ===== 输出验证命令 =====
    print("\n" + "=" * 60)
    print("验证命令 (在路由器上手动执行)")
    print("=" * 60)
    print("""
R1验证命令:
  show ip bgp summary                         ! 查看BGP邻居状态和前缀数
  show ip bgp neighbors 10.10.1.201           ! 查看邻居详细信息(含maximum-prefix)
  show logging | include MAXPFX               ! 查看maximum-prefix告警日志
  show running-config | section router bgp    ! 查看BGP运行配置

R2验证命令:
  show ip bgp summary                         ! 查看BGP邻居状态
  show ip bgp                                 ! 查看BGP路由表
  show running-config | section router bgp    ! 查看BGP运行配置

预期的SYSLOG日志:
  %BGP-4-MAXPFX: Number of prefixes received from 10.10.1.201
  reaches 2, max 2
""")

    print("=" * 60)
    print("任务一配置完成!")
    print("如果R2发布了2条以上前缀, R1应产生 %BGP-4-MAXPFX SYSLOG日志")
    print("=" * 60)
