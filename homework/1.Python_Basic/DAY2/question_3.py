'''
从设备采集回来的版本信息字符串经常有多余的空格，需要处理后再使用:

version_raw = "  Cisco IOS XE Software, Version 17.03.04  "
完成以下3步并分别打印结果:

去掉首尾空格（strip）
把字符串转成全大写（upper）
把 "17.03.04" 替换成 "17.06.01"（replace）
打印效果如下:

去掉空格: Cisco IOS XE Software, Version 17.03.04
转大写:   CISCO IOS XE SOFTWARE, VERSION 17.03.04
替换版本: Cisco IOS XE Software, Version 17.06.01
'''

version_raw = "  Cisco IOS XE Software, Version 17.03.04  "

# 1. 去掉首尾空格
version_stripped = version_raw.strip()
# 2. 转全大写（基于去空格后的结果）
version_upper = version_stripped.upper()
# 3. 替换版本号（基于去空格后的结果）
version_replaced = version_stripped.replace("17.03.04", "17.06.01")

print(f"去掉空格: {version_stripped}")
print(f"转大写:   {version_upper}")
print(f"替换版本: {version_replaced}")