'''
While 循环：监控 TCP/80 HTTP 服务是否开放
先在 Linux 上启动一个简单的 HTTP 服务（端口 80）：

from http.server import HTTPServer, CGIHTTPRequestHandler
port = 80
httpd = HTTPServer(('', port), CGIHTTPRequestHandler)
print('Starting simple httpd on port: ' + str(httpd.server_port))
httpd.serve_forever()
使用 ss -tulnp 确认端口已监听：

[root@AIOps ~]# ss -tulnp | grep :80
tcp   LISTEN 0      5            0.0.0.0:80        0.0.0.0:*    users:(("python3",pid=12345,fd=3))
编写 Python 脚本，使用 While 循环每隔 1 秒检测一次 TCP/80 是否处于监听状态（必须区分 TCP/UDP 和端口号），检测到后退出循环并打印告警:
[*] 检测中... TCP/80 未监听
[*] 检测中... TCP/80 未监听
[*] 检测中... TCP/80 未监听
[!] 告警: TCP/80 已开放！请检查是否为授权服务。
代码提示: 使用 os.popen('ss -tulnp').read() 获取端口信息，逐行判断是否同时包含 tcp 和 :80 （注意 避免误匹配 :8080 或 :8000），使用 import time; time.sleep(1) 控制间隔。


'''


# 导入系统命令模块
import os
# 导入时间模块，控制检测间隔
import time

# 无限循环，持续监控
while True:
    # 严格按照提示：执行ss命令，读取所有端口信息
    port_info = os.popen('ss -tulnp').read()
    
    # 初始化标记：默认未检测到80端口
    is_listen = False

    # 严格按照提示：逐行遍历端口信息
    for line in port_info.splitlines():
        # 核心判断：
        # 1. 包含 tcp（区分协议）
        # 2. 包含 :80（精准匹配，加空格防止匹配8080/8000）
        if "tcp" in line and ":80 " in line:
            is_listen = True
            # 找到后直接退出循环
            break

    # 根据检测结果输出
    if is_listen:
        # 端口开放，打印告警并退出监控
        print("[!] 告警: TCP/80 已开放！请检查是否为授权服务。")
        break
    else:
        # 端口未开放，打印提示
        print("[*] 检测中... TCP/80 未监听")
        # 严格按照提示：等待1秒
        time.sleep(1)