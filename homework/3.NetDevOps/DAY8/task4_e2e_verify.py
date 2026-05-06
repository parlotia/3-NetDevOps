"""
=================================================================
NetDevOps DAY8 任务四: 手工测试Python脚本 + 触发真实BGP告警
=================================================================
验证流程:
  Step 1: 手工测试 - 在R1上执行guestshell run命令, 确认脚本、
          Python导入、SMTP服务器和邮箱授权码都正常
  Step 2: 触发真实告警 - 通过重置BGP邻居触发MAXPFX SYSLOG,
          EEM捕获后自动调用Guestshell脚本发送邮件
  Step 3: 验证结果 - 检查EEM注册状态、SYSLOG日志、邮件收件箱

手工测试命令:
  R1# guestshell run python3 /home/guestshell/bgp_threshold_notification.py \
       received from 10.10.1.201 : 2 exceeds limit 2

触发真实告警 (重置BGP):
  R1# clear ip bgp * out

验证命令:
  R1# show event manager policy registered
  R1# show logging | include BGP-4-MAXPFX|bgp neighbor|current prefixes|max prefixes

期望邮件正文:
  Neighbor: 10.10.1.201
  Now: 2
  Exceed the limit: 2
=================================================================
"""

import os
import sys
import time

# ==================== 设备信息 ====================
R1_IP = '10.10.1.200'       # C8KV-1 (EEM + Guestshell)
R2_IP = '10.10.1.201'       # C8KV-2 (BGP邻居)
USERNAME = 'admin'
PASSWORD = 'Cisc0123'

# Guestshell脚本路径
GUESTSHELL_SCRIPT = '/home/guestshell/bgp_threshold_notification.py'
GUESTSHELL_SMTP_LIB = '/home/guestshell/qyt_smtp_attachment.py'

# 本地脚本目录
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))


# ==================== Paramiko SSH工具 ====================

def ssh_exec(device_ip, command, timeout=60):
    """
    通过Paramiko SSH执行命令并返回输出

    Args:
        device_ip: 设备IP
        command: 要执行的命令
        timeout: 超时时间(秒)

    Returns:
        tuple: (stdout输出, stderr输出) 失败返回(None, None)
    """
    try:
        import paramiko
    except ImportError:
        print("[!] paramiko未安装, 请执行: pip install paramiko")
        return None, None

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device_ip, username=USERNAME, password=PASSWORD,
                    look_for_keys=False, allow_agent=False, timeout=15)

        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        ssh.close()
        return out, err

    except Exception as e:
        print(f"[!] SSH执行失败: {e}")
        return None, None


def ssh_exec_interactive(device_ip, commands, timeout=60):
    """
    通过Paramiko SSH发送交互式CLI命令 (用于configure terminal等)

    Args:
        device_ip: 设备IP
        commands: CLI命令列表
        timeout: 超时时间(秒)

    Returns:
        str: 命令输出, 失败返回None
    """
    try:
        import paramiko
    except ImportError:
        print("[!] paramiko未安装, 请执行: pip install paramiko")
        return None

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device_ip, username=USERNAME, password=PASSWORD,
                    look_for_keys=False, allow_agent=False, timeout=15)

        # 使用invoke_shell进行交互式会话
        shell = ssh.invoke_shell()
        shell.settimeout(timeout)

        # 等待提示符
        time.sleep(1)
        output = shell.recv(65535).decode('utf-8', errors='replace')

        for cmd in commands:
            shell.send(cmd + '\n')
            time.sleep(0.5)

        # 等待所有输出
        time.sleep(3)
        if shell.recv_ready():
            output += shell.recv(65535).decode('utf-8', errors='replace')

        ssh.close()
        return output

    except Exception as e:
        print(f"[!] SSH交互式执行失败: {e}")
        return None


def scp_upload(device_ip, local_path, remote_name):
    """
    通过SCP上传文件到设备bootflash

    Args:
        device_ip: 设备IP
        local_path: 本地文件路径
        remote_name: 远程文件名

    Returns:
        bool: 成功返回True
    """
    try:
        import paramiko
    except ImportError:
        return False

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device_ip, username=USERNAME, password=PASSWORD,
                    look_for_keys=False, allow_agent=False, timeout=15)

        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_name)
        sftp.close()
        ssh.close()
        return True
    except Exception as e:
        print(f"[!] SCP上传失败: {e}")
        return False


# ==================== Step 1: 部署脚本到Guestshell ====================

def deploy_scripts():
    """部署qyt_smtp_attachment.py和bgp_threshold_notification.py到R1 Guestshell"""
    print(f"\n{'=' * 60}")
    print("Step 1: 部署脚本到R1 Guestshell")
    print(f"{'=' * 60}")

    scripts = ['qyt_smtp_attachment.py', 'bgp_threshold_notification.py']
    all_ok = True

    for script_name in scripts:
        local_path = os.path.join(LOCAL_DIR, script_name)

        if not os.path.exists(local_path):
            print(f"  [-] 本地文件不存在: {local_path}")
            all_ok = False
            continue

        print(f"\n  [*] 部署 {script_name}...")

        # SCP上传到bootflash
        if not scp_upload(R1_IP, local_path, script_name):
            print(f"  [-] SCP上传失败")
            all_ok = False
            continue

        # 从bootflash复制到Guestshell
        copy_cmd = (f"guestshell run bash -c "
                    f"'cp /bootflash/{script_name} /home/guestshell/ "
                    f"&& chmod +x /home/guestshell/{script_name}'")
        out, err = ssh_exec(R1_IP, copy_cmd)

        # 验证
        verify_cmd = f"guestshell run bash -c 'ls -la /home/guestshell/{script_name}'"
        out, err = ssh_exec(R1_IP, verify_cmd)
        if out and script_name in out:
            print(f"  [+] {script_name} 部署成功")
        else:
            print(f"  [-] {script_name} 部署可能失败")
            all_ok = False

    return all_ok


# ==================== Step 2: 手工测试Guestshell脚本 ====================

def manual_test():
    """
    手工测试bgp_threshold_notification.py
    在R1上执行: guestshell run python3 /home/guestshell/bgp_threshold_notification.py
                received from 10.10.1.201 : 2 exceeds limit 2
    """
    print(f"\n{'=' * 60}")
    print("Step 2: 手工测试Guestshell脚本")
    print(f"{'=' * 60}")

    test_cmd = (f"guestshell run python3 {GUESTSHELL_SCRIPT} "
                f"received from {R2_IP} : 2 exceeds limit 2")

    print(f"\n[*] 执行命令:")
    print(f"    {test_cmd}")
    print(f"\n[*] 等待脚本执行 (SMTP连接可能需要几秒)...")

    out, err = ssh_exec(R1_IP, test_cmd, timeout=90)

    print(f"\n--- 输出结果 ---")
    if out:
        print(out)
    if err:
        print(f"[stderr] {err}")

    # 判断结果
    if out:
        if '邮件已经成功发出' in out:
            print(f"\n[+] 手工测试成功! 邮件已发送!")
            print(f"    请检查收件箱 {R1_IP} 的邮件")
            print(f"    期望邮件正文:")
            print(f"      Neighbor: {R2_IP}")
            print(f"      Now: 2")
            print(f"      Exceed the limit: 2")
            return True
        elif '无法从参数中提取' in out:
            print(f"\n[-] 手工测试失败: 正则匹配参数失败")
            print(f"    请检查EEM传入的参数格式")
            return False
        elif 'Failed recipients' in out:
            print(f"\n[-] 邮件发送部分失败: 有收件人被拒绝")
            return False
        elif 'smtplib' in (out + (err or '')).lower():
            print(f"\n[-] SMTP连接失败, 可能原因:")
            print(f"    1. Guestshell无法访问smtp.qq.com:465")
            print(f"    2. 路由器DNS解析失败")
            print(f"    3. 邮箱授权码错误")
            return False
        else:
            print(f"\n[?] 测试结果未知, 请检查上方输出")
            return False
    else:
        print(f"\n[-] 未获取到输出")
        return False


# ==================== Step 3: 触发真实BGP告警 ====================

def trigger_bgp_alert():
    """
    触发真实BGP前缀阈值告警
    方法: 在R1上执行 clear ip bgp * out 重置出站BGP会话
    R2重新发布前缀后, R1再次收到2条前缀, 触发MAXPFX SYSLOG
    """
    print(f"\n{'=' * 60}")
    print("Step 3: 触发真实BGP告警")
    print(f"{'=' * 60}")

    print(f"\n[*] 在R1上重置BGP会话 (clear ip bgp * out)...")
    print(f"    这将使R2重新发布前缀给R1, 触发MAXPFX SYSLOG")

    # 使用enable模式的命令
    commands = [
        'enable',
        'clear ip bgp * out',
    ]

    # 通过exec_command执行 (需要特权模式)
    # 使用 guestshell 的方式可能更可靠
    clear_cmd = "clear ip bgp * out"
    out, err = ssh_exec(R1_IP, f"enable\n{clear_cmd}", timeout=30)

    print(f"    命令已发送")

    # 等待BGP重新建立和SYSLOG产生
    print(f"\n[*] 等待BGP重新建立 (15秒)...")
    for i in range(15, 0, -5):
        print(f"    等待中... {i}秒")
        time.sleep(5)

    return True


# ==================== Step 4: 验证EEM和SYSLOG ====================

def verify_eem():
    """验证EEM Applet注册状态"""
    print(f"\n{'=' * 60}")
    print("Step 4a: 验证EEM Applet注册状态")
    print(f"{'=' * 60}")

    print(f"\n[*] 查询EEM注册策略...")
    out, err = ssh_exec(R1_IP, "show event manager policy registered", timeout=15)

    if out:
        if 'bgp_prefix_threshold_notification' in out:
            print(f"[+] EEM Applet 'bgp_prefix_threshold_notification' 已注册!")
            # 显示相关部分
            lines = out.split('\n')
            in_applet = False
            for line in lines:
                if 'bgp_prefix_threshold_notification' in line:
                    in_applet = True
                if in_applet:
                    print(f"    {line.strip()}")
                    if line.strip() == '' and in_applet:
                        break
        else:
            print(f"[-] EEM Applet未注册, 请检查配置")
    else:
        print(f"[-] 无法获取EEM状态")

    return out


def verify_syslog():
    """验证SYSLOG中的BGP MAXPFX和EEM相关日志"""
    print(f"\n{'=' * 60}")
    print("Step 4b: 验证SYSLOG日志")
    print(f"{'=' * 60}")

    print(f"\n[*] 查询BGP MAXPFX和EEM相关SYSLOG...")
    show_cmd = "show logging | include BGP-4-MAXPFX|bgp neighbor|current prefixes|max prefixes"
    out, err = ssh_exec(R1_IP, show_cmd, timeout=15)

    if out:
        print(f"\n--- SYSLOG输出 ---")
        print(out)

        if 'BGP-4-MAXPFX' in out:
            print(f"[+] 发现 %BGP-4-MAXPFX SYSLOG日志!")
        else:
            print(f"[-] 未发现 %BGP-4-MAXPFX 日志")
            print(f"    可能原因: BGP邻居尚未重新建立, 或maximum-prefix未触发")
            print(f"    尝试在R1上执行: clear ip bgp * out")

        if 'bgp neighbor:' in out:
            print(f"[+] EEM regexp提取成功 - 发现 'bgp neighbor' 日志")
        if 'current prefixes:' in out:
            print(f"[+] EEM regexp提取成功 - 发现 'current prefixes' 日志")
        if 'max prefixes:' in out:
            print(f"[+] EEM regexp提取成功 - 发现 'max prefixes' 日志")
    else:
        print(f"[-] 无法获取SYSLOG")

    return out


def verify_bgp_neighbors():
    """验证BGP邻居状态"""
    print(f"\n{'=' * 60}")
    print("Step 4c: 验证BGP邻居状态")
    print(f"{'=' * 60}")

    print(f"\n[*] 查询R1 BGP邻居状态...")
    out, err = ssh_exec(R1_IP, "show ip bgp summary", timeout=15)

    if out:
        print(out)
    else:
        print(f"[-] 无法获取BGP状态")

    return out


# ==================== 输出手工操作指南 ====================

def print_manual_guide():
    """打印手工操作指南 (当自动脚本无法执行时使用)"""
    print(f"\n{'=' * 60}")
    print("手工操作指南 (在R1 CLI中执行)")
    print(f"{'=' * 60}")
    print(f"""
====================================
 1. 手工测试Guestshell脚本
====================================
  R1# guestshell run python3 {GUESTSHELL_SCRIPT} received from {R2_IP} : 2 exceeds limit 2

  期望输出:
    [!] BGP前缀阈值告警!
        BGP邻居: {R2_IP}
        当前前缀数: 2
        最大前缀阈值: 2
    [+] 邮件已经成功发出！

  期望收到的邮件正文:
    Neighbor: {R2_IP}
    Now: 2
    Exceed the limit: 2


====================================
 2. 触发真实BGP告警
====================================
  R1# clear ip bgp * out

  (等待BGP重新建立, R2再次发布2条前缀, 触发MAXPFX SYSLOG)


====================================
 3. 验证EEM和SYSLOG
====================================
  ! 查看EEM Applet是否注册
  R1# show event manager policy registered

  ! 查看BGP MAXPFX和EEM提取的SYSLOG
  R1# show logging | include BGP-4-MAXPFX|bgp neighbor|current prefixes|max prefixes

  ! 查看BGP邻居状态
  R1# show ip bgp summary

  ! 查看BGP邻居详细信息 (含maximum-prefix)
  R1# show ip bgp neighbors {R2_IP}


====================================
 4. 故障排查
====================================
  ! 检查Guestshell是否启用
  R1# show iox

  ! 检查Guestshell中的Python脚本
  R1# guestshell run bash -c "ls -la /home/guestshell/"

  ! 检查Guestshell网络连通性 (能否访问SMTP服务器)
  R1# guestshell run bash -c "python3 -c \\"import socket; s=socket.create_connection(('smtp.qq.com',465),timeout=10); print('SMTP OK'); s.close()\\""

  ! 手动部署脚本 (如果SCP方式失败)
  R1# guestshell run bash
  [guestshell]$ vi /home/guestshell/qyt_smtp_attachment.py
  [guestshell]$ vi /home/guestshell/bgp_threshold_notification.py
  [guestshell]$ chmod +x /home/guestshell/qyt_smtp_attachment.py /home/guestshell/bgp_threshold_notification.py
""")


# ==================== 主程序 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("DAY8 任务四: 手工测试Python脚本 + 触发真实BGP告警")
    print("=" * 60)
    print(f"R1: {R1_IP}  (EEM + Guestshell)")
    print(f"R2: {R2_IP}  (BGP邻居)")
    print(f"Guestshell脚本: {GUESTSHELL_SCRIPT}")

    # ===== Step 1: 部署脚本 =====
    deploy_ok = deploy_scripts()
    if not deploy_ok:
        print("\n[!] 脚本部署可能不完整, 继续后续步骤...")

    # ===== Step 2: 手工测试 =====
    test_ok = manual_test()

    if test_ok:
        print(f"\n[+] 手工测试通过! 邮件已发送")
        print(f"    请检查收件箱确认邮件内容")

        # ===== Step 3: 触发真实BGP告警 =====
        print(f"\n{'=' * 60}")
        print("准备触发真实BGP告警...")
        print(f"{'=' * 60}")
        print(f"这将重置R1的BGP会话, 确认要继续吗?")
        print(f"(EEM将捕获MAXPFX SYSLOG并自动调用Guestshell脚本发送邮件)")

        # 自动触发
        trigger_ok = trigger_bgp_alert()

        if trigger_ok:
            # ===== Step 4: 验证 =====
            verify_eem()
            verify_syslog()
            verify_bgp_neighbors()

    else:
        print(f"\n[-] 手工测试未通过, 请先排查问题:")
        print(f"    1. 确认Guestshell脚本已正确部署")
        print(f"    2. 确认Guestshell能访问smtp.qq.com:465")
        print(f"    3. 确认SMTP邮箱授权码正确")

    # ===== 输出手动操作指南 =====
    print_manual_guide()

    print(f"\n{'=' * 60}")
    print("任务四完成!")
    print("如果手工测试和真实BGP告警都触发成功,")
    print("请检查邮箱确认收到告警邮件")
    print(f"{'=' * 60}")
