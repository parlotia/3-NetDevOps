'''
创建一个Python脚本，打印一台网络设备的基本信息
定义以下变量，并使用print打印出设备信息卡片:

hostname = "C8Kv1"
ip = "192.168.1.1"
vendor = "Cisco"
model = "C8000v"
os_version = "IOS-XE 17.3.4"
打印效果如下:

========== 设备信息 ==========
设备名称: C8Kv1
管理地址: 192.168.1.1
厂商:     Cisco
型号:     C8000v
系统版本: IOS-XE 17.3.4
==============================
'''


hostname = "C8Kv1"
ip = "192.168.1.1"
vendor = "Cisco"
model = "C8000v"
os_version = "IOS-XE 17.3.4"


print("=" * 10 + " 设备信息 " + "=" * 10)
print("设备名称: " + hostname)
print("管理地址: " + ip)
print("厂商:     " + vendor)
print("型号:     " + model)
print("系统版本: " + os_version)
print("=" * 30)