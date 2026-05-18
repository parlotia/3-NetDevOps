'''
f-string：打印一条Syslog告警
定义以下变量，使用 f-string 打印一条网络设备的Syslog告警信息:

date = "2026-03-03"
hostname = "SW-Core-01"
level = "CRITICAL"
message = "%LINK-3-UPDOWN: Interface GigabitEthernet0/1, changed state to down"
打印效果如下:

2026-03-03 SW-Core-01 CRITICAL %LINK-3-UPDOWN: Interface GigabitEthernet0/1, changed state to down
'''

date = "2026-03-03"
hostname = "SW-Core-01"
level = "CRITICAL"
message = "%LINK-3-UPDOWN: Interface GigabitEthernet0/1, changed state to down"


print(f"{date} {hostname} {level} {message}")