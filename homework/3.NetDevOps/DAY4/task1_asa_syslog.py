'''
=================================================================
NetDevOps DAY4 任务
使用ASA REST API配置Syslog服务器
=================================================================
ASA初始化配置:
    hostname ASA
    !
    interface Management0/0
        management-only
        nameif MGMT
        security-level 100
        ip address 10.1.1.4 255.255.255.0
        no shutdown
    !
    aaa authentication ssh console LOCAL
    aaa authentication http console LOCAL
    !
    http server enable
    http 0.0.0.0 0.0.0.0 MGMT
    ssh 0.0.0.0 0.0.0.0 MGMT
    username admin password Cisc0123 privilege 15
    !
    rest-api image flash:/asa-restapi-7131-lfbff-k8.SPA
    rest-api agent

任务要求:
1. 使用requests通过HTTP Basic Auth获取ASA REST API Token
2. 使用Token调用 /api/logging/syslogserver 创建syslog服务器
3. 封装 config_syslog(ifname, syslog_server_ip, token) 函数
'''

import requests
from requests.auth import HTTPBasicAuth
import urllib3

# 禁用SSL警告（测试环境使用自签名证书时需要）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ASA设备默认配置
ASA_IP = "10.10.1.202"
ASA_USER = "admin"
ASA_PASS = "Cisc0123"
ASA_BASE_URL = f"https://{ASA_IP}"


def get_asa_token(asa_ip=ASA_IP, username=ASA_USER, password=ASA_PASS):
    """
    通过HTTP Basic认证获取ASA REST API Token

    参数:
        asa_ip: ASA管理IP地址
        username: 认证用户名
        password: 认证密码

    返回:
        成功返回token字符串，失败返回None
    """
    url = f"https://{asa_ip}/api/tokenservices"
    print(f"[*] 请求Token: {url}")

    try:
        response = requests.post(
            url,
            auth=HTTPBasicAuth(username, password),
            verify=False,
            timeout=10
        )

        if response.status_code == 204:
            # Token在响应头 X-Auth-Token 中
            token = response.headers.get('X-Auth-Token')
            if token:
                print(f"[+] 获取Token成功")
                return token
            else:
                print(f"[-] 响应中未找到X-Auth-Token")
                return None
        elif response.status_code == 401:
            print(f"[-] 认证失败(401): 用户名或密码错误")
            return None
        else:
            print(f"[-] 获取Token失败，状态码: {response.status_code}")
            print(f"[-] 响应内容: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print(f"[-] 连接错误: 无法连接到ASA {asa_ip}")
        return None
    except requests.exceptions.Timeout:
        print(f"[-] 请求超时")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[-] 请求异常: {e}")
        return None


def config_syslog(ifname, syslog_server_ip, token, asa_ip=ASA_IP):
    """
    使用ASA REST API配置Syslog服务器

    参数:
        ifname: 出接口名称，例如 "MGMT"
        syslog_server_ip: Syslog服务器IP地址，例如 "10.1.1.101"
        token: ASA REST API认证Token (X-Auth-Token)
        asa_ip: ASA设备IP地址（默认10.1.1.4）

    返回:
        成功返回True，失败返回False
    """
    url = f"https://{asa_ip}/api/logging/syslogserver"

    # 构造请求体（与ASA REST API文档一致）
    payload = {
        "ip": {
            "kind": "IPv4Address",
            "value": syslog_server_ip
        },
        "interface": {
            "kind": "objectRef#Interface",
            "name": ifname
        },
        "port": 514,
        "emblemEnabled": False,
        "secureEnabled": False,
        "protocol": "UDP"
    }

    # 构造请求头
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    print(f"[*] 配置Syslog服务器: {syslog_server_ip}")
    print(f"[*] 出接口: {ifname}")
    print(f"[*] 请求URL: {url}")
    print(f"[*] 请求Body: {payload}")

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            verify=False,
            timeout=10
        )

        if response.status_code == 201:
            print(f"[+] Syslog服务器配置成功！状态码: {response.status_code}")
            print(f"[+] 响应内容: {response.text}")
            return True
        elif response.status_code == 400:
            print(f"[-] 请求参数错误(400)")
            print(f"[-] 响应内容: {response.text}")
            return False
        elif response.status_code == 401:
            print(f"[-] Token认证失败(401): Token无效或已过期")
            return False
        elif response.status_code == 409:
            print(f"[-] 资源冲突(409): Syslog服务器可能已存在")
            print(f"[-] 响应内容: {response.text}")
            return False
        else:
            print(f"[-] 配置失败，状态码: {response.status_code}")
            print(f"[-] 响应内容: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"[-] 连接错误: 无法连接到ASA {asa_ip}")
        return False
    except requests.exceptions.Timeout:
        print(f"[-] 请求超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[-] 请求异常: {e}")
        return False


def get_syslog_servers(token, asa_ip=ASA_IP):
    """
    查询当前配置的Syslog服务器列表（辅助验证函数）

    参数:
        token: ASA REST API认证Token
        asa_ip: ASA设备IP地址

    返回:
        成功返回服务器列表(dict)，失败返回None
    """
    url = f"https://{asa_ip}/api/logging/syslogserver"
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    print(f"[*] 查询Syslog服务器列表: {url}")

    try:
        response = requests.get(
            url,
            headers=headers,
            verify=False,
            timeout=10
        )

        if response.status_code == 200:
            print(f"[+] 查询成功")
            return response.json()
        else:
            print(f"[-] 查询失败，状态码: {response.status_code}")
            print(f"[-] 响应内容: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[-] 请求异常: {e}")
        return None


if __name__ == '__main__':
    # ======================
    # 配置参数（根据实际环境修改）
    # ======================
    SYSLOG_SERVER_IP = "10.10.1.205"   # Syslog服务器IP（Linux本机地址）
    INTERFACE_NAME = "MGMT"            # ASA出接口名称

    print("=" * 50)
    print("ASA REST API - 配置Syslog服务器")
    print("=" * 50)

    # 步骤1: 获取Token
    print("\n>>> 步骤1: 获取ASA REST API Token")
    token = get_asa_token()

    if not token:
        print("\n[-] 无法获取Token，程序退出")
        exit(1)

    print(f"[+] Token: {token[:20]}...")

    # 步骤2: 配置Syslog服务器
    print("\n>>> 步骤2: 配置Syslog服务器")
    result = config_syslog(INTERFACE_NAME, SYSLOG_SERVER_IP, token)

    if result:
        print("\n[+] Syslog服务器配置完成！")
    else:
        print("\n[-] Syslog服务器配置失败")

    # 步骤3: 验证配置（可选）
    print("\n>>> 步骤3: 验证当前Syslog服务器配置")
    servers = get_syslog_servers(token)
    if servers:
        import json
        print(json.dumps(servers, indent=2, ensure_ascii=False))
