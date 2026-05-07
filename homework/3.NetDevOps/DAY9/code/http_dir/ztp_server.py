#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZTP Server - Configuration Generator
服务端配置生成模块

职责：根据设备类型、接口列表和序列号，从 YAML 数据 + Jinja2 模板生成完整配置列表。
配置分为两层：
  1. 设备类型通用配置（C8000V.template + C8000V.yaml）
  2. 设备特殊配置（<SN>.yaml + interface/ospf.template）

注意：子命令（如 ip address、no shutdown）前的缩进空格必须保留，
      否则 cli.configurep() 无法识别配置层级。
"""

import os
from jinja2 import Template
import yaml

# 当前文件所在目录，用于拼接相对路径
current_dir = os.path.dirname(os.path.realpath(__file__))

# 设备特殊配置：数据文件目录和模板目录
device_config_data_dir = '{}{}specific_device_config{}device_config_data{}'.format(current_dir, os.sep, os.sep, os.sep)
device_config_template_dir = '{}{}specific_device_config{}device_config_template_dir{}'.format(current_dir, os.sep, os.sep, os.sep)

# 设备类型通用配置：数据文件目录和模板目录
device_type_data_dir = '{}{}device_type_config{}device_type_data{}'.format(current_dir, os.sep, os.sep, os.sep)
device_type_template_dir = '{}{}device_type_config{}device_type_template_dir{}'.format(current_dir, os.sep, os.sep, os.sep)


def get_device_config_list(device_type, device_if_list, device_sn):
    """
    生成设备完整配置列表

    :param device_type: 设备类型，如 'C8000V'，对应 device_type_config 下的文件名
    :param device_if_list: 设备接口列表，如 ['GigabitEthernet1', ...]
    :param device_sn: 设备序列号，如 '94CSC2OWS8U'，对应 specific_device_config 下的 <SN>.yaml
    :return: list，每条元素为一个 CLI 配置命令字符串（保留缩进）
    """
    device_config_list = []

    # ========== 第一层：设备类型通用配置 ==========
    # 加载设备类型 YAML 数据（账号、DNS、NTP、Telemetry 等）
    device_type_data_yaml = '{}{}.yaml'.format(device_type_data_dir, device_type)
    if os.path.exists(device_type_data_yaml):
        with open(device_type_data_yaml) as f:
            device_type_data = yaml.load(f, Loader=yaml.FullLoader)

        # 加载设备类型 Jinja2 模板
        device_type_template_file = '{}{}.template'.format(device_type_template_dir, device_type)
        if os.path.exists(device_type_template_file):
            with open(device_type_template_file) as f:
                device_type_template = Template(f.read())

            # 为每个接口生成 Telemetry gRPC 订阅 ID（从 grpc_start_id 开始递增）
            grpc_start_id = device_type_data.get('grpc_start_id', 668)
            grpc_if_list = []
            for idx, if_name in enumerate(device_if_list):
                grpc_if_list.append({
                    'id': grpc_start_id + idx,
                    'name': if_name
                })

            # 渲染通用配置模板
            device_type_rendered = device_type_template.render(
                username=device_type_data.get('username'),
                password=device_type_data.get('password'),
                search_dns=device_type_data.get('search_dns'),
                dns_server=device_type_data.get('dns_server'),
                ntp_server=device_type_data.get('ntp_server'),
                grpc_server=device_type_data.get('grpc_server'),
                grpc_port=device_type_data.get('grpc_port'),
                grpc_list=device_type_data.get('grpc_list', []),
                grpc_if_list=grpc_if_list
            )
            # 按行分割，过滤空行，保留原始缩进（不能用 .strip()）
            for line in device_type_rendered.split('\n'):
                if line.strip():
                    device_config_list.append(line)

    # ========== 第二层：设备特殊配置 ==========
    # 根据序列号查找设备专属 YAML 数据文件
    device_config_data_yaml = '{}{}.yaml'.format(device_config_data_dir, device_sn)
    if os.path.exists(device_config_data_yaml):
        with open(device_config_data_yaml) as f:
            device_config_data = yaml.load(f, Loader=yaml.FullLoader)

        # hostname
        if 'hostname' in device_config_data:
            device_config_list.append('hostname {}'.format(device_config_data['hostname']))

        # 接口配置（ip address、no shutdown 等）
        interface_template_file = '{}cisco_ios_interface.template'.format(device_config_template_dir)
        if os.path.exists(interface_template_file):
            with open(interface_template_file) as f:
                interface_template = Template(f.read())
            interface_config = interface_template.render(interface_list=device_config_data['interface_list'])
            # 保留缩进：子命令前有空格，不能用 .strip()
            for line in interface_config.split('\n'):
                if line.strip():
                    device_config_list.append(line)

        # OSPF 配置
        if 'ospf_process_id' in device_config_data:
            ospf_template_file = '{}cisco_ios_ospf.template'.format(device_config_template_dir)
            if os.path.exists(ospf_template_file):
                with open(ospf_template_file) as f:
                    ospf_template = Template(f.read())
                ospf_config = ospf_template.render(
                    ospf_network_list=device_config_data['ospf_network_list'],
                    ospf_process_id=device_config_data['ospf_process_id'],
                    router_id=device_config_data['router_id']
                )
                # 保留缩进：router-id、network 等是 router ospf 的子命令
                for line in ospf_config.split('\n'):
                    if line.strip():
                        device_config_list.append(line)

    return device_config_list
