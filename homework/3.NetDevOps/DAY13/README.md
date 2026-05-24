# NetDevOps DAY13 — Terraform 管理 IOS-XE 双机 eBGP

## 作业背景

使用 Terraform 的 Cisco IOS-XE Provider（CiscoDevNet/iosxe）通过 RESTCONF 协议统一管理两台 Cisco Catalyst 8000v 路由器，实现基础系统配置、接口地址配置、eBGP 邻居建立与路由通告，验证双方互学对端 Loopback 路由。体验 Infrastructure as Code 在网络设备上的应用。

## 实验环境

| 组件 | 版本/地址 |
|------|-----------|
| Linux 服务器 | 10.10.1.205 (Rocky Linux 9.7) |
| C8Kv1 | 10.10.1.201（管理口），172.16.12.1/24（Gi2） |
| C8Kv2 | 10.10.1.202（管理口），172.16.12.2/24（Gi2） |
| Terraform | v1.9.8 |
| IOS-XE Provider | CiscoDevNet/iosxe v0.17.0 |
| 设备凭据 | admin / Cisc0123 |
| 设备协议 | RESTCONF (HTTPS 443) |

## 项目结构

```
DAY13/
└── code/
    ├── main.tf                         # 根模块：引用c8kv1和c8kv2子模块
    ├── variables.tf                    # 全局变量（用户名/密码）
    ├── modules/
    │   ├── c8kv1/
    │   │   ├── main.tf                 # Provider配置（连接10.10.1.201）
    │   │   ├── variables.tf            # 模块变量
    │   │   ├── iosxe_system.tf         # 系统配置（hostname等）
    │   │   ├── iosxe_interface.tf      # 接口配置（Gi2 + Loopback0/1）
    │   │   └── iosxe_bgp.tf           # BGP配置（AS65001 + neighbor + network）
    │   └── c8kv2/
    │       ├── main.tf                 # Provider配置（连接10.10.1.202）
    │       ├── variables.tf            # 模块变量
    │       ├── iosxe_system.tf         # 系统配置
    │       ├── iosxe_interface.tf      # 接口配置
    │       └── iosxe_bgp.tf           # BGP配置（AS65002 + neighbor + network）
    └── 环境准备与路由器配置.md          # 详细实验文档（391行）
```

## 任务说明

### 任务一：Terraform 下发网络配置

**要求：**
1. 使用 Terraform modules 组织双设备配置
2. 通过 RESTCONF 协议下发配置（需先在设备上启用 `restconf` + `ip http secure-server`）
3. 配置内容包括：

| 资源类型 | C8Kv1 | C8Kv2 |
|---------|-------|-------|
| hostname | C8Kv1 | C8Kv2 |
| GigabitEthernet2 | 172.16.12.1/24 | 172.16.12.2/24 |
| Loopback0 | 1.1.1.1/24 | 2.2.2.2/24 |
| Loopback1 | 11.1.1.1/24 | 22.2.2.2/24 |
| BGP ASN | 65001 | 65002 |
| BGP neighbor | 172.16.12.2 remote-as 65002 | 172.16.12.1 remote-as 65001 |
| BGP network | 1.1.1.0/24, 11.1.1.0/24 | 2.2.2.0/24, 22.2.2.0/24 |

**Terraform 创建的资源类型：**
- `iosxe_system` — 系统配置
- `iosxe_interface_ethernet` — 以太网接口
- `iosxe_interface_loopback` — 环回接口
- `iosxe_bgp` — BGP 进程
- `iosxe_bgp_neighbor` — BGP 邻居
- `iosxe_bgp_address_family_ipv4` — IPv4 地址族
- `iosxe_bgp_ipv4_unicast_neighbor` — 邻居地址族激活

### 任务二：验证 BGP 邻居建立与路由学习

**预期结果：**
- C8Kv1 学习到 `2.2.2.0/24` 与 `22.2.2.0/24`（下一跳 172.16.12.2）
- C8Kv2 学习到 `1.1.1.0/24` 与 `11.1.1.0/24`（下一跳 172.16.12.1）

**验证命令：**
```cisco
show ip interface brief
show run | section router bgp
show ip bgp summary
show ip route bgp
```

## 运行步骤

```bash
# 0. 设备前置准备（两台路由器上执行）
# conf t → ip http secure-server → restconf → end → write memory

# 1. 进入代码目录
cd /netdevops/homework/3.NetDevOps/DAY13/code/

# 2. 设置环境变量（设备凭据）
export TF_VAR_DEVICE_LOGIN_USERNAME=admin
export TF_VAR_DEVICE_LOGIN_PASSWORD='Cisc0123'

# 3. Terraform 初始化（下载Provider）
terraform init

# 4. 格式化检查
terraform fmt -recursive

# 5. 配置验证
terraform validate

# 6. 执行计划（预览变更）
terraform plan

# 7. 应用配置（自动确认）
terraform apply -auto-approve
# 预期输出: Apply complete! Resources: 16 added, 0 changed, 0 destroyed.

# 8. 登录路由器验证
ssh admin@10.10.1.201
# show ip bgp summary → 确认邻居建立
# show ip route bgp → 确认学到对端路由
```

## 知识点

- Terraform HCL 语法与 module 模块化组织
- Terraform 工作流：init → fmt → validate → plan → apply
- CiscoDevNet/iosxe Provider（通过 RESTCONF 管理设备）
- Terraform 环境变量传参（`TF_VAR_` 前缀）
- eBGP 邻居配置与路由通告
- RESTCONF 作为 Terraform Provider 的底层传输
- Infrastructure as Code 在网络自动化中的应用

## 截图清单

1. `terraform init` 成功
2. `terraform validate` 成功
3. `terraform plan` 显示将创建 16 个资源
4. `terraform apply -auto-approve` 显示 Apply complete
5. C8Kv1 `show ip interface brief`（接口地址正确）
6. C8Kv1 `show ip bgp summary`（邻居建立，学到 2 条前缀）
7. C8Kv1 `show ip route bgp`（2.2.2.0/24 + 22.2.2.0/24）
8. C8Kv2 `show ip bgp summary`（邻居建立，学到 2 条前缀）
9. C8Kv2 `show ip route bgp`（1.1.1.0/24 + 11.1.1.0/24）

## 提交文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `code/main.tf` | Terraform | 根模块：引用 c8kv1/c8kv2 子模块 |
| `code/variables.tf` | Terraform | 全局变量定义（用户名/密码） |
| `code/modules/c8kv1/*.tf` | Terraform | C8Kv1 配置（system + interface + bgp） |
| `code/modules/c8kv2/*.tf` | Terraform | C8Kv2 配置（system + interface + bgp） |
| `code/环境准备与路由器配置.md` | 文档 | 详细实验文档（含验证命令和截图指导） |
| `README.md` | 文档 | 本文档 |
