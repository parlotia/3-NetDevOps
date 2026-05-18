import paramiko

def ssh_run(host, username, password, command, timeout=15):
    """
    思科设备SSH单命令执行函数
    返回：命令执行结果字符串
    """
    ssh = paramiko.SSHClient()
    # 自动接受设备SSH主机密钥
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 建立SSH连接
        ssh.connect(
            hostname=host,
            username=username,
            password=password,
            timeout=timeout,
            look_for_keys=False,
            allow_agent=False
        )
        # 执行命令并读取输出
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read().decode('utf-8', errors='ignore')
    
    except Exception as e:
        print(f"[!] SSH执行异常: {e}")
        return ""
    
    finally:
        # 无论是否成功，都关闭SSH连接
        ssh.close()