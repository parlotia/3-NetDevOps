#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from sqlalchemy.orm import sessionmaker
from day7_1_create_db import Router, Interface, OSPFProcess, Area, OSPFNetwork, engine

Session = sessionmaker(bind=engine)
session = Session()


# 设备接口信息
c8kv1_ifs = [{'ifname': "GigabitEthernet1", 'ip': "10.10.1.200", 'mask': "255.255.255.0"},
             {'ifname': "Loopback0", 'ip': "1.1.1.1", 'mask': "255.255.255.255"}]

c8kv2_ifs = [{'ifname': "GigabitEthernet1", 'ip': "10.10.1.201", 'mask': "255.255.255.0"},
             {'ifname': "Loopback0", 'ip': "2.2.2.2", 'mask': "255.255.255.255"}]

# 设备OSPF信息
c8kv1_ospf = {"process_id": 1,
              "router_id": "1.1.1.1",
              "areas": [{'area_id': 0, 'networks': [{'ip': "10.10.1.0", 'wildmask': "0.0.0.255"},
                                                    {'ip': "1.1.1.1", 'wildmask': "0.0.0.0"}]}]}

c8kv2_ospf = {"process_id": 1,
              "router_id": "2.2.2.2",
              "areas": [{'area_id': 0, 'networks': [{'ip': "10.10.1.0", 'wildmask': "0.0.0.255"},
                                                    {'ip': "2.2.2.2", 'wildmask': "0.0.0.0"}]}]}
username = 'admin'
password = 'Cisc0123'

# 汇总后数据
all_network_data = [{'ip': "10.10.1.200",
                     'router_name': 'C8Kv1',
                     'username': username,
                     'password': password,
                     'interfaces': c8kv1_ifs,
                     'ospf': c8kv1_ospf},
                    {'ip': "10.10.1.201",
                     'router_name': 'C8Kv2',
                     'username': username,
                     'password': password,
                     'interfaces': c8kv2_ifs,
                     'ospf': c8kv2_ospf}]

# 把之前的内容删除
session.query(Router).delete()


for device in all_network_data:
    # 添加Router
    router_device = Router(router_name=device['router_name'],
                           username=device['username'],
                           password=device['password'],
                           ip=device['ip'])
    session.add(router_device)

    # 添加Interface
    for ifs in device['interfaces']:
        new_if = Interface(router=router_device, interface_name=ifs['ifname'], ip=ifs['ip'], mask=ifs['mask'])
        session.add(new_if)

    # 添加OSPFProcess
    router_device_process = OSPFProcess(router=router_device,
                                        processid=device["ospf"]["process_id"],
                                        routerid=device["ospf"]["router_id"])

    # 添加Area
    for device_area in device["ospf"]["areas"]:
        router_device_area = Area(ospf_process=router_device_process, area_id=device_area["area_id"])
        session.add(router_device_area)

        # 添加Area下的每一个OSPFNetwork
        for net in device_area["networks"]:
            new_net = OSPFNetwork(area=router_device_area, network=net['ip'], wildmask=net['wildmask'])
            session.add(new_net)

session.commit()
