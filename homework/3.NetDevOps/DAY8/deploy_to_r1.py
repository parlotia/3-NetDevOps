#!/usr/bin/env python3
"""
一键部署DAY8 BGP告警脚本到R1 (10.10.1.200)
1. 启用IOx和Guestshell
2. SCP上传脚本到bootflash
3. 复制到Guestshell
4. 手工测试验证
"""

import paramiko
import time
import os
import sys

R1_IP = '10.10.1.200'
USERNAME = 'admin'
PASSWORD = 'Cisc0123'

SCRIPTS = [
    'qyt_smtp_attachment.py',
    'bgp_threshold_notification.py',
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def ssh_exec(cmd, timeout=90):
    """执行单条SSH命令并返回输出"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(R1_IP, username=USERNAME, password=PASSWORD,
                look_for_keys=False, allow_agent=False, timeout=15)
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    ssh.close()
    return out, err


def interactive_shell(commands, wait_per_cmd=5):
    """交互式shell执行多条命令"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(R1_IP, username=USERNAME, password=PASSWORD,
                look_for_keys=False, allow_agent=False, timeout=15)
    shell = ssh.invoke_shell()
    shell.settimeout(120)
    time.sleep(2)
    shell.recv(4096)  # 清空欢迎信息

    results = []
    for cmd, wait in commands:
        print(f'  > {cmd}')
        shell.send(cmd + '\n')
        time.sleep(wait)
        out = shell.recv(65535).decode('utf-8', errors='replace')
        results.append(out)
        # 显示关键输出
        for line in out.split('\n'):
            line = line.strip()
            if line and 'C8Kv1' not in line and cmd not in line:
                print(f'    {line}')

    shell.close()
    ssh.close()
    return results


def scp_upload(local_path, remote_name):
    """SCP上传文件到R1 bootflash"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(R1_IP, username=USERNAME, password=PASSWORD,
                look_for_keys=False, allow_agent=False, timeout=15)

    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_name)
    sftp.close()
    ssh.close()


def step1_enable_iox_guestshell():
    """Step 1: 启用IOx和Guestshell"""
    print('\n' + '='*60)
    print('Step 1: 启用IOx和Guestshell')
    print('='*60)

    # 先检查IOx是否已启用
    out, err = ssh_exec('show iox', timeout=15)
    if 'Running' in out:
        print('[+] IOx已在运行')
    else:
        print('[*] 启用IOx...')
        interactive_shell([
            ('configure terminal', 2),
            ('iox', 5),
            ('end', 2),
        ], wait_per_cmd=3)
        print('[*] 等待IOx初始化 (60秒)...')
        time.sleep(60)
        out, err = ssh_exec('show iox', timeout=15)
        if 'Running' in out:
            print('[+] IOx已启用成功')
        else:
            print('[-] IOx启用可能失败')
            print(f'    {out.strip()[:200]}')

    # 检查Guestshell状态
    out, err = ssh_exec('guestshell run bash -c "echo GS_OK"', timeout=30)
    if 'GS_OK' in out:
        print('[+] Guestshell已可用')
        return True

    # 需要启用Guestshell - 先配置app-hosting接口
    print('[*] 配置app-hosting接口并启用Guestshell...')
    interactive_shell([
        ('configure terminal', 2),
        ('app-hosting appid guestshell', 2),
        ('app-vnic gateway1 virtualportgroup0 interface GigabitEthernet1', 2),
        ('end', 2),
        ('guestshell enable', 30),
    ], wait_per_cmd=5)

    print('[*] 等待Guestshell初始化 (90秒)...')
    time.sleep(90)

    # 验证
    out, err = ssh_exec('guestshell run bash -c "echo GS_OK"', timeout=30)
    if 'GS_OK' in out:
        print('[+] Guestshell已启用成功!')
        return True
    else:
        print(f'[-] Guestshell仍不可用: {out.strip()[:200]}')
        print('    尝试不带接口配置直接启用...')
        interactive_shell([
            ('guestshell enable', 30),
        ], wait_per_cmd=5)
        time.sleep(60)

        out, err = ssh_exec('guestshell run bash -c "echo GS_OK"', timeout=30)
        if 'GS_OK' in out:
            print('[+] Guestshell已启用成功!')
            return True
        else:
            print(f'[-] Guestshell启用失败: {out.strip()[:200]}')
            return False


def step2_scp_upload():
    """Step 2: SCP上传脚本到bootflash"""
    print('\n' + '='*60)
    print('Step 2: SCP上传脚本到R1 bootflash')
    print('='*60)

    for script in SCRIPTS:
        local_path = os.path.join(BASE_DIR, script)
        if not os.path.exists(local_path):
            print(f'[-] 本地文件不存在: {local_path}')
            return False

        try:
            scp_upload(local_path, script)
            print(f'[+] {script} SCP上传成功')
        except Exception as e:
            # SCP可能被路由器关闭, 尝试用交互式copy
            print(f'[?] SCP上传异常: {e}')
            print(f'    尝试使用base64方式写入...')
            import base64
            with open(local_path, 'r') as f:
                content = f.read()
            b64 = base64.b64encode(content.encode()).decode()

            # 分块写入
            chunk_size = 700
            chunks = [b64[i:i+chunk_size] for i in range(0, len(b64), chunk_size)]

            cmds = []
            # 第一块: 创建文件
            cmds.append((f"guestshell run bash -c 'echo {chunks[0]} | base64 -d > /home/guestshell/{script}'", 10))
            # 后续块: 追加
            for chunk in chunks[1:]:
                cmds.append((f"guestshell run bash -c 'echo {chunk} | base64 -d >> /home/guestshell/{script}'", 10))

            interactive_shell(cmds, wait_per_cmd=10)
            print(f'[+] {script} base64方式写入完成')

    return True


def step3_copy_to_guestshell():
    """Step 3: 从bootflash复制到Guestshell并验证"""
    print('\n' + '='*60)
    print('Step 3: 复制脚本到Guestshell并验证')
    print('='*60)

    # 如果文件已经在Guestshell(通过base64方式), 跳过复制
    out, err = ssh_exec('guestshell run bash -c "ls /home/guestshell/*.py"', timeout=15)
    if all(s in out for s in SCRIPTS):
        print('[+] 脚本已在Guestshell中, 跳过复制')
    else:
        # 从bootflash复制
        copy_cmds = []
        for script in SCRIPTS:
            copy_cmds.append((f"guestshell run bash -c 'cp /bootflash/{script} /home/guestshell/{script}'", 5))
        copy_cmds.append(("guestshell run bash -c 'chmod +x /home/guestshell/*.py'", 5))
        interactive_shell(copy_cmds, wait_per_cmd=5)

    # 验证文件
    out, err = ssh_exec('guestshell run bash -c "ls -la /home/guestshell/*.py"', timeout=15)
    print(f'\n[*] Guestshell中.py文件:')
    print(out)

    # 验证Python可导入
    out, err = ssh_exec(
        "guestshell run python3 -c \"import sys; sys.path.insert(0,'/home/guestshell'); from qyt_smtp_attachment import qyt_smtp_attachment; print('SMTP模块导入OK')\"",
        timeout=30
    )
    print(f'模块导入测试: {out.strip()[:100]}')
    if err:
        print(f'  stderr: {err.strip()[:200]}')

    return True


def step4_manual_test():
    """Step 4: 手工测试bgp_threshold_notification.py"""
    print('\n' + '='*60)
    print('Step 4: 手工测试bgp_threshold_notification.py')
    print('='*60)

    test_cmd = "guestshell run python3 /home/guestshell/bgp_threshold_notification.py 'received from 10.10.1.201 : 2 exceeds limit 2'"
    print(f'[*] 执行: {test_cmd}')
    out, err = ssh_exec(test_cmd, timeout=60)
    print(f'\n输出:')
    print(out)
    if err:
        print(f'stderr: {err.strip()[:200]}')

    if '邮件已经成功发出' in out or 'BGP前缀阈值告警' in out:
        print('[+] 手工测试成功! 邮件已发送!')
    else:
        print('[?] 请检查邮箱确认是否收到邮件')

    return True


if __name__ == '__main__':
    print('DAY8 BGP告警脚本 - 一键部署到R1')
    print(f'目标: {R1_IP} ({USERNAME})')

    ok = step1_enable_iox_guestshell()
    if not ok:
        print('\n[!] Guestshell未就绪, 继续尝试部署...')

    step2_scp_upload()
    step3_copy_to_guestshell()
    step4_manual_test()

    print('\n' + '='*60)
    print('部署完成! 请检查邮箱确认邮件是否收到。')
    print('='*60)
