# NetDevOps DAY8 - BGP前缀阈值邮件告警系统

## 实验环境

| 设备 | IP | AS | 角色 |
|------|-----|-----|------|
| R1 (C8KV-1) | 10.10.1.200 | 65001 | 配置 maximum-prefix 2 warning-only |
| R2 (C8KV-2) | 10.10.1.201 | 65002 | 发布2条前缀触发告警 |
| Linux服务器 | 10.10.1.205 | - | FTP中转 |
| FTP服务器 | 10.10.1.110 | - | admin/Cisc0123 |
| QQ邮箱SMTP | smtp.qq.com:465 | - | 1975141437@qq.com |

---

## 任务一：配置BGP邻居与maximum-prefix阈值

**题目**：在R1上配置BGP邻居R2，设置maximum-prefix 2 warning-only，使R1在接收前缀达到阈值时产生%BGP-4-MAXPFX SYSLOG日志。

### 操作步骤

**1. 配置Loopback接口（为BGP network命令提供路由）**

R1:
```
interface Loopback0
 ip address 1.1.1.1 255.255.255.0
```

R2:
```
interface Loopback0
 ip address 2.2.2.2 255.255.255.0
interface Loopback1
 ip address 22.2.2.2 255.255.255.0
```

**2. 配置BGP**

R1:
```
router bgp 65001
 bgp log-neighbor-changes
 network 1.1.1.0 mask 255.255.255.0
 neighbor 10.10.1.201 remote-as 65002
 neighbor 10.10.1.201 ebgp-multihop 255
 neighbor 10.10.1.201 maximum-prefix 2 warning-only
```

R2:
```
router bgp 65002
 bgp log-neighbor-changes
 network 2.2.2.0 mask 255.255.255.0
 network 22.2.2.0 mask 255.255.255.0
 neighbor 10.10.1.200 remote-as 65001
 neighbor 10.10.1.200 ebgp-multihop 255
```

**3. 验证**

```
show ip bgp summary
show logging | include MAXPFX
```

触发后的SYSLOG格式：
```
%BGP-4-MAXPFX: Number of prefixes received from 10.10.1.201 (afi 0) reaches 2, max 2
```

> 自动化脚本：`task1_bgp_max_prefix.py`（RESTCONF自动配置，含CLI备用命令）

---

## 任务二：配置EEM Applet + Guestshell脚本部署

**题目**：在R1上启用Guestshell并部署Python脚本，配置EEM Applet捕获%BGP-4-MAXPFX日志后自动调用Guestshell脚本。

### 操作步骤

**1. 启用IOx和Guestshell**

```
configure terminal
 iox
end
! 等待1-5分钟IOx初始化
guestshell enable
```

**2. 配置Guestshell网络**

```
configure terminal
 interface VirtualPortGroup0
  ip address 192.168.1.1 255.255.255.0
  ip nat inside
 interface GigabitEthernet2
  ip nat outside
 ip nat inside source list 1 interface GigabitEthernet2 overload
 access-list 1 permit 192.168.1.0 0.0.0.255
 app-hosting appid guestshell
  app-vnic gateway0 virtualportgroup 0 guest-interface 0
   guest-ipaddress 192.168.1.2 netmask 255.255.255.0
  app-default-gateway 192.168.1.1 guest-interface 0
  name-server0 8.8.8.8
end
```

> **关键**：`guest-ipaddress` 必须在 `app-vnic gateway0` 子模式下配置，否则Guestshell eth0无IP！

**3. 重启Guestshell使网络配置生效**

```
guestshell disable
guestshell enable
```

**4. 验证Guestshell网络**

```
guestshell run bash -c "ping -c 2 smtp.qq.com"
```

**5. 部署脚本到Guestshell**

```
configure terminal
 file prompt quiet
end
copy ftp://admin:Cisc0123@10.10.1.110/bgp_threshold_notification.py bootflash:
copy ftp://admin:Cisc0123@10.10.1.110/qyt_smtp_attachment.py bootflash:
copy bootflash:bgp_threshold_notification.py bootflash:guest-share/
copy bootflash:qyt_smtp_attachment.py bootflash:guest-share/
guestshell run bash -c "cp /bootflash/guest-share/bgp_threshold_notification.py /home/guestshell/"
guestshell run bash -c "cp /bootflash/guest-share/qyt_smtp_attachment.py /home/guestshell/"
```

**6. 配置EEM Applet**

```
configure terminal
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
 end
```

> **关键**：
> - `action 7.0 cli command "enable"` — EEM默认在用户模式执行，必须先enable切到特权模式才能运行`guestshell run`
> - `regexp`第一个变量是整段匹配，第二个才是捕获组。如 `ipaddr_full`="from 10.10.1.201"，`ipaddr`="10.10.1.201"

> 自动化脚本：`task2_eem_guestshell.py`

---

## 任务三：邮件告警脚本

**题目**：编写Guestshell脚本，解析EEM传入的参数，拼接告警邮件正文，通过QQ邮箱SMTP发送。

### 脚本说明

**bgp_threshold_notification.py** — 核心告警脚本

```python
#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""
BGP前缀阈值告警脚本 - 运行于IOS-XE Guestshell
由EEM Applet bgp_prefix_threshold_notification调用

EEM传入的参数格式示例:
  received from 10.10.1.201 : 2 exceeds limit 2
"""

import re
import sys
import io
from qyt_smtp_attachment import qyt_smtp_attachment

# Guestshell默认ASCII编码, 需强制切换为UTF-8以支持中文输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

MAIL_SERVER = 'smtp.qq.com'
MAIL_USER = '1975141437@qq.com'
MAIL_PASS = 'avpjlsuqzmwydjij'
MAIL_FROM = '1975141437@qq.com'
MAIL_TO = '1975141437@qq.com'

para_raw = ' '.join(sys.argv[1:]).strip()
match = re.match(r'received from ([0-9.]+) : (\d+) exceeds limit (\d+)', para_raw)

if match:
    bgp_neighbor = match.group(1)
    current_prefix = match.group(2)
    max_prefix = match.group(3)

    mail_subject = f'BGP前缀阈值告警 - 邻居 {bgp_neighbor}'
    mail_body = (
        f'Neighbor: {bgp_neighbor}\n'
        f'Now: {current_prefix}\n'
        f'Exceed the limit: {max_prefix}\n'
    )

    qyt_smtp_attachment(
        mailserver=MAIL_SERVER,
        username=MAIL_USER,
        password=MAIL_PASS,
        from_mail=MAIL_FROM,
        to_mail=MAIL_TO,
        subj=mail_subject,
        main_body=mail_body,
    )
```

**qyt_smtp_attachment.py** — SMTP邮件工具

- `smtplib.SMTP_SSL(mailserver, 465)` 连接QQ邮箱
- 支持正文(MIMEText) + 附件(MIMEApplication)

### 手工测试

```
guestshell run python3 /home/guestshell/bgp_threshold_notification.py "received from 10.10.1.201 : 2 exceeds limit 2"
```

预期输出：
```
[!] BGP前缀阈值告警!
    BGP邻居: 10.10.1.201
    当前前缀数: 2
    最大前缀阈值: 2
[+] 邮件已经成功发出！
```

> 自动化脚本：`task3_email_alert.py`

---

## 任务四：端到端验证

**题目**：清除BGP会话触发真实告警，验证 EEM→Guestshell→邮件 全链路。

### 操作步骤

**1. 触发真实BGP告警**

```
clear ip bgp 10.10.1.201
```

**2. 验证EEM捕获**

```
show logging | include MAXPFX
show event manager history events
```

**3. 检查QQ邮箱收到告警邮件**

> 自动化脚本：`task4_e2e_verify.py`

---

## 踩坑记录

### 1. EEM默认在用户EXEC模式执行CLI命令

EEM的`cli command`默认在用户模式（`C8Kv1>`）运行，而`guestshell run`只能在特权模式（`C8Kv1#`）执行。

**现象**：EEM日志显示 `% Invalid input detected at '^' marker`

**修复**：在guestshell命令前加 `action 7.0 cli command "enable"`

### 2. EEM regexp第一个变量是整段匹配而非捕获组

EEM regexp语法：`regexp "pattern" "input" 变量1(整段匹配) 变量2(第1个捕获组) ...`

**错误写法**：`regexp "from ([0-9.]+)" "$_syslog_msg" ipaddr` → ipaddr="from 10.10.1.201"（含前缀）

**正确写法**：`regexp "from ([0-9.]+)" "$_syslog_msg" ipaddr_full ipaddr` → ipaddr="10.10.1.201"（纯IP）

**现象**：EEM拼接出 `received from from 10.10.1.201 : reaches 2 exceeds limit max 2`，Python正则无法匹配

### 3. EEM正则必须匹配实际SYSLOG字段

实际SYSLOG格式为 `"reaches 2, max 2"`，而非之前误写的 `": 2"` 和 `"exceeds limit 2"`

**错误**：`regexp ": ([0-9]+)"` / `regexp "exceeds limit ([0-9]+)"`

**正确**：`regexp "reaches ([0-9]+)"` / `regexp "max ([0-9]+)"`

### 4. guest-ipaddress必须在gateway0子模式下配置

- **错误**：在 `app-hosting appid guestshell` 下直接输入 `guest-ipaddress` → Invalid input
- **正确**：先 `app-vnic gateway0 virtualportgroup 0 guest-interface 0` 进入子模式，再输入 `guest-ipaddress`
- 缺少此配置则Guestshell eth0无IP，网络完全不通

### 5. NAT outside必须配在实际上网口

本实验Gi1(10.10.1.200)是管理口，Gi2(192.168.72.132/DHCP)才是上网口。必须确认哪个接口能访问互联网。

### 6. Guestshell中bash -c不支持&&复合命令

- **错误**：`guestshell run bash -c "cp x y && chmod +x y"`
- **正确**：分两步执行

### 7. Guestshell Python 3.6不支持sys.stdout.reconfigure()

- **错误**：`sys.stdout.reconfigure(encoding='utf-8')`
- **正确**：`sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')`

### 8. SCP/SFTP到C8KV不支持

使用FTP中转：`FTP → bootflash → guest-share → Guestshell /home/guestshell/`

### 9. bootflash文件在Guestshell中不可直接访问

通过guest-share共享目录中转：
```
copy bootflash:x bootflash:guest-share/x    ! IOS-XE侧
cp /bootflash/guest-share/x /home/guestshell/  ! Guestshell侧
```

### 10. Guestshell中open()默认ASCII编码

写中文到文件需显式指定 `open(file, 'w', encoding='utf-8')`，否则报 `UnicodeEncodeError`

---

## 完整数据流

```
BGP前缀超限
  → IOS-XE产生 %BGP-4-MAXPFX SYSLOG日志
  → EEM Applet 捕获日志
  → EEM regexp提取: ipaddr / current_prefix / max_prefix (注意双变量写法)
  → EEM先enable切特权模式
  → EEM执行: guestshell run python3 /home/guestshell/bgp_threshold_notification.py ...
  → Python脚本re.match解析参数, 拼接邮件正文
  → qyt_smtp_attachment() → smtplib.SMTP_SSL('smtp.qq.com', 465) 发送邮件
  → QQ邮箱收到BGP前缀阈值告警邮件
```

网络路径：
```
Guestshell(192.168.1.2) → eth0 → VPG0(192.168.1.1) → NAT → Gi2(DHCP) → 互联网 → smtp.qq.com:465
```

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `bgp_threshold_notification.py` | 核心告警脚本，解析EEM参数并发送邮件 |
| `qyt_smtp_attachment.py` | SMTP邮件工具，SSL连接QQ邮箱 |
| `task1_bgp_max_prefix.py` | 自动化：RESTCONF配置BGP + maximum-prefix |
| `task2_eem_guestshell.py` | 自动化：配置EEM Applet + 部署Guestshell脚本 |
| `task3_email_alert.py` | 自动化：SCP上传 + 部署 + 本地模拟测试 |
| `task4_e2e_verify.py` | 自动化：端到端验证 |
