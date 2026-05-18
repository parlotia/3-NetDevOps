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
import struct
import hashlib
import pickle

def udp_send_data(ip, port, data_list):
    """
    自定义UDP协议发送数据
    协议结构：
    [头部(16字节)] + [变长数据] + [MD5校验(16字节)]
    头部格式：2字节版本 + 2字节类型 + 4字节ID + 8字节长度
    """
    # 目标服务器地址和端口
    address = (ip, port)
    # 创建UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 协议固定字段
    version = 1       # 协议版本号
    pkt_type = 1      # 1=请求，2=响应（本次实验只有请求）
    seq_id = 1        # 数据包序列号，从1开始递增

    # 循环发送数据列表中的每个元素
    for x in data_list:
        # ======================
        # 1. 序列化Python数据为二进制
        # ======================
        # 使用pickle将任意Python对象转换为二进制字节流
        send_data = pickle.dumps(x)

        # ======================
        # 2. 构造协议头部（16字节）
        # ======================
        # struct.pack格式说明：
        # ! ：使用网络字节序（大端）
        # H ：2字节无符号短整数
        # I ：4字节无符号整数
        # Q ：8字节无符号长整数
        header = struct.pack(
            '!HHIQ',
            version,    # 2字节 版本号
            pkt_type,   # 2字节 包类型
            seq_id,     # 4字节 序列号
            len(send_data)  # 8字节 数据部分长度
        )

        # ======================
        # 3. 计算MD5校验值
        # ======================
        # 对【头部+数据】整体计算MD5，确保完整性
        md5_hash = hashlib.md5(header + send_data).digest()

        # ======================
        # 4. 拼接完整数据包并发送
        # ======================
        full_packet = header + send_data + md5_hash
        s.sendto(full_packet, address)

        # 序列号自增
        seq_id += 1

    # 关闭socket
    s.close()

if __name__ == '__main__':
    from datetime import datetime
    # 测试数据：包含字符串、列表、字典、datetime对象
    user_data = ['乾颐堂', [1, 'qytang', 3], {'qytang': 1, 'test': 3}, {'datetime': datetime.now()}]
    # 发送到服务器
    udp_send_data('10.10.1.205', 6666, user_data)