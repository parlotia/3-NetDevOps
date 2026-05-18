'''
打印一张简单的IP地址规划表
假设你负责一个小型网络，有3台设备，请定义变量并打印如下格式的IP规划表:

========== IP地址规划表 ==========
设备名称          管理地址          角色
-----------------------------------------
CoreSwitch        10.1.1.1          核心交换机
Firewall          10.1.1.2          防火墙
WLC               10.1.1.3          无线控制器
=========================================
提示: 可以直接用多个print语句，也可以尝试用 \t (Tab) 来对齐。
'''


#交换机变量
core_name = "CoreSwitch"
core_ip = "10.1.1.1"     
core_role = "核心交换机"

# 防火墙变量
firewall_name = "Firewall"
firewall_ip = "10.1.1.2"
firewall_role = "防火墙"

# WLC变量
wlc_name = "WLC"
wlc_ip = "10.1.1.3"
wlc_role = "无线控制器"

print("=" * 22  +  "IP地址规划表" + "=" *25)
print("设备名称\t\t管理地址\t\t角色")
print("-" * 59)
print(core_name + "\t\t" + core_ip + "\t\t" + core_role)
print(firewall_name + "\t\t" + firewall_ip + "\t\t" + firewall_role)
print(wlc_name + "\t\t\t" + wlc_ip + "\t\t" + wlc_role)
print("=" * 59)