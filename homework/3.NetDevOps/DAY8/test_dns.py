#!/usr/bin/env python3
# -*- coding=utf-8 -*-
import sys, io, socket

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Step 1: 修复DNS
with open('/etc/resolv.conf', 'w') as f:
    f.write('nameserver 8.8.8.8\n')
print('DNS written')

# Step 2: 测试解析
try:
    addr = socket.getaddrinfo('smtp.qq.com', 465)[0][4]
    print(f'Resolve OK: {addr}')
except Exception as e:
    print(f'Resolve FAIL: {e}')

# Step 3: 测试SMTP连接
try:
    s = socket.create_connection(('smtp.qq.com', 465), timeout=10)
    print('SMTP OK')
    s.close()
except Exception as e:
    print(f'SMTP FAIL: {e}')
