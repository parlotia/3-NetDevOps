'''
监控设备配置改变
如何计算字符串的 MD5 值：

>>> import hashlib
>>> m = hashlib.md5()
>>> m.update('test'.encode())
>>> print(m.hexdigest())
098f6bcd4621d373cade4e832627b4f6
>>> m.update('test1'.encode())
>>> print(m.hexdigest())
c23b2ed66eedb321c5bcfb5e3724b978
一共要制作两个函数：

函数一：获取设备配置

复用第九天的 ssh_run 函数，SSH 登录思科路由器执行 show running-config，只截取 hostname 到 end 之间的有效配置部分，返回配置字符串。

使用自己的思科路由器设备进行测试，填入对应的 IP、用户名和密码。

函数二：每 5 秒监控一次配置变化

每 5 秒调用函数一获取配置，计算 MD5 值；如果和上一次相同则打印当前 MD5，如果不同则打印告警并退出程序。

预期输出：
正常运行时（配置未改变）：

[*] 当前配置 MD5: 90aa7a934c03bd959bcd5e29cb82e5d0
[*] 当前配置 MD5: 90aa7a934c03bd959bcd5e29cb82e5d0
[*] 当前配置 MD5: 90aa7a934c03bd959bcd5e29cb82e5d0
在路由器上修改配置（例如修改 hostname）：

Router(config)#hostname C8Kv1
C8Kv1(config)#
脚本检测到变化后打印告警并退出：

[*] 当前配置 MD5: 90aa7a934c03bd959bcd5e29cb82e5d0
[*] 当前配置 MD5: 90aa7a934c03bd959bcd5e29cb82e5d0
[!] 告警: 配置已改变！新 MD5: 40f13d7459ff338c7dbc56f2e12ff96f
#代码提示: 使用 import hashlib 计算 MD5，import time; time.sleep(5) 控制轮询间隔；截取配置使用正则 re.search(r'(hostname[\s\S]+end)', output) 一次性提取 hostname 到 end 之间的全部内容。
'''

# ==================== 导入库及功能说明 ====================
import sys      # 【系统交互库】和Python解释器打交道，这里用来修改"模块搜索路径"，让Python能找到DAY9的脚本
import os       # 【操作系统库】和文件/文件夹路径打交道，这里用来获取当前脚本的绝对路径、找上级目录
import hashlib  # 【哈希算法库】提供MD5/SHA等加密算法，这里用来计算配置字符串的MD5值，对比配置是否变化
import time     # 【时间库】处理时间相关操作，这里用来实现"每5秒监控一次"的轮询间隔
import re       # 【正则表达式库】用来做字符串的复杂匹配/提取，这里用来截取配置中"hostname到end"的有效部分

# 添加上级目录到搜索路径，导入第九天的SSH函数
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DAY9.question_1 import ssh_exec_cmd

# ==================== 函数一：获取设备配置（截取 hostname 到 end） ====================
def get_device_config(host, username, password):
    # 1. SSH 登录执行 show running-config
    full_output = ssh_exec_cmd(host, username, password, 'show running-config')
    
    # 2. 代码提示要求：用正则截取 hostname 到 end 之间的有效配置
    # [\s\S]+ 表示匹配所有字符（包括换行），一次性提取多行
    match = re.search(r'(hostname[\s\S]+end)', full_output)
    if match:
        # 返回截取到的配置字符串
        return match.group(1)
    else:
        return ""

# ==================== 函数二：计算字符串的 MD5 值 ====================
def calculate_md5(content):
    m = hashlib.md5()
    # 必须 encode() 转成二进制才能计算
    m.update(content.encode())
    # 返回十六进制格式的 MD5
    return m.hexdigest()

# ==================== 函数三：每 5 秒监控配置变化 ====================
def monitor_config_change(host, username, password):
    # 初始化：先获取一次配置和 MD5
    last_config = get_device_config(host, username, password)
    last_md5 = calculate_md5(last_config)
    
    # 无限循环监控
    while True:
        # 1. 等待 5 秒
        time.sleep(5)
        
        # 2. 再次获取配置和 MD5
        current_config = get_device_config(host, username, password)
        current_md5 = calculate_md5(current_config)
        
        # 3. 对比 MD5
        if current_md5 == last_md5:
            # 相同：打印当前 MD5
            print(f"[*] 当前配置 MD5: {current_md5}")
        else:
            # 不同：打印告警并退出
            print(f"[!] 告警: 配置已改变！新 MD5: {current_md5}")
            break
        
        # 4. 更新"上一次 MD5"为当前值，准备下一轮对比
        last_md5 = current_md5

# ==================== 程序入口 ====================
if __name__ == '__main__':
    # 填入你的思科设备信息
    device_ip = '10.10.1.200'
    user = 'admin'
    pwd = 'Cisc0123'
    
    # 启动监控
    monitor_config_change(device_ip, user, pwd)