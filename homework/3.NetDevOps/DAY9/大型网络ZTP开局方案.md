# 大型网络 ZTP 开局全栈方案

> 基于 DAY9 作业双层配置分离架构的扩展思考：当设备从 2 台扩展到 1000+ 台、单厂商扩展到多厂商时，ZTP 系统如何设计。

---

## 一、核心挑战

| 维度 | 小规模（作业） | 大规模（生产） |
|------|---------------|---------------|
| 设备数量 | 2 台 C8Kv | 数百~数千台 |
| 厂商 | 单一（Cisco IOS-XE） | 多厂商（Cisco/华为/Arista/Juniper） |
| 设备类型 | 1 种（C8000V） | 多种（路由器/交换机/无线/防火墙） |
| 数据来源 | 手写 YAML | LLD/CMDB/自动采集 |
| 部署节奏 | 手动逐台 | 批量并行、分站点 |
| 容错 | 无 | 失败重试、回滚、告警 |

---

## 二、整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ZTP 管控平面                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌───────────────┐  │
│  │   CMDB      │   │  模板引擎    │   │  配置生成    │   │  状态追踪     │  │
│  │  设备台账   │──>│ Jinja2 渲染  │──>│  API 服务    │──>│  Dashboard    │  │
│  │  SN/型号/角色│   │ 多厂商模板   │   │  动态下发    │   │  部署进度     │  │
│  └─────────────┘   └─────────────┘   └─────────────┘   └───────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                            ZTP 数据平面                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌───────────────┐  │
│  │  DHCP 服务  │   │  HTTP/TFTP  │   │  镜像仓库    │   │  证书服务     │  │
│  │  多VLAN分区 │   │  文件分发    │   │  OS 版本管理 │   │  PKI/CA       │  │
│  └─────────────┘   └─────────────┘   └─────────────┘   └───────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  站点 A 设备            站点 B 设备              站点 C 设备                  │
│  Cisco + 华为           Cisco + Arista           华为 + Juniper              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 三、数据准备体系

### 3.1 数据来源与流转

```
┌──────────────────┐
│  网络规划文档     │   HLD: 架构设计、路由域划分、安全策略
│  (HLD / LLD)     │   LLD: IP编址、接口互联、VLAN表、设备清单
└────────┬─────────┘
         │ 人工录入或脚本解析
         ▼
┌──────────────────┐
│  结构化数据源     │   Excel / CSV / CMDB 数据库 / NetBox
│  (Single Source   │   字段：SN、型号、厂商、角色、站点、接口、IP...
│   of Truth)       │
└────────┬─────────┘
         │ Python 批量转换脚本
         ▼
┌──────────────────┐
│  ZTP 可消费数据   │   <SN>.yaml / <型号>.yaml / inventory.yaml
│  (YAML 文件)     │   直接被 Jinja2 模板引擎消费
└──────────────────┘
```

### 3.2 设备台账表设计（核心输入）

大规模开局的起点是**一张完整的设备清单表**：

| 字段 | 说明 | 示例 |
|------|------|------|
| SN | 设备序列号（唯一标识） | 94CSC2OWS8U |
| hostname | 设备命名 | BJ-DC1-CORE-R01 |
| vendor | 厂商 | cisco / huawei / arista |
| platform | 平台 | iosxe / vrp / eos |
| model | 具体型号 | C8000V / CE6800 / 7280R |
| role | 网络角色 | core / distribution / access / leaf / spine |
| site | 所在站点 | beijing_dc1 |
| rack | 机柜位置 | A-01-U20 |
| mgmt_ip | 管理 IP | 10.10.1.201/24 |
| mgmt_gw | 管理网关 | 10.10.1.1 |
| os_version | 目标 OS 版本 | 17.12.01a |
| interfaces | 接口规划（JSON/嵌套） | [{name, ip, mask, peer, purpose}] |
| routing | 路由配置（JSON/嵌套） | {ospf: {...}, bgp: {...}} |

### 3.3 从 Excel 批量生成 YAML 示例

```python
#!/usr/bin/env python3
"""
从设备规划表(CSV/Excel)批量生成 ZTP 所需的 YAML 数据文件
输入：devices_inventory.csv
输出：device_config_data/<SN>.yaml（每台设备一个文件）
"""
import csv
import yaml
import os

OUTPUT_DIR = 'specific_device_config/device_config_data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open('devices_inventory.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # 构造接口列表
        interface_list = []
        for i in range(1, 5):  # 最多 4 个接口
            if_name = row.get(f'if{i}_name', '').strip()
            if_ip = row.get(f'if{i}_ip', '').strip()
            if_mask = row.get(f'if{i}_mask', '').strip()
            if if_name and if_ip:
                interface_list.append({
                    'interface_name': if_name,
                    'interface_ip': if_ip,
                    'interface_mask': if_mask
                })

        # 构造 OSPF 网络列表
        ospf_networks = []
        for i in range(1, 5):
            net = row.get(f'ospf_net{i}', '').strip()
            wild = row.get(f'ospf_wild{i}', '').strip()
            area = row.get(f'ospf_area{i}', '0').strip()
            if net and wild:
                ospf_networks.append({
                    'network': net,
                    'wildmask': wild,
                    'area': int(area)
                })

        # 组装最终数据结构
        device_data = {
            'hostname': row['hostname'],
            'interface_list': interface_list,
        }
        if ospf_networks:
            device_data['ospf_process_id'] = int(row.get('ospf_pid', 1))
            device_data['router_id'] = row.get('router_id', '')
            device_data['ospf_network_list'] = ospf_networks

        # 写入 YAML 文件（以 SN 命名）
        sn = row['sn'].strip()
        output_path = os.path.join(OUTPUT_DIR, f'{sn}.yaml')
        with open(output_path, 'w', encoding='utf-8') as yf:
            yaml.dump(device_data, yf, default_flow_style=False, allow_unicode=True)
        print(f'生成: {output_path}')
```

---

## 四、多厂商模板体系

### 4.1 三维分层设计

```
templates/
├── vendors/                           # 第一维：厂商（决定命令语法）
│   ├── cisco_iosxe/
│   │   ├── common/                    # 所有 IOS-XE 设备共享的配置模块
│   │   │   ├── aaa.j2               # 认证授权（username/enable secret）
│   │   │   ├── ntp_dns.j2           # NTP + DNS 配置
│   │   │   ├── snmp.j2              # SNMP v2c/v3 配置
│   │   │   ├── syslog.j2            # Syslog 服务器配置
│   │   │   ├── line_vty.j2          # VTY 线路配置
│   │   │   └── netconf_restconf.j2  # 管理协议启用
│   │   ├── roles/                    # 第二维：角色（决定功能集）
│   │   │   ├── core_router.j2       # 核心路由器（BGP + MPLS + QoS）
│   │   │   ├── dist_switch.j2       # 汇聚交换机（OSPF + VLAN + STP）
│   │   │   └── access_switch.j2     # 接入交换机（Port-Security + DHCP Snooping）
│   │   └── models/                   # 第三维：型号（决定硬件特性）
│   │       ├── C8000V.j2            # 虚拟路由器（无 PoE、无堆叠）
│   │       ├── C9300.j2             # 接入交换机（PoE + 堆叠）
│   │       └── C9500.j2             # 核心交换机（VSS + 大表项）
│   │
│   ├── huawei_vrp/
│   │   ├── common/
│   │   │   ├── aaa.j2               # local-user + authentication-scheme
│   │   │   ├── ntp_dns.j2           # ntp unicast-server + dns resolve
│   │   │   ├── snmp.j2              # snmp-agent sys-info
│   │   │   └── syslog.j2            # info-center loghost
│   │   ├── roles/
│   │   │   ├── core_router.j2       # BGP + MPLS + VPN Instance
│   │   │   └── access_switch.j2     # port-security + dhcp snooping enable
│   │   └── models/
│   │       ├── CE6800.j2
│   │       └── S5700.j2
│   │
│   └── arista_eos/
│       ├── common/
│       ├── roles/
│       └── models/
│
└── shared/                            # 跨厂商共享的逻辑编排
    ├── base_config.j2                # 总入口模板（按厂商分发）
    └── validation.j2                 # 配置完整性校验规则
```

### 4.2 同一功能不同厂商模板对比

**OSPF 配置模板：**

```jinja2
{# cisco_iosxe/roles/core_router.j2 — OSPF 部分 #}
router ospf {{ ospf_process_id }}
 router-id {{ router_id }}
{% for net in ospf_network_list %}
 network {{ net.network }} {{ net.wildmask }} area {{ net.area }}
{% endfor %}
```

```jinja2
{# huawei_vrp/roles/core_router.j2 — OSPF 部分 #}
ospf {{ ospf_process_id }} router-id {{ router_id }}
{% for net in ospf_network_list %}
 area {{ net.area }}
  network {{ net.network }} {{ net.wildmask }}
{% endfor %}
```

```jinja2
{# arista_eos/roles/core_router.j2 — OSPF 部分 #}
router ospf {{ ospf_process_id }}
 router-id {{ router_id }}
{% for net in ospf_network_list %}
 network {{ net.network }}/{{ net.prefix_len }} area {{ net.area }}
{% endfor %}
```

**关键设计原则：YAML 数据结构统一，差异全在模板层。**

### 4.3 模板继承与组合

配置生成引擎按以下顺序组合模板：

```python
def generate_config(device_info):
    """
    根据设备信息生成完整配置
    组合顺序：common（通用基础）→ role（角色功能）→ model（型号特性）→ specific（个体参数）
    """
    vendor = device_info['vendor']       # cisco_iosxe / huawei_vrp
    role = device_info['role']           # core_router / access_switch
    model = device_info['model']         # C8000V / CE6800
    sn = device_info['sn']

    config_lines = []

    # 第一层：厂商通用配置（AAA/NTP/SNMP...）
    for template_name in ['aaa', 'ntp_dns', 'snmp', 'syslog', 'line_vty']:
        tpl = load_template(f'vendors/{vendor}/common/{template_name}.j2')
        config_lines += render(tpl, device_info)

    # 第二层：角色配置（路由协议/安全策略...）
    role_tpl = load_template(f'vendors/{vendor}/roles/{role}.j2')
    config_lines += render(role_tpl, device_info)

    # 第三层：型号特有配置（硬件相关参数）
    model_tpl = load_template(f'vendors/{vendor}/models/{model}.j2')
    config_lines += render(model_tpl, device_info)

    # 第四层：设备个体配置（接口IP/hostname...）
    specific_data = load_yaml(f'device_config_data/{sn}.yaml')
    specific_tpl = load_template(f'vendors/{vendor}/specific/interfaces.j2')
    config_lines += render(specific_tpl, specific_data)

    return config_lines
```

---

## 五、DHCP 多厂商适配

### 5.1 不同厂商的 ZTP 触发机制

| 厂商 | 触发条件 | bootfile 传递方式 | 脚本语言 | 下载协议 |
|------|---------|------------------|---------|---------|
| Cisco IOS-XE | 无 startup-config | DHCP Option 67 | Python（Guestshell） | HTTP/HTTPS |
| Cisco NX-OS | 无 startup-config | DHCP Option 67 | Python（Bash Shell） | HTTP/TFTP |
| 华为 VRP | 无 vrpcfg.zip | DHCP Option 148/149 | 配置文件直接下发 | TFTP/FTP/HTTP |
| Arista EOS | 无 startup-config | DHCP Option 67 | Python/Bash | HTTP/TFTP |
| Juniper Junos | 无 juniper.conf | DHCP Option 43/150 | Junos config 或 Shell | TFTP/HTTP/FTP |

### 5.2 多厂商 DHCP 配置策略

```conf
# dnsmasq 按厂商 Vendor Class (Option 60) 分发不同 bootfile

# Cisco IOS-XE 设备
dhcp-vendorclass=set:cisco-iosxe,ciscoSystems
dhcp-boot=tag:cisco-iosxe,http://10.10.1.205/ztp/cisco/ztp_device.py

# 华为设备
dhcp-vendorclass=set:huawei,Huawei
dhcp-option=tag:huawei,option:tftp-server,10.10.1.205
dhcp-option=tag:huawei,148,"startup.cfg"
dhcp-option=tag:huawei,149,"/ztp/huawei/"

# Arista EOS 设备
dhcp-vendorclass=set:arista,Arista
dhcp-boot=tag:arista,http://10.10.1.205/ztp/arista/ztp_bootstrap.py

# 通用兜底（未识别厂商）
dhcp-boot=http://10.10.1.205/ztp/generic/bootstrap.py
```

**核心要点**：通过 DHCP Option 60（Vendor Class Identifier）区分厂商，下发不同的启动脚本。

---

## 六、设备端脚本适配

### 6.1 Cisco IOS-XE（Guestshell Python）

```python
# 在 Guestshell 中执行，调用 cli 模块
import cli, json, os

sn = extract_sn(cli.execute('show version'))
response = os.popen(f'curl -s -X POST ... http://server/api/config/{sn}')
config_list = json.loads(response.read()).get('config')
cli.configurep(config_list)
```

### 6.2 华为 VRP（配置文件直接下发）

华为设备不运行脚本，而是直接下载配置文件并应用：
- 服务端根据 MAC/Option 61 识别设备
- 动态生成 `vrpcfg.zip`（包含 startup.cfg）
- 设备自动下载并加载

### 6.3 Arista EOS（Bash/Python）

```python
# EOS 上的 ZTP 脚本类似 Linux 环境
import subprocess, json, requests

sn = subprocess.check_output(['Cli', '-c', 'show version | json'])
sn = json.loads(sn)['serialNumber']
config = requests.post(f'http://server/api/config/{sn}').json()
# EOS 通过 eAPI 或直接写文件应用配置
```

---

## 七、流程编排与状态管理

### 7.1 完整生命周期

```
                    ┌───────────────────────────────────┐
                    │          ZTP 状态机                │
                    └───────────────────────────────────┘

 ┌────────┐   ┌────────────┐   ┌────────────┐   ┌──────────────┐   ┌────────┐
 │ 待上线  │──>│  DHCP 获取  │──>│ 脚本下载    │──>│  配置下发     │──>│ 已完成  │
 │PENDING │   │DHCP_ACQUIRED│   │SCRIPT_LOADED│   │CONFIG_APPLIED│   │COMPLETE│
 └────────┘   └──────┬─────┘   └──────┬─────┘   └──────┬───────┘   └────────┘
                      │                │                │
                      ▼                ▼                ▼
                 ┌─────────┐     ┌─────────┐     ┌──────────┐
                 │DHCP失败  │     │下载失败  │     │配置失败   │
                 │重试3次   │     │切备用URL │     │回滚基线   │
                 │→告警     │     │→告警     │     │→人工介入  │
                 └─────────┘     └─────────┘     └──────────┘
```

### 7.2 状态回调机制

设备端脚本在每个关键步骤向服务器上报状态：

```python
def report_status(server, sn, stage, status, message=""):
    """设备端状态上报"""
    payload = {
        "sn": sn,
        "stage": stage,       # dhcp / download / config / complete
        "status": status,     # success / failed
        "message": message,
        "timestamp": time.time()
    }
    os.popen(f'curl -s -X POST -H "Content-Type: application/json" '
             f'-d \'{json.dumps(payload)}\' http://{server}/api/status')
```

### 7.3 部署 Dashboard

服务端实时展示：

| 站点 | 总数 | 待上线 | DHCP | 下载中 | 配置中 | 完成 | 失败 |
|------|------|-------|------|-------|-------|------|------|
| 北京 DC1 | 200 | 50 | 10 | 5 | 15 | 115 | 5 |
| 上海 DC2 | 150 | 0 | 0 | 3 | 7 | 140 | 0 |
| 广州分支 | 80 | 80 | 0 | 0 | 0 | 0 | 0 |

---

## 八、OS 版本管理与固件升级

ZTP 不仅下发配置，还应确保 OS 版本一致：

```python
def check_and_upgrade(device_sn, target_version):
    """
    ZTP 流程中嵌入版本检查
    1. 获取当前版本
    2. 对比目标版本
    3. 不一致则下载固件并升级
    """
    current_version = get_current_version()
    if current_version != target_version:
        firmware_url = f'http://server/firmware/{model}/{target_version}.bin'
        download_firmware(firmware_url)
        install_firmware()
        # 设备重启后会重新走 ZTP，此时版本已正确
        reboot()
```

镜像仓库按厂商/型号/版本组织：

```
firmware/
├── cisco_iosxe/
│   ├── C8000V/
│   │   ├── 17.12.01a.bin
│   │   └── 17.11.03.bin
│   └── C9300/
│       └── 17.09.04a.bin
├── huawei_vrp/
│   └── CE6800/
│       └── V200R022C00SPC500.cc
└── arista_eos/
    └── 7280R/
        └── EOS-4.32.0F.swi
```

---

## 九、安全考量

| 安全点 | 方案 |
|--------|------|
| 配置传输加密 | bootfile 通过 HTTPS 下载 + 配置 API 加 TLS |
| 敏感信息保护 | 密码类参数使用 HashiCorp Vault / Ansible Vault 加密存储 |
| 设备身份验证 | 基于 SN + MAC 双因素校验，防止伪造设备获取配置 |
| 证书管理 | 企业 CA 签发设备证书，ZTP 过程中自动注入 |
| 审计日志 | 记录每次配置下发的 SN、时间、配置内容 hash |
| 网络隔离 | ZTP VLAN 与生产 VLAN 隔离，部署完成后切换 |

---

## 十、多站点部署架构

```
┌─────────────────────────────────────────────────────┐
│              中心管控平台（总部）                      │
│  CMDB + 模板仓库 + 策略引擎 + 全局 Dashboard         │
└───────────────┬────────────────┬────────────────────┘
                │ API 同步        │ API 同步
        ┌───────▼──────┐  ┌──────▼───────┐
        │  站点A ZTP    │  │  站点B ZTP    │
        │  本地 DHCP    │  │  本地 DHCP    │
        │  本地 HTTP    │  │  本地 HTTP    │
        │  本地缓存     │  │  本地缓存     │
        └──────────────┘  └──────────────┘
```

**设计原则**：
- 模板和策略**中心管理**，全局一致
- 数据和服务**站点本地**，降低延迟、不依赖 WAN
- 状态**双向同步**，中心可看全局、站点可独立运行

---

## 十一、与 DAY9 作业的对应关系

| 大型 ZTP 组件 | DAY9 作业中的对应 |
|-------------|-----------------|
| CMDB 设备台账 | `device_config_data/<SN>.yaml`（手写 2 个） |
| 模板引擎 | `ztp_server.py` + Jinja2 模板 |
| 配置 API | `flask_server.py` 的 `/device_config_json` |
| DHCP 服务 | `dnsmasq_ztp.conf` |
| 文件分发 | Apache `ztp_apache.conf` |
| 设备端脚本 | `ztp_device.py`（Guestshell 执行） |
| 状态追踪 | `/tmp/ztp_debug.log`（最简化版） |
| 多厂商支持 | 无（仅 Cisco IOS-XE） |
| OS 版本管理 | 无 |
| 安全加密 | 无（HTTP 明文） |

**作业是最小可运行原型，理解架构思想后，规模化就是扩数据源、扩模板、加运维能力的过程。**

---

## 十二、推荐工具链

| 层面 | 工具 | 用途 |
|------|------|------|
| CMDB | NetBox / IT-Flow | 设备资产管理、IP 地址管理 |
| 模板管理 | Git 仓库 | 版本控制、Code Review、CI/CD |
| 配置生成 | Jinja2 / Nornir | 批量渲染 + 并发下发 |
| 自动化 | Ansible / Salt | Day2 变更、合规检查 |
| DHCP | ISC DHCP / dnsmasq / Kea | 地址分配 + Option 下发 |
| 文件服务 | Nginx / Apache | 高性能 bootfile 分发 |
| 监控 | Grafana + Prometheus | ZTP 进度可视化 |
| 密钥管理 | HashiCorp Vault | 敏感信息加密存储 |
| CI/CD | GitLab CI / Jenkins | 模板变更自动测试 + 部署 |

---

## 十三、总结

**大型网络 ZTP 开局 = 五个核心能力的组合：**

1. **数据能力**：从 LLD/CMDB 获取结构化设备信息（知道有什么设备）
2. **模板能力**：多厂商 × 多角色 × 多型号的 Jinja2 模板体系（知道怎么配）
3. **分发能力**：DHCP + HTTP/TFTP 按厂商下发正确的启动脚本（知道怎么送达）
4. **执行能力**：设备端脚本适配各厂商 API（知道怎么应用）
5. **运维能力**：状态追踪 + 失败重试 + 回滚 + 告警（知道成没成功）

DAY9 作业覆盖了 1~4 的核心原理，第 5 点（运维能力）是生产环境必须追加的工程化增强。
