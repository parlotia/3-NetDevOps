#!/usr/bin/env python3
"""
DAY11 - 使用 pynetbox 读取 NetBox 数据，并使用 netmiko 配置设备

设计目标：
1. 从 NetBox 中读取设备、主管理 IP、接口地址、OSPF 配置上下文
2. 生成 Cisco IOS XE 配置命令
3. 通过 Netmiko 下发到真实设备

说明：
- 参考老师的思路：pynetbox 读取数据，netmiko 推送配置
- 适配当前 NetBox 4.6.0 + pynetbox 环境
"""

import asyncio
import ipaddress
import os
import threading
from typing import Dict, List, Optional

import pynetbox
from netmiko import ConnectHandler

NETBOX_URL = "http://localhost:8080"
NETBOX_TOKEN = "nbt_PuB77ohtZgkG.PBhDlGE1EDDlGnHYn37EOzUXwd9TQec8VDHGkllK"
DEVICE_USERNAME = "admin"
DEVICE_PASSWORD = "Cisc0123"

nb = pynetbox.api(url=NETBOX_URL, token=NETBOX_TOKEN)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


def cidr_to_ip_mask(cidr: str) -> Dict[str, str]:
    """把 CIDR 地址转换为 IP + 子网掩码"""
    interface = ipaddress.ip_interface(cidr)
    return {
        "ip": str(interface.ip),
        "mask": str(interface.network.netmask),
        "prefixlen": str(interface.network.prefixlen),
    }


def get_device_objects() -> List:
    """读取 DAY11 相关设备对象"""
    devices = []
    for device_name in ["C8Kv1", "C8Kv2"]:
        device = nb.dcim.devices.get(name=device_name)
        if device:
            devices.append(device)
    return devices


def get_interface_ip(interface_id: int) -> Optional[str]:
    """根据接口 ID 获取接口 IP 地址（CIDR）"""
    ip_obj = nb.ipam.ip_addresses.get(interface_id=interface_id)
    if ip_obj:
        return str(ip_obj.address)
    return None


def get_device_info(device) -> Dict:
    """获取单台设备完整信息"""
    device_info = {
        "name": device.name,
        "platform": str(device.platform) if device.platform else "Cisco IOS",
        "primary_ip": None,
        "interfaces": [],
        "config_context": device.config_context or {},
    }

    if device.primary_ip4:
        device_info["primary_ip"] = cidr_to_ip_mask(str(device.primary_ip4)).get("ip")

    interfaces = nb.dcim.interfaces.filter(device_id=device.id)
    for interface in interfaces:
        interface_ip = get_interface_ip(interface.id)
        device_info["interfaces"].append(
            {
                "name": interface.name,
                "mgmt_only": interface.mgmt_only,
                "enabled": interface.enabled,
                "ip_cidr": interface_ip,
            }
        )

    return device_info


def build_interface_config(device_info: Dict) -> List[str]:
    """根据 NetBox 接口/IP 数据生成接口配置"""
    commands = []

    for interface in sorted(device_info["interfaces"], key=lambda x: x["name"]):
        if not interface["ip_cidr"]:
            continue

        ip_mask = cidr_to_ip_mask(interface["ip_cidr"])
        commands.append(f"interface {interface['name']}")
        commands.append(f" ip address {ip_mask['ip']} {ip_mask['mask']}")

        if interface["enabled"]:
            commands.append(" no shutdown")
        else:
            commands.append(" shutdown")

        commands.append(" exit")

    return commands


def build_ospf_config(device_info: Dict) -> List[str]:
    """根据 Config Context 生成 OSPF 配置"""
    commands = []
    ospf_data = device_info.get("config_context", {}).get("router", {}).get("ospf", {})
    if not ospf_data:
        return commands

    process_id = ospf_data.get("process_id", 1)
    router_id = ospf_data.get("router_id")
    network_list = ospf_data.get("network_list", [])

    commands.append(f"router ospf {process_id}")
    if router_id:
        commands.append(f" router-id {router_id}")

    for network in network_list:
        network_ip = network.get("network")
        wildmask = network.get("wildmask")
        area = network.get("area", 0)
        if network_ip and wildmask is not None:
            commands.append(f" network {network_ip} {wildmask} area {area}")

    commands.append(" exit")
    return commands


def build_final_config(device_info: Dict) -> List[str]:
    """组合最终配置命令"""
    commands = ["hostname {}".format(device_info["name"])]
    commands.extend(build_interface_config(device_info))
    commands.extend(build_ospf_config(device_info))
    return commands


def netmiko_config_cred(ip: str, username: str, password: str, cmds_list: List[str]) -> str:
    """使用 Netmiko 推送配置"""
    device = {
        "device_type": "cisco_ios",
        "ip": ip,
        "username": username,
        "password": password,
    }

    with ConnectHandler(**device) as conn:
        output = conn.send_config_set(cmds_list)
        return output


async def async_netmiko(task_id: int, ip: str, username: str, password: str, cmds_list: List[str]):
    """并发执行 Netmiko 配置任务"""
    print(f"[TASK-{task_id}] Started")
    print(f"PID={os.getpid()} THREAD={threading.current_thread().ident}")
    result = await loop.run_in_executor(None, netmiko_config_cred, ip, username, password, cmds_list)
    print(f"[TASK-{task_id}] Stopped")
    return result


def preview_configs() -> List[Dict]:
    """预览将要下发的配置"""
    result = []
    for device in get_device_objects():
        info = get_device_info(device)
        result.append(
            {
                "device_name": info["name"],
                "mgmt_ip": info["primary_ip"],
                "commands": build_final_config(info),
            }
        )
    return result


def deploy_all_devices() -> None:
    """从 NetBox 读取数据并下发配置到所有设备"""
    tasks = []
    task_no = 1

    for device in get_device_objects():
        info = get_device_info(device)
        if not info["primary_ip"]:
            print(f"[SKIP] {info['name']} 未配置主管理 IP")
            continue

        final_config = build_final_config(info)
        print(f"\n=== {info['name']} 配置预览 ===")
        for cmd in final_config:
            print(cmd)

        task = loop.create_task(
            async_netmiko(
                task_no,
                info["primary_ip"],
                DEVICE_USERNAME,
                DEVICE_PASSWORD,
                final_config,
            )
        )
        tasks.append(task)
        task_no += 1

    if tasks:
        results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        print("\n=== 配置下发结果 ===")
        for idx, result in enumerate(results, start=1):
            print(f"--- TASK {idx} ---")
            print(result)
    else:
        print("没有可下发的设备任务")


if __name__ == "__main__":
    deploy_all_devices()
