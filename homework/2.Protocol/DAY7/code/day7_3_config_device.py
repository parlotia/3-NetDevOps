#!/usr/bin/env python3
# -*- coding=utf-8 -*-

# ORM
from sqlalchemy.orm import sessionmaker
from day7_1_create_db import Router, engine

# 导入Netmiko代码
from tools.ssh_client_netmiko import netmiko_config_cred

# 协程相关
import asyncio
import os
import threading

import pprint

# 导入jinja2模块, 并设置模板目录
from jinja2 import Template
tem_path = './templates/'

# jinja2读取Cisco接口配置模板
with open(tem_path + 'cisco_ios_interface.template', encoding='utf-8') as f:
    interface_config_template = Template(f.read())

# jinja2读取Cisco OSPF配置模板
with open(tem_path + 'cisco_ios_ospf.template', encoding='utf-8') as f:
    ospf_config_template = Template(f.read())

# 协程任务循环
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# 定义netmiko的协程函数
async def async_netmiko(task_id, ip, username, password, cmds_list):
    """在线程池中异步执行 Netmiko 配置推送，并打印任务开始/结束状态。"""
    print(f'ID: {task_id} Started')
    print(os.getpid(), threading.current_thread().ident)
    result = await loop.run_in_executor(None, netmiko_config_cred, ip, username, password, cmds_list)
    print(f'ID: {task_id} Stopped')
    return result

# 连接数据库的会话
Session = sessionmaker(bind=engine)
session = Session()


# 循环任务计数号
task_no = 1

# 协程的任务清单
tasks = []

# 查询所有路由器
all_routers = session.query(Router).all()


for router in all_routers:
    # 每一个路由器最终配置命令的列表
    router_final_config_list = []

    # 提取路由器IP
    router_ip = router.ip
    # 提取路由器登录用户名
    login_username = router.username
    # 提取路由器登录密码
    login_password = router.password
    # 接口配置列表
    interface_config_list = []
    # 找到这个路由器的每一个接口
    for interface in router.interface:
        # 提取接口名字
        interface_name = interface.interface_name
        # 提取接口IP
        interface_ip = interface.ip
        # 提取接口掩码
        interface_mask = interface.mask
        # 把每一个接口配置的字典, 放入列表"interface_config_list"
        interface_config_list.append({"interface_name": interface_name,
                                      "interface_ip": interface_ip,
                                      "interface_mask": interface_mask
                                      })
    # 路由器接口配置模板内容如下:
    # {% for i in interface_list %}
    #     interface {{ i.interface_name }}
    #           ip address {{ i.interface_ip }} {{ i.interface_mask }}
    #           no shutdown
    # {% endfor %}
    pprint.pprint(interface_config_list)
    # 期望输出:
    # [{'interface_ip': '10.1.1.1',
    #   'interface_mask': '255.255.255.0',
    #   'interface_name': 'GigabitEthernet1'},
    #  {'interface_ip': '1.1.1.1',
    #   'interface_mask': '255.255.255.255',
    #   'interface_name': 'Loopback0'}]
    # 替换接口配置模板产生配置(多行字符串)
    interface_config_result = interface_config_template.render(interface_list=interface_config_list)
    # 把多行字符串, 通过".split('\n')"切分为一行一行的命令, 放入最终配置命令列表"router_final_config_list"
    router_final_config_list.extend(interface_config_result.split('\n'))

    # 提取路由器OSPF进程的数据库条目
    router_ospf_process = router.ospf_process
    # 提取OSPF进程ID
    router_ospf_process_id = router_ospf_process.processid
    # 提取路由器router_id
    router_id = router_ospf_process.routerid

    # 产生OSPF配置的字典, 先写入OSPF进程ID和router_id
    ospf_dict = {"ospf_process_id": router_ospf_process_id,
                 "router_id": router_id}

    # OSPF网络配置列表
    ospf_network_list = []

    # 提取OSPF进程下的每一个Area
    for area in router_ospf_process.area:
        # 提取OSPF的区域ID
        ospf_area_id = area.area_id
        # 找到此OSPF区域下的每一个需要被宣告的网络
        for ospf_network in area.ospf_network:
            # 提取OSPF网络
            ospf_network_net = ospf_network.network
            # 提取OSPF反掩码
            ospf_network_wildmask = ospf_network.wildmask
            # 把区域ID, OSPF网络, OSPF反掩码放入OSPF网络配置列表"ospf_network_list"
            ospf_network_list.append({"area": ospf_area_id,
                                      "network": ospf_network_net,
                                      "wildmask": ospf_network_wildmask
                                      })
    # 把网络配置写入OSPF配置的字典"ospf_dic"
    ospf_dict["ospf_network_list"] = ospf_network_list

    # 路由器OSPF配置模板内容如下:
    # router ospf {{ ospf_process_id }}
    #     router-id {{ router_id }}
    #     {% for n in ospf_network_list %}
    #       network {{ n.network }} {{ n.wildmask }} area {{ n.area }}
    #     {% endfor %}
    pprint.pprint(ospf_dict)
    # 期望输出:
    # {'ospf_network_list': [{'area': 0,
    #                         'network': '10.1.1.0',
    #                         'wildmask': '0.0.0.255'},
    #                        {'area': 0,
    #                         'network': '2.2.2.2',
    #                         'wildmask': '0.0.0.0'}],
    #  'ospf_process_id': 1,
    #  'router_id': '2.2.2.2'}
    # 替换OSPF配置模板产生配置(多行字符串)
    ospf_config_result = ospf_config_template.render(**ospf_dict)
    # 把多行字符串, 通过".split('\n')"切分为一行一行的命令, 放入最终配置命令列表"router_final_config_list"
    router_final_config_list.extend(ospf_config_result.split('\n'))

    # 不使用协程, 可以使用下面的代码
    # netmiko_config_cred(router_ip, login_username, login_password, router_final_config_list, verbose=True)

    # 产生协程任务
    task = loop.create_task(async_netmiko(task_no, router_ip, login_username, login_password, router_final_config_list))
    # 把产生的协程任务放入任务列表
    tasks.append(task)
    # 任务号加1
    task_no += 1

# 执行协程任务列表
loop.run_until_complete(asyncio.wait(tasks))
