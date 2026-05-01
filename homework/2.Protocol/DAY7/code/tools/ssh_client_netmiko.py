#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from netmiko import ConnectHandler


def netmiko_config_cred(ip, username, password, cmds_list, verbose=False):
    """
    使用 Netmiko 通过 SSH 连接到设备并推送配置命令。

    :param ip: 设备 IP 地址
    :param username: SSH 用户名
    :param password: SSH 密码
    :param cmds_list: 配置命令列表（字符串列表）
    :param verbose: 是否打印详细输出
    :return: 配置命令的输出结果（字符串）
    """
    device = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password,
    }

    try:
        with ConnectHandler(**device) as conn:
            # 进入配置模式并发送配置命令集
            output = conn.send_config_set(cmds_list)
            if verbose:
                print(output)
            return output
    except Exception as e:
        print(f"连接设备 {ip} 时发生错误: {e}")
        return str(e)
