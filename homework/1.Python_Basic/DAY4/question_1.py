'''
正则表达式 + os模块：解析ifconfig并ping网关（一个脚本完成）
首先用 os.popen 执行 Linux 命令获取网卡信息:

import os
result = os.popen("ifconfig ens35").read()
如果没有 Linux 环境，可以直接使用下面的字符串作为输入:

result = """ens35: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 196.21.5.228  netmask 255.255.255.0  broadcast 196.21.5.255
        inet6 fe80::20c:29ff:fe4d:73b3  prefixlen 64  scopeid 0x20<link>
        ether 00:0c:29:4d:73:b3  txqueuelen 1000  (Ethernet)
        RX packets 13573278  bytes 13853395220 (12.9 GiB)
        RX errors 0  dropped 15  overruns 0  frame 0
        TX packets 6514517  bytes 1749699427 (1.6 GiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0"""
第一步：用正则表达式提取 IP、掩码、广播地址、MAC，使用 format() 对齐打印:

IP        : 196.21.5.228
Netmask   : 255.255.255.0
Broadcast : 196.21.5.255
MAC       : 00:0c:29:4d:73:b3
第二步：根据 IP 地址的前三段拼接网关地址（假设网关为 x.x.x.1），然后用 os.popen 执行 ping 测试:

假设网关为: 196.21.5.1
Ping 196.21.5.1 ... reachable
'''
import re
import os

#提取网卡信息
result = os.popen("ifconfig ens192").read()

#关键信息提取
pattern_inet = r'inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+netmask (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+broadcast (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
match_inet = re.search(pattern_inet, result)
ip, netmask, broadcast = match_inet.groups()
pattern_mac = r'ether ([0-9a-f:]{17})'
match_mac = re.search(pattern_mac, result)
mac = match_mac.group(1)

# 对齐打印
print("{:<10}: {}".format("IP", ip))
print("{:<10}: {}".format("Netmask", netmask))
print("{:<10}: {}".format("Broadcast", broadcast))
print("{:<10}: {}".format("MAC", mac))

#拼接网关
gateway = '.'.join(ip.split('.')[0:3]) + '.1'
print(f"\n假设网关为: {gateway}")

#执行 ping 命令
ping_cmd = f"ping -c 1 {gateway}"
ping_result = os.popen(ping_cmd).read()

#判断是否 ping 通
if "ttl=" in ping_result:
    print(f"Ping {gateway} ... reachable")
else:
    print(f"Ping {gateway} ... unreachable")