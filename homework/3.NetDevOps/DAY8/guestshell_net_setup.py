#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""Guestshell网络自修复脚本 - 用ioctl给eth0配IP和路由"""
import struct, socket, fcntl, os

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 设置IP 192.168.1.2
fcntl.ioctl(s.fileno(), 0x8916, struct.pack('256s2h8s', b'eth0', 2, 0, socket.inet_aton('192.168.1.2')))

# 设置掩码 255.255.255.0
fcntl.ioctl(s.fileno(), 0x891c, struct.pack('256s2h8s', b'eth0', 2, 0, socket.inet_aton('255.255.255.0')))

# 验证IP
ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', b'eth0'))[20:24])
print('eth0 IP: ' + ip)

# 添加默认路由 via 192.168.1.1
rt = struct.pack('16s2H4s4s4s4s4s4s4s4sH',
    b'eth0',                    # iface
    2,                          # AF_INET
    0,                          # flags
    socket.inet_aton('0.0.0.0'),      # dst
    socket.inet_aton('192.168.1.1'),  # gateway
    socket.inet_aton('0.0.0.0'),      # genmask (not used for default)
    socket.inet_aton('255.255.255.255'),  # genmask
    b'\x00'*4, b'\x00'*4, b'\x00'*4,  # padding
    0)                          # metric
try:
    fcntl.ioctl(s.fileno(), 0x890B, rt)
    print('route added OK')
except Exception as e:
    print('route err: ' + str(e))

# 测试SMTP连通性
try:
    s2 = socket.create_connection(('120.233.18.201', 465), timeout=10)
    print('SMTP_OK')
    s2.close()
except Exception as e:
    print('SMTP_FAIL: ' + str(e))

s.close()
