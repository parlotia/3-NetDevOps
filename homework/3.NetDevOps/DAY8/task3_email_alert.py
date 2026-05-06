"""
=================================================================
NetDevOps DAY8 任务三: 编写Guestshell中的Python邮件告警脚本
=================================================================
场景: 将两个Python脚本部署到R1的Guestshell:
      1. qyt_smtp_attachment.py - SMTP邮件发送工具 (复用课程代码)
      2. bgp_threshold_notification.py - BGP前缀阈值告警脚本
         接收EEM传入的参数, 用re.match提取BGP邻居IP、当前前缀数、
         最大前缀阈值, 然后调用qyt_smtp_attachment发送告警邮件

环境信息:
  R1 (C8KV-1): 10.10.1.200  Guestshell脚本部署目标
  SMTP服务器:  smtp.qq.com (SSL端口465)

EEM -> Guestshell 调用链:
  EEM捕获 %BGP-4-MAXPFX SYSLOG
  → regexp提取 ipaddr, current_prefix, max_prefix
  → action 6.0: guestshell run python3 /home/guestshell/bgp_threshold_notification.py
                 received from $ipaddr : $current_prefix exceeds limit $max_prefix
  → bgp_threshold_notification.py 用re.match解析参数
  → 调用qyt_smtp_attachment()发送告警邮件

部署方式: SCP上传到R1 bootflash, 再复制到Guestshell
=================================================================
"""

import os
import sys

# ==================== 设备信息 ====================
R1_IP = '10.10.1.200'
USERNAME = 'admin'
PASSWORD = 'Cisc0123'

# Guestshell脚本路径
GUESTSHELL_HOME = '/home/guestshell'
SCRIPTS_TO_DEPLOY = [
    'qyt_smtp_attachment.py',
    'bgp_threshold_notification.py',
]

# 本地脚本目录
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))


# ==================== 部署函数 ====================

def deploy_scripts_scp():
    """
    通过SCP将脚本上传到R1 bootflash, 再复制到Guestshell

    Returns:
        bool: 全部成功返回True, 任意失败返回False
    """
    try:
        import paramiko
    except ImportError:
        print("[!] paramiko未安装, 请执行: pip install paramiko")
        return False

    all_ok = True

    for script_name in SCRIPTS_TO_DEPLOY:
        local_path = os.path.join(LOCAL_DIR, script_name)
        remote_guestshell_path = f'{GUESTSHELL_HOME}/{script_name}'

        if not os.path.exists(local_path):
            print(f"[-] 本地脚本不存在: {local_path}")
            all_ok = False
            continue

        print(f"\n{'=' * 60}")
        print(f"部署: {script_name}")
        print(f"  本地:   {local_path}")
        print(f"  目标:   {remote_guestshell_path}")
        print(f"{'=' * 60}")

        try:
            # Step 1: SSH连接
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(R1_IP, username=USERNAME, password=PASSWORD,
                        look_for_keys=False, allow_agent=False, timeout=15)

            # Step 2: SCP上传到bootflash
            print(f"  [1/3] SCP上传到bootflash...")
            sftp = ssh.open_sftp()
            sftp.put(local_path, script_name)
            sftp.close()
            print(f"  [+] 上传成功: bootflash:{script_name}")

            # Step 3: 从bootflash复制到Guestshell
            print(f"  [2/3] 复制到Guestshell...")
            copy_cmd = (f"guestshell run bash -c "
                        f"'cp /bootflash/{script_name} {remote_guestshell_path} "
                        f"&& chmod +x {remote_guestshell_path}'")
            stdin, stdout, stderr = ssh.exec_command(copy_cmd, timeout=30)
            error = stderr.read().decode('utf-8', errors='replace')

            # Step 4: 验证文件
            print(f"  [3/3] 验证文件...")
            verify_cmd = f"guestshell run bash -c 'ls -la {remote_guestshell_path}'"
            stdin, stdout, stderr = ssh.exec_command(verify_cmd, timeout=15)
            output = stdout.read().decode('utf-8', errors='replace')

            if script_name in output:
                print(f"  [+] {script_name} 部署成功!")
                print(f"      {output.strip()}")
            else:
                print(f"  [-] {script_name} 部署可能失败")
                if error:
                    print(f"      stderr: {error[:200]}")
                all_ok = False

            ssh.close()

        except Exception as e:
            print(f"  [!] {script_name} 部署异常: {e}")
            all_ok = False

    return all_ok


def test_guestshell_script():
    """
    在R1上手动测试bgp_threshold_notification.py
    通过SSH执行guestshell run命令, 模拟EEM传入参数

    Returns:
        bool: 测试成功返回True, 失败返回False
    """
    try:
        import paramiko
    except ImportError:
        print("[!] paramiko未安装, 请执行: pip install paramiko")
        return False

    print(f"\n{'=' * 60}")
    print("手动测试: bgp_threshold_notification.py")
    print("模拟EEM传入参数: received from 10.10.1.201 : 2 exceeds limit 2")
    print(f"{'=' * 60}")

    test_cmd = ("guestshell run python3 /home/guestshell/bgp_threshold_notification.py "
                "received from 10.10.1.201 : 2 exceeds limit 2")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(R1_IP, username=USERNAME, password=PASSWORD,
                    look_for_keys=False, allow_agent=False, timeout=15)

        print(f"\n[*] 执行测试命令...")
        stdin, stdout, stderr = ssh.exec_command(test_cmd, timeout=60)
        output = stdout.read().decode('utf-8', errors='replace')
        error = stderr.read().decode('utf-8', errors='replace')

        print(f"\n--- 标准输出 ---")
        print(output)
        if error:
            print(f"\n--- 标准错误 ---")
            print(error)

        # 检查邮件是否发送成功
        if '邮件已经成功发出' in output:
            print(f"[+] 测试成功! 邮件已发送")
            ssh.close()
            return True
        elif '无法从参数中提取' in output:
            print(f"[-] 测试失败: 正则匹配参数失败")
            ssh.close()
            return False
        elif 'Failed recipients' in output:
            print(f"[-] 测试部分失败: 邮件发送有部分收件人失败")
            ssh.close()
            return False
        else:
            print(f"[?] 测试结果未知, 请检查输出")
            ssh.close()
            return False

    except Exception as e:
        print(f"[!] 测试执行异常: {e}")
        return False


def print_manual_deploy_guide():
    """打印手动部署指南"""
    print(f"\n{'=' * 60}")
    print("手动部署指南")
    print(f"{'=' * 60}")
    print(f"""
方法1: SCP上传 (推荐)
------
从Linux主机执行:

  # 上传两个脚本到R1
  scp {LOCAL_DIR}/qyt_smtp_attachment.py {USERNAME}@{R1_IP}:qyt_smtp_attachment.py
  scp {LOCAL_DIR}/bgp_threshold_notification.py {USERNAME}@{R1_IP}:bgp_threshold_notification.py

然后在R1 CLI中执行:
  R1# guestshell run bash -c 'cp /bootflash/qyt_smtp_attachment.py /home/guestshell/ && chmod +x /home/guestshell/qyt_smtp_attachment.py'
  R1# guestshell run bash -c 'cp /bootflash/bgp_threshold_notification.py /home/guestshell/ && chmod +x /home/guestshell/bgp_threshold_notification.py'


方法2: 在Guestshell中直接创建
------
在R1 CLI中执行:
  R1# guestshell run bash

进入Guestshell后:
  [guestshell]$ vi /home/guestshell/qyt_smtp_attachment.py
  [guestshell]$ vi /home/guestshell/bgp_threshold_notification.py
  [guestshell]$ chmod +x /home/guestshell/qyt_smtp_attachment.py /home/guestshell/bgp_threshold_notification.py


手动测试脚本:
------
在R1 CLI中执行:
  R1# guestshell run python3 /home/guestshell/bgp_threshold_notification.py received from 10.10.1.201 : 2 exceeds limit 2

期望输出:
  [!] BGP前缀阈值告警!
      BGP邻居: 10.10.1.201
      当前前缀数: 2
      最大前缀阈值: 2
  [+] 邮件已经成功发出！
""")


# ==================== 主程序 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("DAY8 任务三: 编写Guestshell中的Python邮件告警脚本")
    print("=" * 60)
    print(f"R1: {R1_IP}")
    print(f"部署脚本:")
    for s in SCRIPTS_TO_DEPLOY:
        print(f"  - {GUESTSHELL_HOME}/{s}")

    # ===== Step 1: 检查本地脚本文件 =====
    print(f"\n{'=' * 60}")
    print("Step 1: 检查本地脚本文件")
    print(f"{'=' * 60}")
    all_exist = True
    for script_name in SCRIPTS_TO_DEPLOY:
        local_path = os.path.join(LOCAL_DIR, script_name)
        if os.path.exists(local_path):
            size = os.path.getsize(local_path)
            print(f"  [+] {script_name} ({size} bytes)")
        else:
            print(f"  [-] {script_name} 不存在!")
            all_exist = False

    if not all_exist:
        print("\n[-] 部分脚本文件缺失, 请先确认文件存在")
        sys.exit(1)

    # ===== Step 2: 部署脚本到R1 Guestshell =====
    print(f"\n{'=' * 60}")
    print("Step 2: 部署脚本到R1 Guestshell")
    print(f"{'=' * 60}")
    deploy_ok = deploy_scripts_scp()

    if not deploy_ok:
        print_manual_deploy_guide()

    # ===== Step 3: 手动测试脚本 =====
    if deploy_ok:
        print(f"\n{'=' * 60}")
        print("Step 3: 手动测试脚本 (模拟EEM调用)")
        print(f"{'=' * 60}")
        test_ok = test_guestshell_script()

        if test_ok:
            print(f"\n{'=' * 60}")
            print("[+] 任务三完成! 邮件告警脚本部署并测试成功!")
            print("=" * 60)
        else:
            print(f"\n{'=' * 60}")
            print("[!] 邮件发送可能失败, 请检查:")
            print("    1. Guestshell是否能访问smtp.qq.com:465")
            print("    2. SMTP账号密码是否正确")
            print("    3. QQ邮箱授权码是否有效")
            print("=" * 60)

    # ===== 输出手动部署指南 =====
    print_manual_deploy_guide()
