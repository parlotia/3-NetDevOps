'''
制作一个能配置路由器的 SSH 交互函数
paramiko 交互模式测试脚本（可直接粘贴运行）：

import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('196.21.5.211', port=22, username='admin', password='Cisc0123',
            timeout=5, look_for_keys=False, allow_agent=False)

chan = ssh.invoke_shell()
time.sleep(1)
print(chan.recv(2048).decode())   # 查看登录提示符

chan.send(b'terminal length 0\n')
time.sleep(1)
print(chan.recv(2048).decode())

chan.send(b'show version\n')
time.sleep(2)
print(chan.recv(4096).decode())

chan.send(b'config ter\n')
time.sleep(1)
print(chan.recv(2048).decode())

chan.send(b'router ospf 1\n')
time.sleep(1)
print(chan.recv(2048).decode())

ssh.close()
在以上测试基础上，制作一个可执行多条命令的函数，参数设计如下：

def qytang_multicmd(ip, username, password, cmd_list, enable='', wait_time=2, verbose=True):
    """
    参数说明：
      cmd_list  : 要执行的命令列表，例如 ['terminal length 0', 'show version']
      enable    : enable 密码，若设备无需 enable 则保持默认空字符串
      wait_time : 每条命令发送后等待设备响应的秒数
      verbose   : True 则打印每条命令的返回结果，False 则静默执行
    """
测试要求：使用制作的函数，一次执行以下命令列表，打印所有返回内容：

cmd_list = [
    'terminal length 0',
    'show version',
    'config ter',
    'router ospf 1',
    'network 10.0.0.0 0.0.0.255 area 0',
    'end',
]
期望输出（节选）：

--- terminal length 0 ---
terminal length 0
C8Kv1#

--- show version ---
show version
Cisco IOS XE Software, Version 17.14.01a
Cisco IOS Software [IOSXE], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 17.14.1a, RELEASE SOFTWARE (fc1)
...
C8Kv1#

--- config ter ---
config ter
Enter configuration commands, one per line.  End with CNTL/Z.
C8Kv1(config)#

--- router ospf 1 ---
router ospf 1
C8Kv1(config-router)#

--- network 10.0.0.0 0.0.0.255 area 0 ---
network 10.0.0.0 0.0.0.255 area 0
C8Kv1(config-router)#

--- end ---
end
C8Kv1#
'''
import paramiko
import time

def qytang_multicmd(ip, username, password, cmd_list, enable='', wait_time=2, verbose=True):
    """
    可执行多条命令的思科SSH交互函数
    参数说明：
      ip        : 设备IP地址
      username  : SSH登录用户名
      password  : SSH登录密码
      cmd_list  : 要执行的命令列表，例如 ['terminal length 0', 'show version']
      enable    : enable 密码，若设备无需 enable 则保持默认空字符串
      wait_time : 每条命令发送后等待设备响应的秒数
      verbose   : True 则打印每条命令的返回结果，False 则静默执行
    """
    # 1. 创建SSH客户端对象
    ssh = paramiko.SSHClient()
    # 2. 自动添加主机密钥，避免首次连接报错
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 3. 连接设备
        ssh.connect(
            hostname=ip,
            port=22,
            username=username,
            password=password,
            timeout=5,
            look_for_keys=False,
            allow_agent=False
        )
        
        # 4. 【核心】调用 invoke_shell() 模拟真实终端交互
        chan = ssh.invoke_shell()
        # 等待终端初始化
        time.sleep(1)
        
        # 5. 处理 Enable 密码（如果提供了）
        if enable:
            # 先读取登录后的初始输出，判断是否在用户模式
            output = chan.recv(2048).decode('utf-8', errors='ignore')
            if '>' in output:
                # 发送 enable 命令
                chan.send(b'enable\n')
                time.sleep(1)
                # 发送 enable 密码
                chan.send(f'{enable}\n'.encode())
                time.sleep(1)
        
        # 6. 循环执行命令列表
        all_output = ""
        for cmd in cmd_list:
            # 发送命令（注意要加换行符 \n，模拟回车）
            chan.send(f'{cmd}\n'.encode())
            # 等待设备执行命令并返回结果
            time.sleep(wait_time)
            
            # 读取设备返回的输出
            output = chan.recv(65535).decode('utf-8', errors='ignore')
            # 累加到总输出中
            all_output += output
            
            # 如果 verbose=True，打印当前命令的输出
            if verbose:
                print(f"\n--- {cmd} ---")
                print(output)
        
        # 返回所有命令的总输出
        return all_output
        
    except Exception as e:
        print(f"连接或执行出错: {e}")
        return ""
    finally:
        # 7. 关闭SSH连接
        ssh.close()

# ==================== 测试要求：执行题目指定的命令列表 ====================
if __name__ == '__main__':
    # 填入你的设备信息
    device_ip = '196.21.5.211'
    user = 'admin'
    pwd = 'Cisc0123'
    
    # 题目要求的测试命令列表
    cmd_list = [
        'terminal length 0',
        'show version',
        'config ter',
        'router ospf 1',
        'network 10.0.0.0 0.0.0.255 area 0',
        'end',
    ]
    
    # 调用函数，执行命令并打印结果
    qytang_multicmd(
        ip=device_ip,
        username=user,
        password=pwd,
        cmd_list=cmd_list,
        enable='',          # 你的权限是15，不需要enable密码，留空即可
        wait_time=2,
        verbose=True
    )