'''
正则表达式测试 2：解析ASA防火墙连接表
字符串为ASA防火墙 show conn 输出:

conn = 'TCP server  172.16.1.101:443 localserver  172.16.66.1:53710, idle 0:01:09, bytes 27575949, flags UIO'
使用正则表达式匹配，提取出协议、目标IP、目标端口、源IP、源端口，使用 format() 对齐后打印结果如下:

Protocol    : TCP
Server IP   : 172.16.1.101
Server Port : 443
Client IP   : 172.16.66.1
Client Port : 53710
'''

import re

info = 'TCP server  172.16.1.101:443 localserver  172.16.66.1:53710, idle 0:01:09, bytes 27575949, flags UIO'

ip = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'


pattern = rf'(\S+)\s+server\s+({ip}):(\d+)\s+localserver\s+({ip}):(\d+)'

protocol, server_ip, server_port, client_ip, client_port = re.search(pattern, info).groups()

print("{:<15}: {}".format("Protocol", protocol))
print("{:<15}: {}".format("Server IP", server_ip))
print("{:<15}: {}".format("Server Port", server_port))
print("{:<15}: {}".format("Client IP", client_ip))
print("{:<15}: {}".format("Client Port", client_port))