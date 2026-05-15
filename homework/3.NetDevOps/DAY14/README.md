# NetDevOps DAY14 - 基于老师 NSO 环境的作业重做

## 1. 先说明本次重做思路

DAY14 之前的版本把重点放在“直接对 IOS XE 设备做 RESTCONF SYSLOG 测试”，但老师后续 DAY15 的主题是 NSO CI/CD，因此 DAY14 更合理的衔接方式应该是：

1. 先按老师提供的 NSO 环境资料把控制器环境读透并确认可用
2. 以 NSO 作为控制面，完成设备纳管、同步、CLI 下发与验证
3. 将设备南向 RESTCONF 验证作为补充验证，而不是把 DAY14 写成纯设备 RESTCONF 实验

因此本次 README 按老师在 [`记录_1_nso操作(nso-6.1.8).md`](../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/记录_1_nso操作(nso-6.1.8).md) 中的真实流程重新整理，并结合当前机器实际状态进行修正。

---

## 2. 老师提供资料与安装包位置

本机已经在 [`../root`](../root) 下存在老师给的 NSO 相关资料和安装包，关键内容如下：

- 课程压缩包：[`../root/netdevops2023_iac_nso_pyats-ci.tar.gz`](../root/netdevops2023_iac_nso_pyats-ci.tar.gz)
- 课程压缩包副本：[`../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats-ci.tar.gz`](../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats-ci.tar.gz)
- 老师解压后的实验目录：[`../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats`](../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats)
- NSO 签名包：[`../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/nso_install_files/nso-6.1.8.linux.x86_64.signed.bin`](../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/nso_install_files/nso-6.1.8.linux.x86_64.signed.bin)
- NSO 安装器：[`../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/nso_install_files/nso-6.1.8.linux.x86_64.installer.bin`](../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/nso_install_files/nso-6.1.8.linux.x86_64.installer.bin)
- 老师操作记录：[`../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/记录_1_nso操作(nso-6.1.8).md`](../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/记录_1_nso操作(nso-6.1.8).md)

---

## 3. 当前环境真实确认结果

### 3.1 NSO 运行状态已正常

当前机器上已经存在本地安装目录与运行目录：

- 本地安装目录：[`../root/nso-6.1.8-local`](../root/nso-6.1.8-local)
- 运行目录：[`../root/nso-6.1.8-run`](../root/nso-6.1.8-run)

实际检查命令：

```bash
source /root/nso-6.1.8-local/ncsrc
/root/nso-6.1.8-local/bin/ncs --status
```

实际确认结果：

- NSO 版本：6.1.8
- 状态：`started`
- 已加载模块：`backplane, netconf, cdb, cli, snmp, webui`
- 已加载 NED：`cisco-ios-cli-3.8`

### 3.2 WebUI 已可访问

本机验证命令：

```bash
curl -s http://127.0.0.1:8080/login.html | head -n 5
```

已返回 HTML 登录页头部内容，说明 NSO WebUI 已启动。

### 3.3 设备纳管基础配置已存在

当前 NSO 中已存在老师实验所需的关键对象：

- authgroup：`qytadmin`
- device：`C8Kv1`
- 设备地址：`10.10.1.201`
- NED：`cisco-ios-cli-3.8`
- 协议：`ssh`

对应检查命令：

```bash
source /root/nso-6.1.8-local/ncsrc
printf 'show running-config devices authgroups | nomore\nshow running-config devices device | de-select config | nomore\n' | /root/nso-6.1.8-local/bin/ncs_cli -C --noaaa
```

### 3.4 南向连接已验证通过

执行：

```bash
source /root/nso-6.1.8-local/ncsrc
printf 'devices device C8Kv1 connect\ndevices sync-from device C8Kv1\nshow running-config devices device C8Kv1 config ios:logging | nomore\n' | /root/nso-6.1.8-local/bin/ncs_cli -C --noaaa
```

结果确认：

- `connect` 成功
- `sync-from` 成功
- 设备当前 NSO 视图下的 SYSLOG 配置为：
  - `logging host 10.10.1.205`
  - `logging trap debugging`

### 3.5 设备 RESTCONF 也已验证可读

执行：

```bash
curl -sk -u admin:Cisc0123 \
  -H 'Accept: application/yang-data+json' \
  https://10.10.1.201/restconf/data/Cisco-IOS-XE-native:native/logging
```

返回结果确认：

- `hostip` 为 `10.10.1.205`
- `trap.severity` 为 `7`
- 与 `debugging` 级别对应一致

这说明当前 DAY14 可以建立为“NSO 控制 + 设备 RESTCONF 补充验证”的结构。

---

## 4. 与老师文档对比后的修正点

老师在 [`记录_1_nso操作(nso-6.1.8).md`](../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/记录_1_nso操作(nso-6.1.8).md) 中演示的是一套通用流程，但本次作业需要结合当前实验网段做修正：

### 4.1 设备 IP 需要改成当前实验地址

老师示例中设备地址写的是 `192.168.1.1`，但当前真实实验环境应为：

- `C8Kv1` = `10.10.1.201`
- SYSLOG Server = `10.10.1.205`

### 4.2 DAY14 不应该只写设备 RESTCONF

如果 DAY14 直接写成对 IOS XE 设备的 RESTCONF PUT/GET，会与 DAY15 的 NSO CI/CD 主线脱节。

更合理的结构应为：

1. NSO 环境确认
2. NSO 纳管设备
3. NSO CLI 修改 SYSLOG
4. NSO 侧验证结果
5. 设备 RESTCONF 侧做交叉验证

### 4.3 trap 级别要按真实状态写清楚

当前真实状态不是 `informational`，而是：

- CLI 视图：`logging trap debugging`
- RESTCONF 视图：`severity = 7`

因此文档中如果继续写 `informational`，就与当前真实环境不一致。

---

## 5. 重做后的 DAY14 作业目标

本次 DAY14 作业重新定义为：

### 任务一：阅读老师资料并确认 NSO 环境已经就绪

目标：确认老师提供的 NSO 安装包、操作文档、运行目录和 WebUI 都能对应起来。

### 任务二：以 NSO 为控制器确认设备纳管状态

目标：确认 `authgroup`、`device`、`NED`、`connect`、`sync-from` 都是通的。

### 任务三：使用 NSO CLI 管理设备 SYSLOG

目标：学会从 NSO 的数据模型视角查看与修改设备配置，而不是直接 SSH 上设备敲命令。

### 任务四：使用设备 RESTCONF 做交叉验证

目标：确认 NSO 下发后的设备配置，从设备北向接口看也是一致的，为后续 DAY15 的自动化与 CI/CD 做铺垫。

---

## 6. 重做后的详细实验记录

## 6.1 任务一：确认老师环境与 NSO 已就绪

### 6.1.1 关键资料定位

老师资料位于：[`../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats`](../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats)

关键安装文件：

```bash
/root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/nso_install_files/nso-6.1.8.linux.x86_64.signed.bin
/root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/nso_install_files/nso-6.1.8.linux.x86_64.installer.bin
```

### 6.1.2 如果从零安装，标准步骤如下

> 这一部分按老师文档整理，用于说明环境来源；当前机器实际上已经安装完成，不需要重复执行。

```bash
cd /root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/nso_install_files
chmod +x nso-6.1.8.linux.x86_64.signed.bin
./nso-6.1.8.linux.x86_64.signed.bin
./nso-6.1.8.linux.x86_64.installer.bin --local-install /root/nso-6.1.8-local
```

初始化运行目录：

```bash
source /root/nso-6.1.8-local/ncsrc
/root/nso-6.1.8-local/bin/ncs-setup --dest /root/nso-6.1.8-run
```

启动：

```bash
cd /root/nso-6.1.8-run
/root/nso-6.1.8-local/bin/ncs
/root/nso-6.1.8-local/bin/ncs --status
```

### 6.1.3 当前实际环境确认

当前机器不是“待安装”状态，而是“已安装并可用”状态。

确认命令：

```bash
source /root/nso-6.1.8-local/ncsrc
/root/nso-6.1.8-local/bin/ncs --status
```

确认结果：

- `status: started`
- Web 模块已加载
- `cisco-ios-cli-3.8` 已可用

### 6.1.4 WebUI 确认

验证命令：

```bash
curl -s http://127.0.0.1:8080/login.html | head -n 5
```

结果：已经返回 HTML 页面头部，证明 WebUI 正常。

---

## 6.2 任务二：确认 NSO 已纳管实验设备

### 6.2.1 查看 authgroup 与 device

```bash
source /root/nso-6.1.8-local/ncsrc
printf 'show running-config devices authgroups | nomore\nshow running-config devices device | de-select config | nomore\n' | /root/nso-6.1.8-local/bin/ncs_cli -C --noaaa
```

实际确认到：

```text
devices authgroups group qytadmin
 default-map remote-name admin
 default-map remote-password ******
!

devices device C8Kv1
 address   10.10.1.201
 ssh host-key-verification none
 authgroup qytadmin
 device-type cli ned-id cisco-ios-cli-3.8
 device-type cli protocol ssh
 state admin-state unlocked
!
```

### 6.2.2 查看已加载 NED

```bash
source /root/nso-6.1.8-local/ncsrc
printf 'show packages package package-version | nomore\n' | /root/nso-6.1.8-local/bin/ncs_cli -C --noaaa
```

实际结果：

```text
packages package cisco-ios-cli-3.8
 package-version 3.8.0.1
```

### 6.2.3 连接设备并同步配置

```bash
source /root/nso-6.1.8-local/ncsrc
printf 'devices device C8Kv1 connect\ndevices sync-from device C8Kv1\n' | /root/nso-6.1.8-local/bin/ncs_cli -C --noaaa
```

实际结果：

```text
result true
info (root) Connected to C8Kv1 - 10.10.1.201:22
sync-result {
    device C8Kv1
    result true
}
```

这一步说明：

- NSO 到设备的 SSH 管理通道正常
- NSO 已成功把设备现网配置同步进自身数据库

---

## 6.3 任务三：从 NSO 视角查看 SYSLOG 配置

### 6.3.1 查看当前 SYSLOG 配置

```bash
source /root/nso-6.1.8-local/ncsrc
printf 'show running-config devices device C8Kv1 config ios:logging | nomore\n' | /root/nso-6.1.8-local/bin/ncs_cli -C --noaaa
```

实际结果：

```text
devices device C8Kv1
 config
  logging host 10.10.1.205
  logging trap debugging
 !
!
```

### 6.3.2 配置含义说明

这表示当前 R1 设备已经通过 NSO 视图体现出如下配置：

- SYSLOG 服务器：`10.10.1.205`
- Trap 级别：`debugging`

即使配置最初可能来自设备或历史实验，只要执行过 [`devices sync-from`](../root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/记录_1_nso操作(nso-6.1.8).md:368)，NSO 就已经拥有该配置的统一视图。

### 6.3.3 如果需要用 NSO CLI 重新下发，可用如下命令

> 这一段作为“重做作业时的标准命令模板”，适合截图提交；若现场已存在相同配置，则提交时可在空闲时段执行一次以生成截图。

```cli
config
devices device C8Kv1 config ios:logging host 10.10.1.205
devices device C8Kv1 config ios:logging trap debugging
top
commit
```

### 6.3.4 提交前建议先做 dry-run

```cli
config
devices device C8Kv1 config ios:logging host 10.10.1.205
devices device C8Kv1 config ios:logging trap debugging
top
commit dry-run outformat native
commit
```

这样可以先看到 NSO 将要下发给设备的原生命令，符合 NSO 自动化控制的思路。

---

## 6.4 任务四：用设备 RESTCONF 做交叉验证

### 6.4.1 获取当前 logging 配置

```bash
curl -sk -u admin:Cisc0123 \
  -H 'Accept: application/yang-data+json' \
  https://10.10.1.201/restconf/data/Cisco-IOS-XE-native:native/logging
```

实际返回：

```json
{
  "Cisco-IOS-XE-native:logging": {
    "trap": {
      "severity": 7
    },
    "host": {
      "ipv4-host-list": [
        {
          "ipv4-host": "10.10.1.205"
        }
      ]
    },
    "hostip": "10.10.1.205"
  }
}
```

### 6.4.2 与 NSO 结果对照

NSO CLI 结果：

```text
logging host 10.10.1.205
logging trap debugging
```

设备 RESTCONF 结果：

```json
{
  "trap": {
    "severity": 7
  },
  "hostip": "10.10.1.205"
}
```

对照关系：

- `debugging` = severity `7`
- `logging host 10.10.1.205` 与 `hostip: 10.10.1.205` 一致

这说明 NSO 视图与设备 RESTCONF 视图一致，实验链路成立。

---

## 7. 本次 DAY14 最终建议提交内容

如果要按“老师路线 + 为 DAY15 铺垫”的方式提交，建议 DAY14 只提交以下核心内容：

### 7.1 提交主线

1. 老师提供的 NSO 安装包与操作文档已阅读
2. NSO 环境已确认运行正常
3. NSO 已成功纳管 `C8Kv1`
4. 已执行 `connect` 与 `sync-from`
5. 已从 NSO 视图确认设备 SYSLOG 配置
6. 已用设备 RESTCONF 验证 NSO 视图与设备真实配置一致

### 7.2 建议截图顺序

1. `ncs --status` 成功截图
2. WebUI 登录页截图
3. `show running-config devices authgroups` 与 `show running-config devices device` 截图
4. `devices device C8Kv1 connect` 成功截图
5. `devices sync-from device C8Kv1` 成功截图
6. `show running-config devices device C8Kv1 config ios:logging` 截图
7. 设备 RESTCONF GET 返回 JSON 截图

---

## 8. 为什么这样改更适合衔接 DAY15

DAY15 是 NSO CI/CD，因此 DAY14 的价值不在于“会不会对路由器发一个 RESTCONF PUT”，而在于先建立以下基础认知：

1. NSO 的安装包、运行目录、NED、设备纳管这些基本组件分别是什么
2. NSO 如何把设备配置纳入自己的统一数据模型
3. 为什么在做自动化交付前需要先 `connect`、`sync-from`
4. 为什么设备真实配置要能被 NSO 与设备接口双向验证

这样到了 DAY15，再做 service、pipeline、CI/CD 时，逻辑才是连贯的。

---

## 9. 当前结论

本次 DAY14 重做后的结论是：

- 老师给的 NSO 安装包与操作记录已经对上
- 当前机器上的 NSO 环境已经搭好，不需要重复从零安装
- NSO 已正常运行，WebUI 正常，IOS NED 已加载
- `C8Kv1` 已被 NSO 纳管，并可成功 `connect` / `sync-from`
- 设备当前 SYSLOG 实际状态为：
  - `logging host 10.10.1.205`
  - `logging trap debugging`
- 设备 RESTCONF 返回与 NSO 视图一致
- 因而 DAY14 应重写为“NSO 环境确认 + 设备纳管 + NSO 视图验证 + RESTCONF 交叉验证”

---

## 10. 文件说明

- 说明文档：[`README.md`](homework/3.NetDevOps/DAY14/README.md)
- RESTCONF 集合：[`NSO_RESTCONF_Collection.json`](homework/3.NetDevOps/DAY14/NSO_RESTCONF_Collection.json)
