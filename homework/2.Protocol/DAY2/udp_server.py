'''
设计一个自己的UDP协议!用于传输各种Python数据
协议字段设计

# ---header设计---
# 2 字节 版本 1
# 2 字节 类型 1 为请求 2 为响应(由于是UDP单向流量!所有此次试验只有请求)
# 4 字节 ID号
# 8 字节 长度

# ---变长数据部分---总长度控制为512
# 使用pickle转换数据

# ---HASH校验---
# 16 字节 MD5值
'''

import socket
import sys
import struct
import hashlib
import pickle

# 绑定到所有网卡的6666端口
address = ('0.0.0.0', 6666)
# 创建UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 绑定地址
s.bind(address)

print('UDP服务器就绪!等待客户数据!')

while True:
    try:
        # ======================
        # 1. 接收客户端数据包
        # ======================
        # 限制最大接收512字节（符合题目要求）
        recv_source_data = s.recvfrom(512)
        # 分离数据和客户端地址
        rdata, addr = recv_source_data

        # ======================
        # 2. 解析协议头部（前16字节）
        # ======================
        header = rdata[:16]
        # 解包头部，格式和客户端完全一致
        version, pkt_type, seq_id, length = struct.unpack('!HHIQ', header)

        # ======================
        # 3. 分离数据部分和MD5校验部分
        # ======================
        # 数据部分：从16字节到倒数16字节
        data = rdata[16:-16]
        # MD5校验部分：最后16字节
        md5_recv = rdata[-16:]

        # ======================
        # 4. 本地计算MD5进行校验
        # ======================
        md5_value = hashlib.md5(header + data).digest()

        # ======================
        # 5. 校验通过则打印数据
        # ======================
        if md5_recv == md5_value:
            print('=' * 80)
            print("{0:<30}:{1:<30}".format("数据源自于", str(addr)))
            print("{0:<30}:{1:<30}".format("数据序列号", seq_id))
            print("{0:<30}:{1:<30}".format("数据长度为", length))
            # 反序列化二进制数据为Python对象
            print("{0:<30}:{1:<30}".format("数据内容为", str(pickle.loads(data))))
        else:
            print('MD5校验错误!')

    except KeyboardInterrupt:
        # 按Ctrl+C退出
        sys.exit()