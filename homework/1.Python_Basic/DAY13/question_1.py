'''
面向对象：网络设备与接口配置（组合模式）
背景知识：什么是类？什么是组合？

类（class）是一个"模板"，用来创建具有相同属性和方法的对象。组合（composition）是指一个类的对象持有另一个类的对象 —— 例如"一台网络设备拥有多个接口"，设备和接口是两个独立的类，设备内部维护一个接口列表。

本次作业的整体架构：

NetworkDevice：网络设备类，保存登录信息，管理多个接口，负责批量下发配置
Interface：接口类，只保存接口数据（名称、IP、掩码、描述、状态），不负责下发
通过 device.add_interface(iface) 将接口加入设备，由 device.apply() 一次性下发所有接口配置
前置条件：需要导入第十二天的 qytang_multicmd 函数：

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from day12.day12_task01_multicmd import qytang_multicmd

任务一：完成 Interface 接口类（填写 ??? 部分）

Interface 只负责存储数据和打印自身信息，不负责下发配置。请补全 __init__ 中的默认值和 __str__ 中的两个条件判断：

class Interface:
    """接口配置类，只保存接口数据"""
    def __init__(self, name):
        self.name = name
        self.device = ???        # 所属设备，默认未绑定
        self.ip_address = ???    # IP 地址，默认空字符串
        self.mask = ???          # 子网掩码，默认空字符串
        self.description = ???   # 接口描述，默认空字符串
        self.status = ???        # True=no shutdown, False=shutdown，默认关闭

    def __str__(self):
        """格式化打印接口信息"""
        status_str = ???  # 如果 self.status 为 True 则为 'no shutdown'，否则为 'shutdown'
        device_ip = ???   # 如果 self.device 存在则取 self.device.ip，否则显示 '未绑定设备'
        lines = [
            f"接口名称    : {self.name}",
            f"所属设备    : {device_ip}",
            f"IP 地址     : {self.ip_address} {self.mask}",
            f"描述        : {self.description}",
            f"状态        : {status_str}",
        ]
        return '\n'.join(lines)

任务二：完成 NetworkDevice 网络设备类（填写 ??? 部分）

设备类管理多个接口，add_interface 建立双向关联，apply 遍历所有接口拼接命令并一次性下发：

class NetworkDevice:
    """网络设备类，保存设备登录信息及关联的接口"""
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.interfaces = []

    def add_interface(self, interface):
        """将接口加入本设备，并建立双向关联"""
        ???  # 把 interface 的 device 属性指向自己（self）
        ???  # 把 interface 追加到 self.interfaces 列表

    def apply(self):
        """将所有关联接口的配置一次性下发到设备"""
        if not self.interfaces:
            print(f"[*] {self.ip} 没有待下发的接口配置")
            return

        cmds = ['config ter']
        for iface in self.interfaces:
            ???  # 追加: interface {接口名}
            ???  # 追加: ip address {IP} {掩码}
            ???  # 如果有 description，追加: description {描述}
            ???  # 根据 status 追加 'no shutdown' 或 'shutdown'
        cmds.append('end')

        iface_names = ', '.join(iface.name for iface in self.interfaces)
        print(f"[*] 正在 {self.ip} 上批量应用接口配置: {iface_names}")
        qytang_multicmd(self.ip, self.username, self.password, cmds, verbose=False)
        print(f"[*] {self.ip} 所有接口配置应用完成！")

    def __str__(self):
        """打印设备信息及下属接口列表"""
        lines = [
            f"设备 IP      : {self.ip}",
            f"用户名       : {self.username}",
            "接口列表     :",
        ]
        if not self.interfaces:
            lines.append("  （无）")
        else:
            for iface in self.interfaces:
                status_str = 'no shutdown' if iface.status else 'shutdown'
                lines.append(f"  - {iface.name}: {iface.ip_address} {iface.mask}, {status_str}")
        return '\n'.join(lines)

任务三：测试代码

使用自己的思科路由器设备，创建设备对象，添加多个接口，打印设备信息后批量下发配置：

if __name__ == '__main__':
    # 1. 实例化设备对象（填入自己的设备 IP、用户名、密码）
    r1 = NetworkDevice('设备IP', '用户名', '密码')

    # 2. 创建第一个接口并设置参数
    loop13 = Interface('Loopback13')
    loop13.ip_address = '13.13.13.13'
    loop13.mask = '255.255.255.255'
    loop13.description = 'Created_by_Python'
    loop13.status = True
    r1.add_interface(loop13)

    # 3. 创建第二个接口并设置参数
    gi2 = Interface('GigabitEthernet2')
    gi2.ip_address = '172.16.1.12'
    gi2.mask = '255.255.255.0'
    gi2.description = 'Created_by_Python'
    gi2.status = True
    r1.add_interface(gi2)

    # 4. 打印设备及下属所有接口
    print(r1)

    # 5. 一次 SSH 连接，批量下发所有接口配置
    r1.apply()
期望输出（IP 根据自己的设备而不同）：
设备 IP      : 你的设备IP
用户名       : admin
接口列表     :
  - Loopback13: 13.13.13.13 255.255.255.255, no shutdown
  - GigabitEthernet2: 172.16.1.12 255.255.255.0, no shutdown

[*] 正在 你的设备IP 上批量应用接口配置: Loopback13, GigabitEthernet2
[*] 你的设备IP 所有接口配置应用完成！
验证：在路由器上执行 show run interface Loopback13 和 show run interface GigabitEthernet2，确认接口已创建且 IP、描述配置正确。
'''
# ======================== 前置导入（必须保留） ========================
import sys
import os
# 将上级目录加入Python路径，导入第十二天的多命令执行函数
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from homework.DAY12.question_1 import qytang_multicmd

# ======================== 任务一：完成 Interface 接口类 ========================
class Interface:
    """接口配置类，只保存接口数据（属性：名称、IP、掩码、描述、状态）"""
    def __init__(self, name):
        self.name = name              # 接口名称（必传）
        self.device = None            # 所属设备，默认未绑定（None）
        self.ip_address = ""          # IP 地址，默认空字符串
        self.mask = ""                # 子网掩码，默认空字符串
        self.description = ""         # 接口描述，默认空字符串
        self.status = False           # True=开启, False=关闭，默认关闭

    def __str__(self):
        """格式化打印接口信息（补全条件判断）"""
        # 如果 status 为 True → no shutdown，否则 → shutdown
        status_str = "no shutdown" if self.status else "shutdown"
        # 如果 device 存在 → 取设备IP，否则 → 未绑定设备
        device_ip = self.device.ip if self.device else "未绑定设备"

        lines = [
            f"接口名称    : {self.name}",
            f"所属设备    : {device_ip}",
            f"IP 地址     : {self.ip_address} {self.mask}",
            f"描述        : {self.description}",
            f"状态        : {status_str}",
        ]
        return '\n'.join(lines)

# ======================== 任务二：完成 NetworkDevice 网络设备类 ========================
class NetworkDevice:
    """网络设备类，保存登录信息，管理多个接口，批量下发配置（组合模式）"""
    def __init__(self, ip, username, password):
        self.ip = ip                  # 设备管理IP
        self.username = username      # SSH登录用户名
        self.password = password      # SSH登录密码
        self.interfaces = []          # 接口列表，存储多个Interface对象

    def add_interface(self, interface):
        """将接口加入设备，并建立双向关联（组合核心）"""
        interface.device = self       # 把接口的device指向当前设备（双向绑定）
        self.interfaces.append(interface)  # 把接口加入设备的接口列表

    def apply(self):
        """将所有关联接口的配置一次性下发到设备"""
        if not self.interfaces:
            print(f"[*] {self.ip} 没有待下发的接口配置")
            return

        cmds = ['config ter']  # 进入全局配置模式
        for iface in self.interfaces:
            cmds.append(f"interface {iface.name}")                          # 进入接口
            cmds.append(f"ip address {iface.ip_address} {iface.mask}")      # 配置IP
            if iface.description:                                           # 如果有描述
                cmds.append(f"description {iface.description}")
            if iface.status:                                                # 如果状态为True
                cmds.append("no shutdown")
            else:
                cmds.append("shutdown")

        cmds.append('end')  # 退出配置模式

        iface_names = ', '.join(iface.name for iface in self.interfaces)
        print(f"[*] 正在 {self.ip} 上批量应用接口配置: {iface_names}")
        qytang_multicmd(self.ip, self.username, self.password, cmds, verbose=False)
        print(f"[*] {self.ip} 所有接口配置应用完成！")

    def __str__(self):
        """打印设备信息及下属接口列表"""
        lines = [
            f"设备 IP      : {self.ip}",
            f"用户名       : {self.username}",
            "接口列表     :",
        ]
        if not self.interfaces:
            lines.append("  （无）")
        else:
            for iface in self.interfaces:
                status_str = 'no shutdown' if iface.status else 'shutdown'
                lines.append(f"  - {iface.name}: {iface.ip_address} {iface.mask}, {status_str}")
        return '\n'.join(lines)

# ======================== 任务三：测试代码 ========================
if __name__ == '__main__':
    # 1. 实例化设备对象（请改为你的设备信息）
    r1 = NetworkDevice('10.10.1.200', 'admin', 'Cisc0123')

    # 2. 创建第一个接口并设置参数
    loop13 = Interface('Loopback13')
    loop13.ip_address = '13.13.13.13'
    loop13.mask = '255.255.255.255'
    loop13.description = 'Created_by_Python'
    loop13.status = True
    r1.add_interface(loop13)

    # 3. 创建第二个接口并设置参数
    gi2 = Interface('GigabitEthernet2')
    gi2.ip_address = '172.16.1.12'
    gi2.mask = '255.255.255.0'
    gi2.description = 'Created_by_Python'
    gi2.status = True
    r1.add_interface(gi2)

    # 4. 打印设备及下属所有接口
    print(r1)

    # 5. 一次 SSH 连接，批量下发所有接口配置
    r1.apply()
