# NetDevOps DAY6 — NETCONF 协议实战（ncclient）

## 作业背景

使用 Python `ncclient` 库通过 NETCONF 协议（RFC 6241）与 Cisco IOS-XE 设备交互：获取 CPU 利用率操作数据（`<get>` RPC），以及配置 Syslog trap level 与 host（`<edit-config>` RPC）。同时部署 YangSuite 容器辅助 YANG 模型浏览。

## 实验环境

| 组件 | 版本/地址 |
|------|-----------|
| Linux 服务器 | 10.10.1.205 (Rocky Linux 9.7) |
| C8Kv 路由器 | 10.10.1.200 |
| NETCONF 端口 | TCP 830 |
| Syslog 服务器 | 10.10.1.205 |
| Python | 3.x |
| 关键依赖 | ncclient / lxml |
| YangSuite | Docker Compose 部署 |

## 项目结构

```
DAY6/
├── task2_monitor_cpu.py       # 任务二：NETCONF获取CPU利用率
├── task3_conf_syslog.py       # 任务三：NETCONF配置Syslog
├── docker-compose.yaml        # YangSuite容器编排（YANG模型浏览器）
└── README.md                  # 本文档
```

## 任务说明

### 任务二：使用 NETCONF 获取 CPU 利用率

**YANG 路径：** `Cisco-IOS-XE-process-cpu-oper > cpu-usage > cpu-utilization`

**要求：**
1. 使用 `ncclient.manager.connect()` 建立 NETCONF 会话
2. 构造 subtree filter XML，指定目标 YANG 叶子节点
3. 调用 `m.get(filter=("subtree", filter_xml))` 获取操作数据
4. 使用 `xml.etree.ElementTree` 解析 XML 响应提取 CPU 值
5. 支持三种监控类型：5 秒 / 1 分钟 / 5 分钟

**监控类型映射：**

| 参数 | YANG 叶子节点 | 含义 |
|------|---------------|------|
| `5s` | `five-seconds` | 最近 5 秒 CPU 利用率 |
| `1m` | `one-minute` | 最近 1 分钟 CPU 利用率 |
| `5m` | `five-minutes` | 最近 5 分钟 CPU 利用率 |

**NETCONF Filter XML：**

```xml
<cpu-usage xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-process-cpu-oper">
  <cpu-utilization>
    <five-seconds/>
  </cpu-utilization>
</cpu-usage>
```

**预期输出：**

```
==================================================
NETCONF CPU利用率采集测试
==================================================
[+] 10.10.1.200 CPU利用率(5s): 3%
    -> 5s CPU利用率: 3%

[+] 10.10.1.200 CPU利用率(1m): 2%
    -> 1m CPU利用率: 2%

[+] 10.10.1.200 CPU利用率(5m): 1%
    -> 5m CPU利用率: 1%
```

### 任务三：使用 NETCONF 配置 Syslog

**YANG 路径：** `Cisco-IOS-XE-native > native > logging`

**要求：**
1. 使用 `ncclient.xml_.new_ele` + `lxml.etree.SubElement` 构建 edit-config RPC
2. 配置 `logging > trap > severity`（trap 级别）
3. 配置 `logging > host > ipv4-host-list > ipv4-host`（Syslog 服务器 IP）
4. 使用 `m.dispatch()` 发送 RPC（绕过 YANG 校验问题）
5. 配置后通过 `<get>` RPC 验证配置结果

**Severity 级别映射：**

| 数字 | YANG 枚举值 | 含义 |
|------|-------------|------|
| 0 | emergencies | 紧急 |
| 1 | alerts | 告警 |
| 2 | critical | 严重 |
| 3 | errors | 错误 |
| 4 | warnings | 警告 |
| 5 | notifications | 通知 |
| 6 | informational | 信息 |
| 7 | debugging | 调试 |

**预期输出：**

```
==================================================
NETCONF SYSLOG配置测试
==================================================

--- 配置SYSLOG ---
[+] 10.10.1.200 SYSLOG配置成功:
    trap severity: 7 (debugging)
    syslog server: 10.10.1.205
    配置结果: 成功

--- 验证SYSLOG配置 ---
[+] 10.10.1.200 当前SYSLOG配置:
    trap severity: 7 (debugging)
    syslog server: 10.10.1.205
```

## YangSuite 部署（Docker Compose）

```yaml
services:
  yangsuite:
    image: yangsuite:latest
    ports:
      - "443:443"      # HTTPS Web界面
      - "8443:8443"    # Nginx反向代理
    environment:
      - YS_ADMIN_USER=admin
      - YS_ADMIN_PASS=Cisc0123
  nginx:
    image: nginx:latest
    depends_on: [yangsuite]
  backup:
    image: backup:latest
    depends_on: [yangsuite]
```

## 运行步骤

```bash
# 1. 安装依赖
pip install ncclient lxml

# 2. (可选) 启动YangSuite浏览YANG模型
cd /netdevops/homework/3.NetDevOps/DAY6/
docker compose up -d
# 访问 https://10.10.1.205:8443

# 3. 测试NETCONF获取CPU利用率
python task2_monitor_cpu.py

# 4. 测试NETCONF配置Syslog
python task3_conf_syslog.py

# 5. 在路由器上验证配置
# ssh admin@10.10.1.200
# show logging | include Trap
```

## 知识点

- NETCONF 协议架构（SSH 传输层 / RPC 层 / 操作层 / 内容层）
- `ncclient.manager.connect()` 建立 NETCONF 会话
- `<get>` RPC + subtree filter 获取操作数据
- `<edit-config>` RPC 修改 running 配置
- `dispatch()` 方法绕过 ncclient 内置 YANG 校验
- `lxml.etree.SubElement` 构建带命名空间的 XML 节点
- YANG 模型命名空间（`xmlns`）概念
- Cisco IOS-XE YANG 模型：`Cisco-IOS-XE-process-cpu-oper` / `Cisco-IOS-XE-native`
- YangSuite 容器化部署与 YANG 模型浏览

## 截图清单

1. `task2_monitor_cpu.py` 运行结果（三种监控类型 CPU 利用率）
2. `task3_conf_syslog.py` 运行结果（配置成功 + 验证结果）
3. 路由器 `show logging` 验证 Syslog 配置
4. YangSuite Web 界面（可选）

## 提交文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `task2_monitor_cpu.py` | Python | NETCONF 获取 CPU 利用率（5s/1m/5m） |
| `task3_conf_syslog.py` | Python | NETCONF 配置 Syslog trap + host |
| `docker-compose.yaml` | YAML | YangSuite 容器编排配置 |
| `README.md` | 文档 | 本文档 |
