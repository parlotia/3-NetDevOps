'''
正则表达式测试 1：解析MAC地址表
字符串为交换机MAC地址表内容:

mac_table = '166    54a2.74f7.0326    DYNAMIC     Gi1/0/11'
使用正则表达式匹配，提取出 VLAN、MAC地址、类型、接口，使用 format() 对齐后打印结果如下:

VLAN  : 166
MAC   : 54a2.74f7.0326
Type  : DYNAMIC
Port  : Gi1/0/11
'''

import re

mac_table = '166    54a2.74f7.0326    DYNAMIC     Gi1/0/11'
pattern = r'(\d+)\s+([0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})\s+([A-Z]+)\s+(\S+)'
vlan, mac, mac_type, port = re.match(pattern, mac_table).groups()

print("{:<10}: {}".format("VLAN", vlan))
print("{:<10}: {}".format("MAC", mac))
print("{:<10}: {}".format("Type", mac_type))
print("{:<10}: {}".format("Port", port))