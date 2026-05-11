# NetDevOps DAY11 - NetBox 实战

## 实验目标

复刻课堂上的 NetBox 实验，并结合自己的真实环境完成以下任务：

- 使用 NetBox 记录实际网络拓扑
- 按照 `Organization -> Devices -> IPAM -> Config Context` 的结构录入资源
- 使用 [`pynetbox`](code/day11_netbox_populate.py:26) 读取和写入 NetBox 数据
- 使用 [`netmiko`](code/day11_netbox_netmiko_config.py:22) 根据 NetBox 中的数据下发设备配置

---

## 实际环境信息

本次作业使用两台真实设备：

| 设备 | 管理 IP | 接口信息 |
|------|--------|----------|
| C8Kv1 | 10.10.1.201 | GigabitEthernet1: 10.10.1.201/24<br>GigabitEthernet2: 137.78.5.254/24<br>GigabitEthernet3: 61.128.1.254/24<br>Loopback0: 1.1.1.1/32 |
| C8Kv2 | 10.10.1.202 | GigabitEthernet1: 10.10.1.202/24<br>GigabitEthernet2: 137.78.5.253/24<br>GigabitEthernet3: 61.128.1.253/24<br>Loopback0: 2.2.2.2/32 |

### OSPF 信息

- Area：0
- C8Kv1 Router ID：1.1.1.1
- C8Kv2 Router ID：2.2.2.2
- 邻居关系：两台设备通过 `GigabitEthernet2` 和 `GigabitEthernet3` 建立 OSPF 邻接

---

## NetBox 录入结构

按照课堂结构图，本次录入内容如下：

```text
Organization
├── Region: QYT
├── Site Group: QYT_Group
└── Site: QYT_Site

Devices
├── Manufacturer: Cisco
├── Device Type: C8000V
├── Device Role: Router
├── Platform: Cisco IOS
├── Device: C8Kv1
│   ├── GigabitEthernet1
│   ├── GigabitEthernet2
│   ├── GigabitEthernet3
│   └── Loopback0
└── Device: C8Kv2
    ├── GigabitEthernet1
    ├── GigabitEthernet2
    ├── GigabitEthernet3
    └── Loopback0

IPAM
├── Prefix: 10.10.1.0/24
├── Prefix: 137.78.5.0/24
├── Prefix: 61.128.1.0/24
└── IP Address: 各接口地址

Config Context
└── OSPF 配置数据
```

---

## 最终完成的文件

### 1. 数据录入脚本

- [`day11_netbox_populate.py`](code/day11_netbox_populate.py)

作用：
- 检查 NetBox API 连接
- 创建 Region、Site Group、Site
- 创建设备制造商、类型、角色、平台
- 创建设备、接口、IP、Prefix
- 设置 `Primary IPv4`
- 写入设备的 OSPF `Config Context`

### 2. 基于 NetBox 的配置下发脚本

- [`day11_netbox_netmiko_config.py`](code/day11_netbox_netmiko_config.py)

作用：
- 从 NetBox 读取设备、接口、主 IP、配置上下文
- 生成接口和 OSPF 配置命令
- 使用 `netmiko` 将配置下发到真实设备

---

## NetBox 登录信息

NetBox Web 地址：

- [`http://localhost:8080/login/`](http://localhost:8080/login/)

登录账号密码配置在 [`netbox.env`](code/env/netbox.env) 中：

- 用户名：`admin`
- 密码：`admin123`

对应字段：
- [`SUPERUSER_NAME`](code/env/netbox.env:2)
- [`SUPERUSER_PASSWORD`](code/env/netbox.env:4)

---

## 操作步骤

### 1. 启动 NetBox

```bash
cd /netdevops/homework/3.NetDevOps/DAY11/code && docker compose up -d
```

查看容器状态：

```bash
cd /netdevops/homework/3.NetDevOps/DAY11/code && docker compose ps
```

---

### 2. 验证 Web 页面是否可访问

```bash
curl -I http://localhost:8080/login/
```

如果返回 `200 OK`，说明 Web 服务正常。

---

### 3. 执行 NetBox 数据录入

```bash
cd /netdevops/homework/3.NetDevOps/DAY11/code && python3 day11_netbox_populate.py
```

成功后会看到以下关键输出：

- `QYT_Site 已存在`
- `C8Kv1 已存在`
- `C8Kv2 已存在`
- 各接口创建成功
- 各 IP 创建成功
- `primary_ip4 设置成功`
- `OSPF配置上下文更新成功`

---

### 4. 先测试“只读 NetBox 并生成配置”

这一步不会下发配置，只是确认 NetBox 中的数据能被正确读取。

```bash
cd /netdevops/homework/3.NetDevOps/DAY11/code && python3 - <<'PY'
from day11_netbox_netmiko_config import preview_configs
from pprint import pprint
pprint(preview_configs())
PY
```

该命令会调用 [`preview_configs()`](code/day11_netbox_netmiko_config.py:153)，输出：

- 设备名
- 管理 IP
- 生成的接口配置命令
- 生成的 OSPF 配置命令

---

### 5. 真正下发配置到设备

```bash
cd /netdevops/homework/3.NetDevOps/DAY11/code && python3 day11_netbox_netmiko_config.py
```

该脚本会调用 [`deploy_all_devices()`](code/day11_netbox_netmiko_config.py:166)，流程如下：

1. 从 NetBox 读取 `C8Kv1` 和 `C8Kv2`
2. 读取设备主管理 IP
3. 读取接口 IP 地址
4. 读取 `Config Context` 中的 OSPF 参数
5. 生成 IOS XE 配置命令
6. 使用 `netmiko` 并发下发到真实设备

---

## 如何在网页中查看结果

登录后推荐按这个顺序查看：

### 1. 查看站点信息

- `Organization -> Regions`
- `Organization -> Sites`

重点看：
- `QYT`
- `QYT_Site`

### 2. 查看设备信息

- `Devices -> Devices`

重点看：
- `C8Kv1`
- `C8Kv2`

进入设备详情页后重点检查：
- `Device Type`
- `Role`
- `Platform`
- `Site`
- `Primary IPv4`

### 3. 查看接口信息

在设备详情页中查看接口：
- `GigabitEthernet1`
- `GigabitEthernet2`
- `GigabitEthernet3`
- `Loopback0`

### 4. 查看 IP 地址和前缀

- `IPAM -> IP Addresses`
- `IPAM -> Prefixes`

应该能看到：
- `10.10.1.201/24`
- `10.10.1.202/24`
- `137.78.5.254/24`
- `137.78.5.253/24`
- `61.128.1.254/24`
- `61.128.1.253/24`
- `1.1.1.1/32`
- `2.2.2.2/32`

以及前缀：
- `10.10.1.0/24`
- `137.78.5.0/24`
- `61.128.1.0/24`

### 5. 查看 Config Context

进入设备详情页查看 `Config Context`，重点看：
- `process_id`
- `router_id`
- `network_list`

这部分就是课堂结构图里“配置数据”的核心内容。

---

## 测试命令汇总

### 启动 NetBox

```bash
cd /netdevops/homework/3.NetDevOps/DAY11/code && docker compose up -d
```

### 查看容器状态

```bash
cd /netdevops/homework/3.NetDevOps/DAY11/code && docker compose ps
```

### 检查登录页

```bash
curl -I http://localhost:8080/login/
```

### 执行数据录入

```bash
cd /netdevops/homework/3.NetDevOps/DAY11/code && python3 day11_netbox_populate.py
```

### 预览配置，不下发设备

```bash
cd /netdevops/homework/3.NetDevOps/DAY11/code && python3 - <<'PY'
from day11_netbox_netmiko_config import preview_configs
from pprint import pprint
pprint(preview_configs())
PY
```

### 下发配置到设备

```bash
cd /netdevops/homework/3.NetDevOps/DAY11/code && python3 day11_netbox_netmiko_config.py
```

### 直接检查 NetBox 中的设备与接口

```bash
cd /netdevops/homework/3.NetDevOps/DAY11/code && python3 - <<'PY'
import pynetbox
nb = pynetbox.api(url='http://localhost:8080', token='nbt_PuB77ohtZgkG.PBhDlGE1EDDlGnHYn37EOzUXwd9TQec8VDHGkllK')
for name in ['C8Kv1', 'C8Kv2']:
    d = nb.dcim.devices.get(name=name)
    print(name, 'primary_ip4=', d.primary_ip4)
    for i in nb.dcim.interfaces.filter(device_id=d.id):
        print(' ', i.name)
PY
```

---

## 设备侧验证命令

登录设备后执行：

### 验证 C8Kv1

```bash
ssh admin@10.10.1.201
```

```text
show ip interface brief
show run | section router ospf
show ip ospf neighbor
```

### 验证 C8Kv2

```bash
ssh admin@10.10.1.202
```

```text
show ip interface brief
show run | section router ospf
show ip ospf neighbor
```

重点验证：
- 接口 IP 地址是否正确
- `router ospf 1` 是否存在
- `router-id` 是否正确
- OSPF 邻居是否正常

---

## 本次踩坑与修复

### 1. NetBox 4.6 与 `pynetbox` 外键写入兼容问题

现象：
- 使用 `device=1`、`site=1` 等外键字段时，部分资源创建失败

修复：
- 在 [`day11_netbox_populate.py`](code/day11_netbox_populate.py) 中统一重新读取对象
- 接口与设备对象过滤时使用 `device_id`
- 设备缓存对象不直接复用，避免旧对象导致外键序列化异常

### 2. `Primary IPv4` 不能在设备创建时直接设置

现象：
- 设备创建时如果直接指定 `primary_ip4`，会因 IP 尚未创建而失败

修复：
- 先创建接口和 IP
- 再单独更新 `primary_ip4`

### 3. `Config Context` 适合作为 OSPF 配置数据来源

做法：
- 在 [`populate_ospf_config_context()`](code/day11_netbox_populate.py:343) 中将 OSPF 数据写入 NetBox
- 在 [`build_ospf_config()`](code/day11_netbox_netmiko_config.py:104) 中从 `Config Context` 读取并生成命令

### 4. 真实环境测试要先做配置预览

建议：
- 先执行 [`preview_configs()`](code/day11_netbox_netmiko_config.py:153)
- 确认生成命令正确后，再执行 [`deploy_all_devices()`](code/day11_netbox_netmiko_config.py:166)

---

## 目录结构

```text
DAY11/
├── README.md
└── code/
    ├── docker-compose.yaml
    ├── extra.py
    ├── env/
    │   ├── netbox.env
    │   ├── postgres.env
    │   └── redis.env
    ├── day11_netbox_populate.py
    └── day11_netbox_netmiko_config.py
```

---

## 最终结论

本次作业已经完成以下目标：

- NetBox 服务成功部署
- Web 页面可正常登录
- 使用真实设备环境完成拓扑录入
- 使用 [`pynetbox`](code/day11_netbox_populate.py:26) 成功写入和读取 NetBox 数据
- 使用 [`netmiko`](code/day11_netbox_netmiko_config.py:22) 生成并可下发设备配置
- 可通过网页、API、CLI 三种方式验证录入结果
