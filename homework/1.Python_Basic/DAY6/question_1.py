'''
字典课堂作业
把防火墙状态信息表存为字典!

注意:一定要考虑很多很多行的可能性

asa_conn = "TCP Student 192.168.189.167:32806 Teacher 137.78.5.128:65247, idle 0:00:00, bytes 74, flags UIO\n
TCP Student 192.168.189.167:80 Teacher 137.78.5.128:65233, idle 0:00:03, bytes 334516, flags UIO"
打印分析后的字典:

{('192.168.189.167', '32806', '137.78.5.128', '65247'): ('74', 'UIO'),
 ('192.168.189.167', '80', '137.78.5.128', '65233'): ('334516', 'UIO')}
键为: 源IP, 源端口, 目的IP, 目的端口；值为: 字节数, Flags

格式化打印输出（使用 format() 对齐，用 | 分隔各列）:

src       : 192.168.189.167 | src_port  : 32806  | dst       : 137.78.5.128 | dst_port  : 65247
bytes     : 74              | flags     : UIO
====================================================================================

src       : 192.168.189.167 | src_port  : 80     | dst       : 137.78.5.128 | dst_port  : 65233
bytes     : 334516          | flags     : UIO
====================================================================================
代码提示: 使用 asa_conn.split('\n') 按行遍历，re.match 提取各组，键为 (源IP, 源端口, 目的IP, 目的端口)，值为 (bytes, flags)。


'''

# 导入正则表达式模块，用来提取字符串里的信息
import re

# 防火墙的连接信息，这里可以是 1 行，也可以是 1000 行
asa_conn = """TCP Student 192.168.189.167:32806 Teacher 137.78.5.128:65247, idle 0:00:00, bytes 74, flags UIO
TCP Student 192.168.189.167:80 Teacher 137.78.5.128:65233, idle 0:00:03, bytes 334516, flags UIO"""

# 创建一个空字典，用来存放所有连接信息
conn_dict = {}

# 把长字符串按 换行符 切成一行一行的列表
# 这样就能循环处理每一行，支持无数行
lines = asa_conn.split('\n')

# 开始循环，一行一行处理
for line in lines:

    # 用正则表达式匹配这一行，把需要的信息都抓出来
    # (\S+) = 抓一段没有空格的内容（IP、端口等）
    match = re.match(r'TCP Student (\S+):(\S+) Teacher (\S+):(\S+).*bytes (\d+), flags (\S+)', line)

    # 把正则抓到的 6 个内容，按顺序赋值给变量
    src_ip, src_port, dst_ip, dst_port, bytes_, flags = match.groups()

    # 拼接字典的 键：(源IP, 源端口, 目标IP, 目标端口)
    key = (src_ip, src_port, dst_ip, dst_port)

    # 拼接字典的 值：(字节数, flags状态)
    value = (bytes_, flags)

    # 把 键值对 存入字典
    conn_dict[key] = value

# 打印最终的字典
print(conn_dict)
print("=" * 80)  # 打印分割线

# 循环遍历字典，格式化输出每一条连接
for key, value in conn_dict.items():

    # 把键里的内容拆出来
    src_ip, src_port, dst_ip, dst_port = key
    bytes_, flags = value

    # 用 format 对齐打印第一行
    print("{:<10}: {:<18} | {:<10}: {:<6} | {:<10}: {:<15} | {:<10}: {:<6}".format(
        "src", src_ip, "src_port", src_port, "dst", dst_ip, "dst_port", dst_port
    ))

    # 打印字节数和状态
    print("{:<10}: {:<18} | {:<10}: {:<6}".format("bytes", bytes_, "flags", flags))

    # 打印分割线
    print("=" * 80)