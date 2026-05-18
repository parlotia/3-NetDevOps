#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""Day 9 - Netmiko 采集工具"""

from netmiko import Netmiko
from netmiko.exceptions import NetmikoAuthenticationException
from netmiko.exceptions import NetmikoTimeoutException


def netmiko_show_cred(host, username, password, cmd, enable='Cisc0123', ssh=True):
    """通过 Netmiko 连接设备并执行 show 命令。"""
    device_info = {
        'host': host,
        'username': username,
        'password': password,
        'device_type': 'cisco_ios' if ssh else 'cisco_ios_telnet',
        'secret': enable,
    }

    try:
        net_connect = Netmiko(**device_info)
        net_connect.enable()
        result = net_connect.send_command(cmd, read_timeout=120)
        net_connect.disconnect()
        return result, host
    except (NetmikoTimeoutException, NetmikoAuthenticationException, OSError) as error:
        print(f'[-] connection error ip: {host} error: {error}')
        return None


if __name__ == '__main__':
    print('请在 Day 9 主程序中调用 netmiko_show_cred()。')
