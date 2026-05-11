#!/usr/bin/env python3
"""
Netbox DAY11 - 网络拓扑数据录入脚本
基于实际环境（C8Kv1/C8Kv2）录入网络拓扑到Netbox

实际环境信息：
- C8Kv1 (R1): 10.10.1.201 (管理IP)
  - GigabitEthernet1: 10.10.1.201/24 (管理)
  - GigabitEthernet2: 137.78.5.254/24
  - GigabitEthernet3: 61.128.1.254/24
  - Loopback0: 1.1.1.1/32
  - OSPF Router ID: 1.1.1.1

- C8Kv2 (R2): 10.10.1.202 (管理IP)
  - GigabitEthernet1: 10.10.1.202/24 (管理)
  - GigabitEthernet2: 137.78.5.253/24
  - GigabitEthernet3: 61.128.1.253/24
  - Loopback0: 2.2.2.2/32
  - OSPF Router ID: 2.2.2.2

OSPF邻居关系：
- 两台路由器通过GigabitEthernet2和GigabitEthernet3建立了FULL邻接关系
- Area 0 (BACKBONE)
"""

import pynetbox
import sys

# Netbox API 配置
NETBOX_URL = "http://localhost:8080"
NETBOX_TOKEN = "nbt_PuB77ohtZgkG.PBhDlGE1EDDlGnHYn37EOzUXwd9TQec8VDHGkllK"  # API Token v2 (nbt_<key>.<token>)

# 创建pynetbox API连接实例
nb = pynetbox.api(url=NETBOX_URL, token=NETBOX_TOKEN)


def check_netbox_connection():
    """检查Netbox连接状态"""
    try:
        status = nb.status()
        print(f"[OK] Netbox连接成功, 版本: {status.get('netbox-version', 'unknown')}")
        return True
    except Exception as e:
        print(f"[ERROR] 无法连接到Netbox: {e}")
        return False


def create_or_get(func, **kwargs):
    """创建或获取已存在的对象"""
    try:
        # 构建查询参数（只使用可过滤的字段）
        query_params = {}
        if 'name' in kwargs:
            query_params['name'] = kwargs['name']
        elif 'slug' in kwargs:
            query_params['slug'] = kwargs['slug']
        elif 'model' in kwargs:
            query_params['model'] = kwargs['model']
        
        # 先尝试查找是否已存在
        if query_params:
            results = list(func.filter(**query_params))
            if results:
                print(f"  [FOUND] {kwargs.get('name', kwargs.get('model', kwargs))} 已存在")
                return results[0]
        
        # 不存在则创建
        result = func.create(**kwargs)
        print(f"  [CREATED] {kwargs.get('name', kwargs.get('model', kwargs))} 创建成功")
        return result
    except Exception as e:
        print(f"  [ERROR] 创建/获取 {kwargs.get('name', kwargs.get('model', kwargs))} 失败: {e}")
        return None


def populate_organization():
    """录入组织数据（Region, Site）"""
    print("\n=== 录入组织数据 ===")
    
    # 创建Region
    region = create_or_get(nb.dcim.regions, name="QYT", slug="qyt")
    
    # 创建Site Group
    site_group = create_or_get(nb.dcim.site_groups, name="QYT_Group", slug="qyt_group")
    
    # 创建Site - 使用对象ID作为外键引用
    site_params = {"name": "QYT_Site", "slug": "qyt_site"}
    if region:
        site_params["region"] = region.id
    if site_group:
        site_params["group"] = site_group.id
    
    site = create_or_get(nb.dcim.sites, **site_params)
    
    return site


def populate_manufacturers_and_types():
    """录入设备制造商和类型"""
    print("\n=== 录入设备制造商和类型 ===")
    
    # 创建Manufacturer
    manufacturer = create_or_get(nb.dcim.manufacturers, name="Cisco", slug="cisco")
    
    # 创建Device Type - 使用对象ID作为外键引用
    device_type_params = {"model": "C8000V", "slug": "c8000v"}
    if manufacturer:
        device_type_params["manufacturer"] = manufacturer.id
    
    device_type = create_or_get(nb.dcim.device_types, **device_type_params)
    
    return device_type


def populate_roles_and_platforms():
    """录入设备角色和平台"""
    print("\n=== 录入设备角色和平台 ===")
    
    # 创建Device Role
    role = create_or_get(nb.dcim.device_roles, name="Router", slug="router", color="ff0000")
    
    # 创建Platform - 先获取manufacturer对象
    manufacturer = create_or_get(nb.dcim.manufacturers, name="Cisco", slug="cisco")
    platform_params = {"name": "Cisco IOS", "slug": "cisco_ios"}
    if manufacturer:
        platform_params["manufacturer"] = manufacturer.id
    
    platform = create_or_get(nb.dcim.platforms, **platform_params)
    
    return role, platform


def populate_devices(site, device_type, role, platform):
    """录入设备信息（C8Kv1, C8Kv2）- 不包含primary_ip4，稍后设置"""
    print("\n=== 录入设备信息 ===")
    
    devices = []
    
    # C8Kv1 - 使用对象ID作为外键引用，不设置primary_ip4（IP地址还未创建）
    c8kv1_params = {
        "name": "C8Kv1",
        "slug": "c8kv1",
    }
    if device_type:
        c8kv1_params["device_type"] = device_type.id
    if role:
        c8kv1_params["role"] = role.id
    if platform:
        c8kv1_params["platform"] = platform.id
    if site:
        c8kv1_params["site"] = site.id
    
    c8kv1 = create_or_get(nb.dcim.devices, **c8kv1_params)
    if c8kv1:
        devices.append(c8kv1)
    
    # C8Kv2
    c8kv2_params = {
        "name": "C8Kv2",
        "slug": "c8kv2",
    }
    if device_type:
        c8kv2_params["device_type"] = device_type.id
    if role:
        c8kv2_params["role"] = role.id
    if platform:
        c8kv2_params["platform"] = platform.id
    if site:
        c8kv2_params["site"] = site.id
    
    c8kv2 = create_or_get(nb.dcim.devices, **c8kv2_params)
    if c8kv2:
        devices.append(c8kv2)
    
    return devices


def populate_interfaces(devices):
    """录入接口信息"""
    print("\n=== 录入接口信息 ===")
    
    # 重新从NetBox读取设备对象，避免使用旧缓存对象导致外键序列化异常
    device_map = {}
    for device_name in ["C8Kv1", "C8Kv2"]:
        device_obj = nb.dcim.devices.get(name=device_name)
        if device_obj:
            device_map[device_name] = device_obj
    
    # C8Kv1接口
    c8kv1_interfaces = [
        {"name": "GigabitEthernet1", "type": "1000base-t", "mgmt_only": True},
        {"name": "GigabitEthernet2", "type": "1000base-t", "mgmt_only": False},
        {"name": "GigabitEthernet3", "type": "1000base-t", "mgmt_only": False},
        {"name": "Loopback0", "type": "virtual", "mgmt_only": False},
    ]
    
    # C8Kv2接口
    c8kv2_interfaces = [
        {"name": "GigabitEthernet1", "type": "1000base-t", "mgmt_only": True},
        {"name": "GigabitEthernet2", "type": "1000base-t", "mgmt_only": False},
        {"name": "GigabitEthernet3", "type": "1000base-t", "mgmt_only": False},
        {"name": "Loopback0", "type": "virtual", "mgmt_only": False},
    ]
    
    # 创建C8Kv1接口
    if "C8Kv1" in device_map:
        for iface_data in c8kv1_interfaces:
            try:
                # 先查找是否已存在
                existing = list(nb.dcim.interfaces.filter(device_id=device_map["C8Kv1"].id, name=iface_data["name"]))
                if existing:
                    print(f"  [FOUND] C8Kv1:{iface_data['name']} 已存在")
                    continue
                
                # 创建接口 - 使用设备对象ID
                iface_params = {**iface_data, "device": {"id": device_map["C8Kv1"].id}}
                result = nb.dcim.interfaces.create(**iface_params)
                print(f"  [CREATED] C8Kv1:{iface_data['name']} 创建成功")
            except Exception as e:
                print(f"  [ERROR] 创建接口 C8Kv1:{iface_data['name']} 失败: {e}")
    
    # 创建C8Kv2接口
    if "C8Kv2" in device_map:
        for iface_data in c8kv2_interfaces:
            try:
                # 先查找是否已存在
                existing = list(nb.dcim.interfaces.filter(device_id=device_map["C8Kv2"].id, name=iface_data["name"]))
                if existing:
                    print(f"  [FOUND] C8Kv2:{iface_data['name']} 已存在")
                    continue
                
                # 创建接口 - 使用设备对象ID
                iface_params = {**iface_data, "device": {"id": device_map["C8Kv2"].id}}
                result = nb.dcim.interfaces.create(**iface_params)
                print(f"  [CREATED] C8Kv2:{iface_data['name']} 创建成功")
            except Exception as e:
                print(f"  [ERROR] 创建接口 C8Kv2:{iface_data['name']} 失败: {e}")


def populate_ip_addresses(devices):
    """录入IP地址和前缀"""
    print("\n=== 录入IP地址和前缀 ===")
    
    # 重新从NetBox读取设备对象，避免使用旧缓存对象导致外键序列化异常
    device_map = {}
    for device_name in ["C8Kv1", "C8Kv2"]:
        device_obj = nb.dcim.devices.get(name=device_name)
        if device_obj:
            device_map[device_name] = device_obj
    
    # 获取Site对象
    sites = list(nb.dcim.sites.filter(name="QYT_Site"))
    site_id = sites[0].id if sites else None
    
    # 创建Prefix
    prefixes = [
        {"prefix": "10.10.1.0/24", "site": site_id, "description": "管理网络"},
        {"prefix": "137.78.5.0/24", "site": site_id, "description": "业务网络1"},
        {"prefix": "61.128.1.0/24", "site": site_id, "description": "业务网络2"},
    ]
    
    for prefix_data in prefixes:
        try:
            existing = list(nb.ipam.prefixes.filter(prefix=prefix_data["prefix"]))
            if existing:
                print(f"  [FOUND] {prefix_data['prefix']} 已存在")
                continue
            
            result = nb.ipam.prefixes.create(**prefix_data)
            print(f"  [CREATED] {prefix_data['prefix']} 创建成功")
        except Exception as e:
            print(f"  [ERROR] 创建前缀 {prefix_data['prefix']} 失败: {e}")
    
    # 创建IP地址
    ip_addresses = [
        {"address": "10.10.1.201/24", "device_name": "C8Kv1", "interface_name": "GigabitEthernet1"},
        {"address": "137.78.5.254/24", "device_name": "C8Kv1", "interface_name": "GigabitEthernet2"},
        {"address": "61.128.1.254/24", "device_name": "C8Kv1", "interface_name": "GigabitEthernet3"},
        {"address": "1.1.1.1/32", "device_name": "C8Kv1", "interface_name": "Loopback0"},
        {"address": "10.10.1.202/24", "device_name": "C8Kv2", "interface_name": "GigabitEthernet1"},
        {"address": "137.78.5.253/24", "device_name": "C8Kv2", "interface_name": "GigabitEthernet2"},
        {"address": "61.128.1.253/24", "device_name": "C8Kv2", "interface_name": "GigabitEthernet3"},
        {"address": "2.2.2.2/32", "device_name": "C8Kv2", "interface_name": "Loopback0"},
    ]
    
    for ip_data in ip_addresses:
        try:
            device = device_map.get(ip_data["device_name"])
            if not device:
                print(f"  [ERROR] 找不到设备 {ip_data['device_name']}")
                continue
            
            # 先查找接口
            interfaces = list(nb.dcim.interfaces.filter(device_id=device.id, name=ip_data["interface_name"]))
            if not interfaces:
                print(f"  [ERROR] 找不到接口 {ip_data['device_name']}:{ip_data['interface_name']}")
                continue
            
            interface_id = interfaces[0].id
            
            existing = list(nb.ipam.ip_addresses.filter(address=ip_data["address"]))
            if existing:
                print(f"  [FOUND] {ip_data['address']} 已存在")
                # 更新接口关联
                ip_obj = existing[0]
                if not ip_obj.assigned_object_id:
                    ip_obj.assigned_object_type = "dcim.interface"
                    ip_obj.assigned_object_id = interface_id
                    ip_obj.save()
                    print(f"  [UPDATED] {ip_data['address']} 关联接口成功")
                continue
            
            result = nb.ipam.ip_addresses.create(
                address=ip_data["address"],
                assigned_object_type="dcim.interface",
                assigned_object_id=interface_id
            )
            print(f"  [CREATED] {ip_data['address']} 创建成功")
        except Exception as e:
            print(f"  [ERROR] 创建IP地址 {ip_data['address']} 失败: {e}")
    
    # 更新设备的primary_ip4
    print("\n=== 更新设备主IP地址 ===")
    if "C8Kv1" in device_map:
        try:
            c8kv1 = device_map["C8Kv1"]
            mgmt_ips = list(nb.ipam.ip_addresses.filter(address="10.10.1.201/24"))
            if mgmt_ips:
                c8kv1.primary_ip4 = {"id": mgmt_ips[0].id}
                c8kv1.save()
                print("  [UPDATED] C8Kv1 primary_ip4 设置成功")
        except Exception as e:
            print(f"  [ERROR] 设置C8Kv1 primary_ip4失败: {e}")
    
    if "C8Kv2" in device_map:
        try:
            c8kv2 = device_map["C8Kv2"]
            mgmt_ips = list(nb.ipam.ip_addresses.filter(address="10.10.1.202/24"))
            if mgmt_ips:
                c8kv2.primary_ip4 = {"id": mgmt_ips[0].id}
                c8kv2.save()
                print("  [UPDATED] C8Kv2 primary_ip4 设置成功")
        except Exception as e:
            print(f"  [ERROR] 设置C8Kv2 primary_ip4失败: {e}")


def populate_ospf_config_context():
    """录入OSPF配置上下文数据"""
    print("\n=== 录入OSPF配置上下文 ===")
    
    # C8Kv1 OSPF配置
    c8kv1_config = {
        "router": {
            "ospf": {
                "process_id": 1,
                "router_id": "1.1.1.1",
                "network_list": [
                    {"area": 0, "network": "1.1.1.0", "wildmask": "0.0.0.255"},
                    {"area": 0, "network": "137.78.5.0", "wildmask": "0.0.0.255"},
                    {"area": 0, "network": "61.128.1.0", "wildmask": "0.0.0.255"},
                ]
            }
        }
    }
    
    # C8Kv2 OSPF配置
    c8kv2_config = {
        "router": {
            "ospf": {
                "process_id": 1,
                "router_id": "2.2.2.2",
                "network_list": [
                    {"area": 0, "network": "2.2.2.0", "wildmask": "0.0.0.255"},
                    {"area": 0, "network": "137.78.5.0", "wildmask": "0.0.0.255"},
                    {"area": 0, "network": "61.128.1.0", "wildmask": "0.0.0.255"},
                ]
            }
        }
    }
    
    # 更新C8Kv1配置上下文
    try:
        c8kv1 = list(nb.dcim.devices.filter(name="C8Kv1"))
        if c8kv1:
            c8kv1[0].config_context = c8kv1_config
            c8kv1[0].save()
            print("  [UPDATED] C8Kv1 OSPF配置上下文更新成功")
    except Exception as e:
        print(f"  [ERROR] 更新C8Kv1配置上下文失败: {e}")
    
    # 更新C8Kv2配置上下文
    try:
        c8kv2 = list(nb.dcim.devices.filter(name="C8Kv2"))
        if c8kv2:
            c8kv2[0].config_context = c8kv2_config
            c8kv2[0].save()
            print("  [UPDATED] C8Kv2 OSPF配置上下文更新成功")
    except Exception as e:
        print(f"  [ERROR] 更新C8Kv2配置上下文失败: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("Netbox DAY11 - 网络拓扑数据录入")
    print("=" * 60)
    
    # 检查连接
    if not check_netbox_connection():
        print("\n请先启动Netbox并获取API Token")
        print("启动命令: cd homework/3.NetDevOps/DAY11/code && docker compose up -d")
        sys.exit(1)
    
    # 录入组织数据
    site = populate_organization()
    
    # 录入设备制造商和类型
    device_type = populate_manufacturers_and_types()
    
    # 录入设备角色和平台
    role, platform = populate_roles_and_platforms()
    
    # 录入设备信息
    devices = populate_devices(site, device_type, role, platform)
    
    # 录入接口信息
    populate_interfaces(devices)
    
    # 录入IP地址和前缀
    populate_ip_addresses(devices)
    
    # 录入OSPF配置上下文
    populate_ospf_config_context()
    
    print("\n" + "=" * 60)
    print("数据录入完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
