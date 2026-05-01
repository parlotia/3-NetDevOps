'''
任务二：为 SSH 登录脚本配置命令行选项
使用 argparse 模块，为第九天的 SSH 登录脚本添加命令行参数。要求支持以下参数：

-i 或 --ip：设备的 IP 地址（必填）
-u 或 --username：登录用户名（必填）
-p 或 --password：登录密码（必填）
-c 或 --cmd：要执行的命令（必填）
代码提示（可以参考以下框架）：

import argparse
import paramiko

def ssh_run(host, username, password, command):
    """通过 paramiko 执行 SSH 命令并返回结果"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port=22, username=username, password=password, timeout=5,
                look_for_keys=False, allow_agent=False)
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode()
    ssh.close()
    return result

def main():
    parser = argparse.ArgumentParser(description='网络设备 SSH 命令执行工具')
    
    # 添加四个参数：-i/--ip, -u/--username, -p/--password, -c/--cmd
    # ??? 你的代码写在这里 ???
    
    args = parser.parse_args()
    
    # 调用 ssh_run 函数执行命令，并打印结果
    # ??? 你的代码写在这里 ???

if __name__ == '__main__':
    main()
期望输出示例（在终端中执行）：
$ python day14_task02_ssh_argparse.py -h
usage: day14_task02_ssh_argparse.py [-h] -i IP -u USERNAME -p PASSWORD -c CMD

网络设备 SSH 命令执行工具

options:
  -h, --help            show this help message and exit
  -i IP, --ip IP        设备的 IP 地址
  -u USERNAME, --username USERNAME
                        登录用户名
  -p PASSWORD, --password PASSWORD
                        登录密码
  -c CMD, --cmd CMD     要执行的命令

$ python day14_task02_ssh_argparse.py -i 196.21.5.211 -u admin -p Cisc0123 -c "show ip inter brief"

Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet1       196.21.5.211    YES NVRAM  up                    up      
GigabitEthernet2       172.16.1.12     YES manual administratively down down    
GigabitEthernet3       unassigned      YES TFTP   administratively down down    
Loopback13             13.13.13.13     YES manual up                    up      
'''
import argparse
import paramiko

def ssh_run(host, username, password, command):
    """
    通过 paramiko 执行 SSH 命令并返回结果
    参数：
        host: 设备IP
        username: 登录用户名
        password: 登录密码
        command: 要执行的命令
    """
    # 创建SSH客户端对象
    ssh = paramiko.SSHClient()
    # 自动接受主机密钥，避免首次连接报错
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # 连接设备
    ssh.connect(
        host, 
        port=22, 
        username=username, 
        password=password, 
        timeout=5,
        look_for_keys=False,  # 不使用本地密钥文件
        allow_agent=False     # 不使用SSH代理
    )
    
    # 执行命令，返回三个对象：输入、输出、错误
    stdin, stdout, stderr = ssh.exec_command(command)
    # 读取输出结果，并解码成字符串
    result = stdout.read().decode()
    # 关闭SSH连接
    ssh.close()
    return result

def main():
    # ======================
    # 1. 创建参数解析器
    # ======================
    parser = argparse.ArgumentParser(description='网络设备 SSH 命令执行工具')
    
    # ======================
    # 2. 添加四个必填参数
    # ======================
    # -i 或 --ip：设备IP
    parser.add_argument('-i', '--ip', required=True, help='设备的 IP 地址')
    # -u 或 --username：用户名
    parser.add_argument('-u', '--username', required=True, help='登录用户名')
    # -p 或 --password：密码
    parser.add_argument('-p', '--password', required=True, help='登录密码')
    # -c 或 --cmd：要执行的命令
    parser.add_argument('-c', '--cmd', required=True, help='要执行的命令')
    
    # ======================
    # 3. 解析命令行输入
    # ======================
    args = parser.parse_args()
    
    # ======================
    # 4. 调用函数执行命令并打印
    # ======================
    output = ssh_run(args.ip, args.username, args.password, args.cmd)
    print(output)

if __name__ == '__main__':
    main()