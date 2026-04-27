# 单独的测试脚本：验证Paramiko安装和SSH连接
import paramiko

# 创建SSH客户端对象
ssh = paramiko.SSHClient()
# 自动添加主机密钥
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 连接SSH服务器（按你实际环境修改IP/密码）
ssh.connect(
    '192.168.72.130',
    port=22,
    username='root',
    password='123123',
    timeout=5,
    look_for_keys=False,
    allow_agent=False
)
# 执行hostname命令
stdin, stdout, stderr = ssh.exec_command('hostname')
# 打印输出
print(stdout.read().decode())
# 关闭连接
ssh.close()