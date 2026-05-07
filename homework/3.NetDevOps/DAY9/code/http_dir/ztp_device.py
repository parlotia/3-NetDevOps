#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
ZTP Device-Side Script
设备端 ZTP 脚本

执行环境：Cisco IOS-XE day0 guestshell（通过 DHCP Option 67 bootfile 下载）
执行流程：
  1. 获取设备序列号（SN）和 IP 地址
  2. 临时设置 hostname 为 SN（便于识别）
  3. 通过 HTTP POST 将 SN/IP 提交到 ZTP 服务器 /device_config_json
  4. 解析返回的 JSON 配置列表
  5. 调用 cli.configurep() 批量应用配置

注意：
  - 此脚本在 guestshell 中运行，依赖 Cisco 专有 cli 模块
  - 所有 print 输出必须是 ASCII（guestshell 默认编码不支持中文）
  - curl 命令使用单引号包裹 JSON 数据，避免 shell 转义问题
"""

import cli
import json
import os

# ZTP 服务器 IP（DHCP 服务器地址）
ZTP_SERVER = "10.10.1.205"


# ========== 步骤 1：获取设备序列号 ==========
# cli.execute() 返回命令输出字符串（区别于 cli.executep() 只执行不返回）
version_result = cli.execute('show version')
version_list = version_result.split('\n')
device_sn = ""
for x in version_list:
    if "Processor board ID" in x:
        # 示例输出：Processor board ID 94CSC2OWS8U
        # split() 按空格分割，第 4 个元素（索引 3）即为 SN
        device_sn = x.split()[3]

# ========== 步骤 2：获取设备 DHCP IP ==========
device_ip = ""
if_result = cli.execute('show ip inter brie').split('\n')
for x in if_result:
    if 'DHCP' in x:
        # 示例输出：GigabitEthernet1  10.10.1.121  YES DHCP  up  up
        # split() 后第 2 个元素（索引 1）即为 IP
        device_ip = x.split()[1]

# ========== 步骤 3：临时设置 hostname ==========
cli.configurep(["hostname {}".format(device_sn)])

# ========== 步骤 4：向服务器请求完整配置 ==========
if device_sn:
    # 构造 JSON 请求体
    data = json.dumps({"device_sn": device_sn, "device_ip": device_ip})
    # 使用 curl POST 提交 SN，获取 JSON 格式配置列表
    cmd = 'curl -X POST -H "Content-Type: application/json" -d \'{}\' http://{}/device_config_json'.format(data, ZTP_SERVER)
    result = os.popen(cmd)
    response = result.read()
    try:
        config_list = json.loads(response).get('config')
        if config_list:
            # ========== 步骤 5：应用配置 ==========
            # cli.configurep() 接收配置命令列表，在配置模式下逐条执行
            # 列表中的缩进空格用于标识子命令层级（如 interface 下的 ip address）
            cli.configurep(config_list)
    except Exception as e:
        print("Config apply error: {}".format(e))

print("\n\n *** ZTP Day0 Python Script Execution Complete *** \n\n")
