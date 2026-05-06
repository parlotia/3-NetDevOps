"""
=================================================================
NetDevOps DAY8 任务二: 配置EEM捕获BGP前缀阈值日志并调用Guestshell脚本
=================================================================
场景: 在R1上配置EEM Applet, 当SYSLOG中出现 %BGP-4-MAXPFX 日志时,
      EEM提取BGP邻居IP、当前前缀数、最大前缀阈值, 然后调用
      Guestshell中的Python脚本发送告警

环境信息:
  R1 (C8KV-1): 10.10.1.200  AS 65001  配置EEM + maximum-prefix
  R2 (C8KV-2): 10.10.1.201  AS 65002  发布多个前缀触发告警
  Linux主机:   10.10.1.205

EEM工作流程:
  1. IOS-XE产生 %BGP-4-MAXPFX SYSLOG日志
  2. EEM捕获日志, 用regexp提取关键信息
  3. EEM调用 Guestshell Python脚本, 传递参数
  4. Python脚本解析参数并发送邮件告警

EEM Applet配置:
  event manager applet bgp_prefix_threshold_notification
   event syslog pattern "BGP-4-MAXPFX: Number of prefixes received from"
   action 1.0 regexp "received from ([0-9.]+)" "$_syslog_msg" match ipaddr
   action 2.0 regexp "reaches ([0-9]+), max ([0-9]+)" "$_syslog_msg" match current_prefix max_prefix
   action 3.0 syslog msg "bgp neighbor: $ipaddr"
   action 4.0 syslog msg "current prefixes: $current_prefix"
   action 5.0 syslog msg "max prefixes: $max_prefix"
   action 5.5 cli command "en"
   action 6.0 cli command "guestshell run python3 /home/guestshell/bgp_threshold_notification.py received from $ipaddr : $current_prefix exceeds limit $max_prefix"

配置方式: RESTCONF (主) + Paramiko SSH (备选)
=================================================================
"""

import requests
import urllib3
import time
import json
import os
import sys

# 禁用SSL证书警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== 设备信息 ====================
R1_IP = '10.10.1.200'       # C8KV-1 (EEM配置在此设备)
R2_IP = '10.10.1.201'       # C8KV-2
USERNAME = 'admin'
PASSWORD = 'Cisc0123'

# EEM参数
EEM_APPLET_NAME = 'bgp_prefix_threshold_notification'
GUESTSHELL_SCRIPT_PATH = '/home/guestshell/bgp_threshold_notification.py'
GUESTSHELL_SCRIPT_LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       'bgp_threshold_notification.py')

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

        if response.status_code == 204:
            print(f"[+] {device_ip} RESTCONF {method}成功 (204 No Content)")
            return True if method != 'GET' else None

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

        if response.status_code == 201:
            print(f"[+] {device_ip} RESTCONF {method}成功 (201 Created)")
            return True

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


# ==================== Paramiko SSH工具函数 ====================

def ssh_configure(device_ip, cli_commands):
    """
    通过Paramiko SSH发送CLI配置命令

    Args:
        device_ip: 设备IP地址
        cli_commands: CLI命令列表 (每行一个命令)

    Returns:
        bool: 成功返回True, 失败返回False
    """
    try:
        import paramiko
    except ImportError:
        print("[!] paramiko未安装, 请执行: pip install paramiko")
        return False

    print(f"\n[*] 通过SSH配置 {device_ip}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device_ip, username=USERNAME, password=PASSWORD,
                    look_for_keys=False, allow_agent=False, timeout=15)

        # 进入配置模式并发送命令
        full_cmd = 'configure terminal\n'
        for cmd in cli_commands:
            full_cmd += cmd + '\n'
        full_cmd += 'end\n'

        stdin, stdout, stderr = ssh.exec_command(full_cmd, timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        error = stderr.read().decode('utf-8', errors='replace')

        ssh.close()

        if error and 'Invalid' in error:
            print(f"[-] {device_ip} SSH配置可能有错误:")
            print(f"    {error[:300]}")
            return False

        print(f"[+] {device_ip} SSH配置命令已发送")
        return True

    except Exception as e:
        print(f"[!] {device_ip} SSH连接失败: {e}")
        return False


def ssh_deploy_guestshell_script(device_ip, script_content):
    """
    通过SSH在Guestshell中部署Python脚本
    使用方式: SCP脚本到bootflash, 再从Guestshell中复制

    Args:
        device_ip: 设备IP地址
        script_content: 脚本内容 (字符串)

    Returns:
        bool: 成功返回True, 失败返回False
    """
    try:
        import paramiko
    except ImportError:
        print("[!] paramiko未安装, 请执行: pip install paramiko")
        return False

    script_name = os.path.basename(GUESTSHELL_SCRIPT_PATH)

    print(f"\n[*] 通过SSH部署Guestshell脚本到 {device_ip}...")
    print(f"    目标路径: {GUESTSHELL_SCRIPT_PATH}")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device_ip, username=USERNAME, password=PASSWORD,
                    look_for_keys=False, allow_agent=False, timeout=15)

        # 方法: 使用guestshell run bash创建脚本文件
        # 将脚本内容通过bash heredoc写入Guestshell
        # 注意: 需要转义脚本中的特殊字符
        escaped_content = script_content.replace("'", "'\\''")
        bash_cmd = f"guestshell run bash -c 'cat > {GUESTSHELL_SCRIPT_PATH} << 'GUESTSHELL_EOF'\n{script_content}\nGUESTSHELL_EOF'"

        # 分步方式: 先写到bootflash, 再从Guestshell中复制
        # Step 1: 写脚本到bootflash
        print(f"    Step 1: 写入脚本到bootflash...")
        write_cmd = f"put file bootflash:{script_name}\n"
        stdin, stdout, stderr = ssh.exec_command(
            f"echo '{escaped_content}' | shell -c 'cat > bootflash:{script_name}'",
            timeout=30
        )
        error = stderr.read().decode('utf-8', errors='replace')
        # shell命令可能不可用, 尝试其他方式

        # Step 2: 从bootflash复制到Guestshell
        print(f"    Step 2: 从bootflash复制到Guestshell...")
        copy_cmd = f"guestshell run bash -c 'cp /bootflash/{script_name} {GUESTSHELL_SCRIPT_PATH} && chmod +x {GUESTSHELL_SCRIPT_PATH}'"
        stdin, stdout, stderr = ssh.exec_command(copy_cmd, timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        error = stderr.read().decode('utf-8', errors='replace')

        # Step 3: 验证脚本是否存在
        print(f"    Step 3: 验证脚本部署...")
        verify_cmd = f"guestshell run bash -c 'ls -la {GUESTSHELL_SCRIPT_PATH}'"
        stdin, stdout, stderr = ssh.exec_command(verify_cmd, timeout=15)
        output = stdout.read().decode('utf-8', errors='replace')
        if GUESTSHELL_SCRIPT_PATH in output:
            print(f"[+] Guestshell脚本部署成功!")
            print(f"    {output.strip()}")
            ssh.close()
            return True
        else:
            print(f"[-] Guestshell脚本可能未部署成功")
            print(f"    stdout: {output[:200]}")
            print(f"    stderr: {error[:200]}")
            ssh.close()
            return False

    except Exception as e:
        print(f"[!] {device_ip} SSH部署Guestshell脚本失败: {e}")
        return False


def scp_deploy_guestshell_script(device_ip, local_script_path):
    """
    通过SCP将脚本上传到设备bootflash, 然后复制到Guestshell

    Args:
        device_ip: 设备IP地址
        local_script_path: 本地脚本文件路径

    Returns:
        bool: 成功返回True, 失败返回False
    """
    try:
        import paramiko
    except ImportError:
        print("[!] paramiko未安装, 请执行: pip install paramiko")
        return False

    script_name = os.path.basename(local_script_path)

    if not os.path.exists(local_script_path):
        print(f"[-] 本地脚本不存在: {local_script_path}")
        return False

    print(f"\n[*] 通过SCP部署Guestshell脚本到 {device_ip}...")
    print(f"    本地路径: {local_script_path}")
    print(f"    目标路径: {GUESTSHELL_SCRIPT_PATH}")

    try:
        # Step 1: SCP上传到bootflash
        print(f"    Step 1: SCP上传脚本到bootflash...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device_ip, username=USERNAME, password=PASSWORD,
                    look_for_keys=False, allow_agent=False, timeout=15)

        sftp = ssh.open_sftp()
        remote_path = f'{script_name}'  # bootflash根目录
        # paramiko SFTP对IOS-XE: 默认路径就是bootflash
        sftp.put(local_script_path, remote_path)
        print(f"[+] SCP上传成功: bootflash:{script_name}")
        sftp.close()

        # Step 2: 从bootflash复制到Guestshell
        print(f"    Step 2: 从bootflash复制到Guestshell...")
        copy_cmd = (f"guestshell run bash -c "
                    f"'cp /bootflash/{script_name} {GUESTSHELL_SCRIPT_PATH} "
                    f"&& chmod +x {GUESTSHELL_SCRIPT_PATH}'")
        stdin, stdout, stderr = ssh.exec_command(copy_cmd, timeout=30)
        error = stderr.read().decode('utf-8', errors='replace')

        # Step 3: 验证
        print(f"    Step 3: 验证脚本部署...")
        verify_cmd = f"guestshell run bash -c 'ls -la {GUESTSHELL_SCRIPT_PATH}'"
        stdin, stdout, stderr = ssh.exec_command(verify_cmd, timeout=15)
        output = stdout.read().decode('utf-8', errors='replace')

        if GUESTSHELL_SCRIPT_PATH in output:
            print(f"[+] Guestshell脚本部署成功!")
            print(f"    {output.strip()}")
            ssh.close()
            return True
        else:
            print(f"[-] Guestshell脚本可能未部署成功")
            print(f"    stdout: {output[:200]}")
            if error:
                print(f"    stderr: {error[:200]}")
            ssh.close()
            return False

    except Exception as e:
        print(f"[!] SCP部署失败: {e}")
        print(f"    请手动部署脚本 (参考下方说明)")
        return False


# ==================== EEM配置函数 ====================

# EEM CLI配置命令 (完整, 可直接在设备上执行)
EEM_CLI_COMMANDS = [
    f"no event manager applet {EEM_APPLET_NAME}",          # 先删除已有applet
    f"event manager applet {EEM_APPLET_NAME}",
    ' event syslog pattern "BGP-4-MAXPFX: Number of prefixes received from"',
    ' action 1.0 regexp "received from ([0-9.]+)" "$_syslog_msg" match ipaddr',
    ' action 2.0 regexp "reaches ([0-9]+), max ([0-9]+)" "$_syslog_msg" match current_prefix max_prefix',
    ' action 3.0 syslog msg "bgp neighbor: $ipaddr"',
    ' action 4.0 syslog msg "current prefixes: $current_prefix"',
    ' action 5.0 syslog msg "max prefixes: $max_prefix"',
    ' action 5.5 cli command "en"',
    f' action 6.0 cli command "guestshell run python3 {GUESTSHELL_SCRIPT_PATH} received from $ipaddr : $current_prefix exceeds limit $max_prefix"',
]


def configure_eem_restconf():
    """
    通过RESTCONF配置EEM Applet
    使用Cisco-IOS-XE-eem YANG模型

    注意: EEM的YANG模型结构较复杂, 如果RESTCONF方式失败,
          请使用CLI方式或Paramiko SSH方式
    """
    print(f"\n[*] 通过RESTCONF配置EEM Applet '{EEM_APPLET_NAME}'...")

    # 先删除已有applet
    delete_path = f"Cisco-IOS-XE-native:native/event-manager/Cisco-IOS-XE-eem:applet={EEM_APPLET_NAME}"
    restconf_delete(R1_IP, delete_path)

    # 构造EEM Applet的RESTCONF payload
    # 基于Cisco-IOS-XE-eem YANG模型结构
    payload = {
        "Cisco-IOS-XE-eem:applet": [
            {
                "name": EEM_APPLET_NAME,
                "event": {
                    "syslog": {
                        "pattern": "BGP-4-MAXPFX: Number of prefixes received from"
                    }
                },
                "action": [
                    {
                        "name": "1.0",
                        "string": 'regexp "received from ([0-9.]+)" "$_syslog_msg" match ipaddr'
                    },
                    {
                        "name": "2.0",
                        "string": 'regexp "reaches ([0-9]+), max ([0-9]+)" "$_syslog_msg" match current_prefix max_prefix'
                    },
                    {
                        "name": "3.0",
                        "string": 'syslog msg "bgp neighbor: $ipaddr"'
                    },
                    {
                        "name": "4.0",
                        "string": 'syslog msg "current prefixes: $current_prefix"'
                    },
                    {
                        "name": "5.0",
                        "string": 'syslog msg "max prefixes: $max_prefix"'
                    },
                    {
                        "name": "5.5",
                        "string": 'cli command "en"'
                    },
                    {
                        "name": "6.0",
                        "string": f'cli command "guestshell run python3 {GUESTSHELL_SCRIPT_PATH} received from $ipaddr : $current_prefix exceeds limit $max_prefix"'
                    }
                ]
            }
        ]
    }

    result = restconf_patch(R1_IP, "Cisco-IOS-XE-native:native/event-manager", payload)
    if not result:
        print("    [!] RESTCONF配置EEM失败, 请使用以下替代方式:")
        print("    方式1: Paramiko SSH自动配置 (本脚本支持)")
        print("    方式2: 手动在R1 CLI中粘贴EEM配置命令")
    return result


def configure_eem_ssh():
    """
    通过Paramiko SSH配置EEM Applet (更可靠的备选方式)

    Returns:
        bool: 成功返回True, 失败返回False
    """
    print(f"\n[*] 通过Paramiko SSH配置EEM Applet '{EEM_APPLET_NAME}'...")
    return ssh_configure(R1_IP, EEM_CLI_COMMANDS)


def print_eem_cli_commands():
    """打印EEM CLI配置命令 (供手动在设备上执行)"""
    print("\n" + "=" * 60)
    print(f"R1 ({R1_IP}) EEM Applet CLI配置命令:")
    print("=" * 60)
    print("configure terminal")
    for cmd in EEM_CLI_COMMANDS:
        print(f" {cmd}")
    print("end")
    print()
    print("验证命令:")
    print(f"  show event manager applet {EEM_APPLET_NAME}")
    print("  show event manager action")
    print("  show logging | include bgp_prefix_threshold")
    print()


# ==================== EEM验证函数 ====================

def verify_eem_config():
    """
    通过RESTCONF查询EEM Applet配置

    Returns:
        dict: EEM配置数据, 失败返回None
    """
    print(f"\n[*] 查询R1 EEM Applet '{EEM_APPLET_NAME}' 配置...")
    path = f"Cisco-IOS-XE-native:native/event-manager/Cisco-IOS-XE-eem:applet={EEM_APPLET_NAME}"
    data = restconf_get(R1_IP, path)
    if data is None:
        print(f"[-] 无法通过RESTCONF获取EEM配置")
        print(f"    请手动执行: show event manager applet {EEM_APPLET_NAME}")
        return None

    print(f"[+] R1 EEM Applet配置:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def verify_guestshell():
    """
    通过RESTCONF查询Guestshell运行状态

    Returns:
        dict: Guestshell状态数据, 失败返回None
    """
    print(f"\n[*] 查询R1 Guestshell状态...")
    path = "Cisco-IOS-XE-native:native/iox"
    data = restconf_get(R1_IP, path)
    if data is None:
        print(f"[-] 无法通过RESTCONF获取Guestshell状态")
        print(f"    请手动执行: show iox")
        return None

    print(f"[+] R1 Guestshell/IOx状态:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


# ==================== Guestshell脚本内容 ====================

def get_guestshell_script_content():
    """
    返回bgp_threshold_notification.py的脚本内容
    此脚本将部署到R1的Guestshell中, 由EEM Applet调用
    (任务三中已更新为使用re.match解析参数 + 调用邮件函数的版本)

    注意: 此处保留的是任务二版本的脚本(仅记录日志, 不发邮件)
    完整版本(含邮件发送)请使用 task3 同目录下的 bgp_threshold_notification.py
    """
    # 读取本地最新版本的脚本文件
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'bgp_threshold_notification.py')
    if os.path.exists(script_path):
        with open(script_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # 如果本地文件不存在, 返回任务二版本的备用内容
        return '''#!/usr/bin/env python3
# -*- coding=utf-8 -*-
import sys
import datetime

para_raw = ' '.join(sys.argv[1:]).strip()
print(f"[!] BGP前缀阈值告警 (备用版本)")
print(f"    原始参数: {para_raw}")
print(f"    请部署完整版本的bgp_threshold_notification.py")
'''


# ==================== 主程序 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("DAY8 任务二: 配置EEM捕获BGP前缀阈值日志")
    print("             并调用Guestshell脚本")
    print("=" * 60)
    print(f"R1: {R1_IP}  (配置EEM Applet)")
    print(f"EEM Applet: {EEM_APPLET_NAME}")
    print(f"Guestshell脚本: {GUESTSHELL_SCRIPT_PATH}")

    # ===== Step 1: 验证Guestshell状态 =====
    print("\n" + "=" * 60)
    print("Step 1: 验证R1的Guestshell状态")
    print("=" * 60)
    verify_guestshell()

    # ===== Step 2: 创建本地Guestshell脚本文件 =====
    print("\n" + "=" * 60)
    print("Step 2: 创建本地Guestshell脚本文件")
    print("=" * 60)
    print(f"[*] 写入脚本到: {GUESTSHELL_SCRIPT_LOCAL}")
    script_content = get_guestshell_script_content()
    # 去掉外层的三引号包裹 (因为是从Python字符串返回的)
    # 实际写入时内容已经是干净的Python代码
    with open(GUESTSHELL_SCRIPT_LOCAL, 'w', encoding='utf-8') as f:
        f.write(script_content)
    print(f"[+] Guestshell脚本已创建: {GUESTSHELL_SCRIPT_LOCAL}")

    # ===== Step 3: 部署Guestshell脚本到R1 =====
    print("\n" + "=" * 60)
    print("Step 3: 部署Guestshell脚本到R1")
    print("=" * 60)
    deploy_ok = scp_deploy_guestshell_script(R1_IP, GUESTSHELL_SCRIPT_LOCAL)
    if not deploy_ok:
        print("\n[!] 自动部署失败, 请手动部署脚本:")
        print(f"    方法1: SCP上传")
        print(f"      scp {GUESTSHELL_SCRIPT_LOCAL} {USERNAME}@{R1_IP}:{os.path.basename(GUESTSHELL_SCRIPT_PATH)}")
        print(f"      然后在R1 CLI执行:")
        print(f"        guestshell run bash -c 'cp /bootflash/{os.path.basename(GUESTSHELL_SCRIPT_PATH)} {GUESTSHELL_SCRIPT_PATH} && chmod +x {GUESTSHELL_SCRIPT_PATH}'")
        print()
        print(f"    方法2: 直接在R1 CLI创建")
        print(f"      在R1上进入: guestshell run bash")
        print(f"      然后执行: vi {GUESTSHELL_SCRIPT_PATH}")
        print(f"      粘贴脚本内容并保存")

    # ===== Step 4: 配置EEM Applet =====
    print("\n" + "=" * 60)
    print("Step 4: 配置EEM Applet")
    print("=" * 60)

    # 方式1: 尝试RESTCONF
    eem_ok = configure_eem_restconf()

    # 方式2: 如果RESTCONF失败, 尝试Paramiko SSH
    if not eem_ok:
        print("\n[*] RESTCONF配置失败, 尝试Paramiko SSH方式...")
        try:
            eem_ok = configure_eem_ssh()
        except Exception as e:
            print(f"[!] Paramiko SSH也失败: {e}")

    # 方式3: 如果都失败, 打印CLI命令供手动执行
    if not eem_ok:
        print_eem_cli_commands()

    # ===== Step 5: 验证EEM配置 =====
    print("\n" + "=" * 60)
    print("Step 5: 验证EEM配置")
    print("=" * 60)
    verify_eem_config()

    # ===== 输出完整CLI命令参考 =====
    print("\n" + "=" * 60)
    print("CLI配置命令参考 (如自动配置失败, 请手动在R1上执行)")
    print("=" * 60)
    print_eem_cli_commands()

    # ===== 输出验证和测试说明 =====
    print("\n" + "=" * 60)
    print("验证和测试说明")
    print("=" * 60)
    print("""
1. 验证EEM Applet配置:
   R1# show event manager applet bgp_prefix_threshold_notification

2. 验证Guestshell脚本:
   R1# guestshell run python3 /home/guestshell/bgp_threshold_notification.py received from 10.10.1.201 : 2 exceeds limit 2
   (手动测试脚本是否能正确解析参数)

3. 触发BGP MAXPFX告警 (如果尚未触发):
   R1# clear ip bgp * out
   (重新建立BGP邻居, 触发MAXPFX SYSLOG)

4. 查看EEM触发的SYSLOG:
   R1# show logging | include bgp_prefix_threshold
   R1# show logging | include MAXPFX

5. 查看Guestshell脚本执行日志:
   R1# guestshell run bash -c "cat /home/guestshell/bgp_threshold_alert.log"

6. 验证IOS-XE Guestshell是否启用:
   R1# show iox
   如果未启用, 需要执行:
   R1(config)# iox
""")

    print("=" * 60)
    print("任务二配置完成!")
    print("EEM将在BGP前缀达到阈值时自动调用Guestshell脚本")
    print("=" * 60)
