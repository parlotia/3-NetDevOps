'''
paramiko：SSH 登录 Linux 查询默认网关
安装 paramiko：

pip3 install paramiko
交互界面测试：

>>> import paramiko
>>> ssh = paramiko.SSHClient()
>>> ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
>>> ssh.connect('196.21.5.228', port=22, username='root', password='Cisc0123', timeout=5, look_for_keys=False, allow_agent=False)
>>> stdin, stdout, stderr = ssh.exec_command('hostname')
>>> print(stdout.read().decode())
AIOps
>>> ssh.close()
也可以直接粘贴运行以下脚本快速验证 paramiko 是否安装成功：

import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('196.21.5.228', port=22, username='root', password='Cisc0123', timeout=5, look_for_keys=False, allow_agent=False)
stdin, stdout, stderr = ssh.exec_command('hostname')
print(stdout.read().decode())
ssh.close()
预期输出：

AIOps
编写 Python 脚本，封装一个 SSH 执行命令的函数，然后调用该函数 SSH 登录 Linux，执行 route -n，提取并打印默认网关（Destination 为 0.0.0.0 的那一行的 Gateway 字段）：
默认网关: 196.21.5.1
代码提示: 封装函数接收 host、username、password、command 参数，返回命令输出字符串；对 route -n 输出逐行用 re.match 匹配 Destination 为 0.0.0.0 且 Flags 含 UG 的行，用正则表达式捕获组提取网关 IP。

注意：ssh.connect() 建议加上 look_for_keys=False, allow_agent=False，禁用密钥认证，避免连接非 Linux 设备（如思科路由器）时因密钥尝试失败导致认证中断。
'''

import paramiko
import re

# 封装SSH执行命令函数：接收4个参数，返回命令输出字符串（严格按题目要求）
def ssh_exec_cmd(host, username, password, command):
    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    # 自动接受未知主机密钥
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # 建立SSH连接（严格按注意事项添加参数）
    ssh.connect(
        hostname=host,
        port=22,
        username=username,
        password=password,
        timeout=5,
        look_for_keys=False,
        allow_agent=False
    )
    
    # 执行命令
    stdin, stdout, stderr = ssh.exec_command(command)
    # 读取输出并转字符串返回
    result = stdout.read().decode()
    # 关闭连接
    ssh.close()
    
    return result

# 主程序
if __name__ == "__main__":
    # 连接信息
    host = "192.168.72.130"
    username = "root"
    password = "123123"
    
    # 调用函数执行 route -n
    route_info = ssh_exec_cmd(host, username, password, "route -n")
    
    # 逐行匹配（严格按提示：re.match + 0.0.0.0 + UG + 捕获网关）
    for line in route_info.splitlines():
        # 精准正则：匹配目标网段0.0.0.0，标志位UG，捕获网关IP
        match = re.match(r"^0\.0\.0\.0\s+(\S+)\s+\S+\s+UG", line.strip())
        if match:
            gateway = match.group(1)
            print(f"默认网关: {gateway}")
            break