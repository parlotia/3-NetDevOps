# NetDevOps DAY8 — BGP 前缀阈值邮件告警系统（EEM + Guestshell）

## 作业背景

构建一套完整的 BGP 前缀阈值自动告警系统：在 Cisco IOS-XE 路由器上配置 `maximum-prefix warning-only`，当 BGP 邻居发送的前缀数达到阈值时触发 `%BGP-4-MAXPFX` Syslog 日志，由 EEM Applet 捕获后调用 Guestshell 中的 Python 脚本，通过 QQ 邮箱 SMTP 发送告警邮件。实现全链路：BGP 超限 → Syslog → EEM → Guestshell → 邮件通知。

## 实验环境

| 设备 | IP | AS | 角色 |
|------|-----|-----|------|
| R1 (C8KV-1) | 10.10.1.200 | 65001 | 配置 maximum-prefix 2 warning-only |
| R2 (C8KV-2) | 10.10.1.201 | 65002 | 发布 2 条前缀触发告警 |
| Linux 服务器 | 10.10.1.205 | - | FTP 中转站 |
| FTP 服务器 | 10.10.1.110 | - | admin/Cisc0123 |
| QQ 邮箱 SMTP | smtp.qq.com:465 | - | SSL 加密连接 |

## 项目结构

```
DAY8/
├── task1_bgp_max_prefix.py              # 自动化：RESTCONF配置BGP + maximum-prefix
├── task2_eem_guestshell.py              # 自动化：配置EEM Applet + 部署Guestshell脚本
├── task3_email_alert.py                 # 自动化：SCP上传 + 部署 + 本地模拟测试
├── task4_e2e_verify.py                  # 自动化：端到端验证（clear bgp触发）
├── bgp_threshold_notification.py        # 核心告警脚本（运行于Guestshell）
├── qyt_smtp_attachment.py               # SMTP邮件工具（SSL连接QQ邮箱）
├── deploy_to_r1.py                      # FTP部署脚本到路由器
├── guestshell_net_setup.py              # Guestshell网络初始化
├── test_dns.py                          # DNS连通性测试
├── DAY8_BGP前缀阈值邮件告警.md          # 详细实验文档（含踩坑记录）
├── DAY8_任务记录.txt                    # 任务执行记录
└── README.md                            # 本文档
```

## 任务说明

### 任务一：配置 BGP 邻居与 maximum-prefix 阈值

**要求：**
在 R1 上配置 BGP 邻居 R2，设置 `maximum-prefix 2 warning-only`，使 R1 在接收前缀达到阈值时产生 `%BGP-4-MAXPFX` Syslog 日志。

**路由器配置：**

```
! R1 (AS 65001)
router bgp 65001
 network 1.1.1.0 mask 255.255.255.0
 neighbor 10.10.1.201 remote-as 65002
 neighbor 10.10.1.201 ebgp-multihop 255
 neighbor 10.10.1.201 maximum-prefix 2 warning-only

! R2 (AS 65002) - 发布2条前缀触发告警
router bgp 65002
 network 2.2.2.0 mask 255.255.255.0
 network 22.2.2.0 mask 255.255.255.0
 neighbor 10.10.1.200 remote-as 65001
```

**触发后的 Syslog 格式：**
```
%BGP-4-MAXPFX: Number of prefixes received from 10.10.1.201 (afi 0) reaches 2, max 2
```

### 任务二：配置 EEM Applet + Guestshell 脚本部署

**要求：**
1. 启用 IOx 和 Guestshell
2. 配置 VirtualPortGroup0 + NAT 使 Guestshell 能访问互联网
3. 通过 FTP 部署 Python 脚本到 Guestshell
4. 配置 EEM Applet 捕获 `%BGP-4-MAXPFX` 日志并调用脚本

**EEM Applet 配置：**

```
event manager applet bgp_prefix_threshold_notification
 event syslog pattern "BGP-4-MAXPFX" maxrun 60
 action 1.0 regexp "from ([0-9.]+)" "$_syslog_msg" ipaddr_full ipaddr
 action 2.0 regexp "reaches ([0-9]+)" "$_syslog_msg" cur_full current_prefix
 action 3.0 regexp "max ([0-9]+)" "$_syslog_msg" max_full max_prefix
 action 4.0 string trim "$ipaddr"
 action 5.0 string trim "$current_prefix"
 action 6.0 string trim "$max_prefix"
 action 7.0 cli command "enable"
 action 8.0 cli command "guestshell run python3 /home/guestshell/bgp_threshold_notification.py received from $ipaddr : $current_prefix exceeds limit $max_prefix"
```

### 任务三：邮件告警脚本

**核心逻辑：**
```python
# EEM传入参数: "received from 10.10.1.201 : 2 exceeds limit 2"
para_raw = ' '.join(sys.argv[1:]).strip()
match = re.match(r'received from ([0-9.]+) : (\d+) exceeds limit (\d+)', para_raw)
bgp_neighbor = match.group(1)    # 10.10.1.201
current_prefix = match.group(2)  # 2
max_prefix = match.group(3)      # 2
# 拼接邮件 → smtplib.SMTP_SSL('smtp.qq.com', 465) 发送
```

**预期输出：**
```
[!] BGP前缀阈值告警!
    BGP邻居: 10.10.1.201
    当前前缀数: 2
    最大前缀阈值: 2
[+] 邮件已经成功发出！
```

### 任务四：端到端验证

```
clear ip bgp 10.10.1.201          # 触发BGP重建 → 前缀超限
show logging | include MAXPFX     # 确认Syslog产生
show event manager history events  # 确认EEM执行
# 检查QQ邮箱收到告警邮件
```

## 完整数据流

```
BGP前缀超限
  → IOS-XE产生 %BGP-4-MAXPFX SYSLOG日志
  → EEM Applet 捕获日志 (pattern "BGP-4-MAXPFX")
  → EEM regexp提取: ipaddr / current_prefix / max_prefix
  → EEM先 enable 切特权模式
  → EEM执行: guestshell run python3 bgp_threshold_notification.py ...
  → Python脚本 re.match 解析参数, 拼接邮件正文
  → qyt_smtp_attachment() → SMTP_SSL('smtp.qq.com', 465) 发送
  → QQ邮箱收到BGP前缀阈值告警邮件
```

**网络路径：**
```
Guestshell(192.168.1.2) → eth0 → VPG0(192.168.1.1) → NAT → Gi2(DHCP) → 互联网 → smtp.qq.com:465
```

## 运行步骤

```bash
# 1. 自动化配置BGP + maximum-prefix
cd /netdevops/homework/3.NetDevOps/DAY8/
python task1_bgp_max_prefix.py

# 2. 自动化部署EEM + Guestshell
python task2_eem_guestshell.py

# 3. 部署告警脚本并本地测试
python task3_email_alert.py

# 4. 端到端验证（清除BGP触发真实告警）
python task4_e2e_verify.py
```

## 关键踩坑记录

| 问题 | 现象 | 解决方案 |
|------|------|---------|
| EEM 默认用户模式 | `% Invalid input detected` | action 中先 `cli command "enable"` |
| EEM regexp 变量 | 第一变量含前缀文本 | 使用双变量：`ipaddr_full ipaddr` |
| Guestshell 无 IP | eth0 无地址 | `guest-ipaddress` 必须在 `app-vnic gateway0` 子模式下 |
| Python 3.6 编码 | `reconfigure()` 不存在 | 使用 `io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')` |
| SCP 不支持 | C8KV 无 SCP server | FTP → bootflash → guest-share → Guestshell |

## 知识点

- BGP `maximum-prefix` 阈值告警机制（warning-only vs shutdown）
- EEM Applet 事件驱动编程（syslog pattern + regexp + cli command）
- IOS-XE Guestshell 容器化 Linux 环境
- VirtualPortGroup + NAT 实现 Guestshell 外网访问
- `re.match` 正则参数解析（替代 sys.argv 硬索引）
- `smtplib.SMTP_SSL` QQ 邮箱 SSL 连接
- FTP 文件中转部署流程（FTP → bootflash → guest-share）
- RESTCONF 自动化路由器配置

## 截图清单

1. `show ip bgp summary` 邻居建立成功
2. `show logging | include MAXPFX` 阈值告警日志
3. `show event manager history events` EEM 执行记录
4. Guestshell 脚本手工测试输出
5. QQ 邮箱收到的 BGP 告警邮件截图

## 提交文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `task1_bgp_max_prefix.py` | Python | RESTCONF 自动配置 BGP + maximum-prefix |
| `task2_eem_guestshell.py` | Python | 自动配置 EEM Applet + 部署 Guestshell |
| `task3_email_alert.py` | Python | SCP 上传 + 部署 + 本地模拟测试 |
| `task4_e2e_verify.py` | Python | 端到端验证（clear bgp 触发真实告警） |
| `bgp_threshold_notification.py` | Python | 核心告警脚本（Guestshell 中运行） |
| `qyt_smtp_attachment.py` | Python | SMTP 邮件工具（SSL 连接 QQ 邮箱） |
| `deploy_to_r1.py` | Python | FTP 部署脚本到路由器 |
| `guestshell_net_setup.py` | Python | Guestshell 网络初始化配置 |
| `DAY8_BGP前缀阈值邮件告警.md` | 文档 | 详细实验文档（含 10 条踩坑记录） |
| `README.md` | 文档 | 本文档 |
