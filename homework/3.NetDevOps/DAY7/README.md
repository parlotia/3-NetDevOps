# NetDevOps DAY7 — RESTCONF 协议实战（requests HTTPS）

## 作业背景

使用 Python `requests` 库通过 RESTCONF 协议（RFC 8040）与 Cisco IOS-XE 设备交互：以 HTTPS GET 获取 CPU 利用率操作数据，以 HTTPS PUT 配置 Syslog trap level 与 host。对比 DAY6 的 NETCONF 方式，体会 RESTful 风格的简洁性。

## 实验环境

| 组件 | 版本/地址 |
|------|-----------|
| Linux 服务器 | 10.10.1.205 (Rocky Linux 9.7) |
| C8Kv 路由器 | 10.10.1.200 |
| RESTCONF 端口 | TCP 443 (HTTPS) |
| Syslog 服务器 | 10.10.1.205 |
| Python | 3.x |
| 关键依赖 | requests / urllib3 |
| 认证方式 | HTTP Basic Auth |

## 项目结构

```
DAY7/
├── task2_monitor_cpu.py                    # 任务二：RESTCONF获取CPU利用率
├── task3_conf_syslog.py                    # 任务三：RESTCONF配置Syslog
├── NetDevOps_RESTCONF_Collection.json      # Postman/Apifox 接口集合
└── README.md                               # 本文档
```

## 任务说明

### 任务二：使用 RESTCONF 获取 CPU 利用率

**RESTCONF URL：**
```
GET https://{device_ip}/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization/{leaf}
```

**要求：**
1. 使用 `requests.get()` 发送 HTTPS GET 请求
2. 设置 `Accept: application/yang-data+json` 头
3. 使用 HTTP Basic Auth 认证（`auth=(username, password)`）
4. 禁用 SSL 证书验证（`verify=False`）
5. 从 JSON 响应中提取 CPU 利用率值
6. 支持三种监控类型：5 秒 / 1 分钟 / 5 分钟

**监控类型与 URL 路径映射：**

| 参数 | URL 路径片段 | JSON Key |
|------|-------------|----------|
| `5s` | `five-seconds` | `Cisco-IOS-XE-process-cpu-oper:five-seconds` |
| `1m` | `one-minute` | `Cisco-IOS-XE-process-cpu-oper:one-minute` |
| `5m` | `five-minutes` | `Cisco-IOS-XE-process-cpu-oper:five-minutes` |

**预期输出：**

```
==================================================
RESTCONF CPU利用率采集测试
==================================================
[+] 10.10.1.200 CPU利用率(5s): 2%
    -> 5s CPU利用率: 2%

[+] 10.10.1.200 CPU利用率(1m): 1%
    -> 1m CPU利用率: 1%

[+] 10.10.1.200 CPU利用率(5m): 1%
    -> 5m CPU利用率: 1%
```

**JSON 响应示例：**

```json
{
  "Cisco-IOS-XE-process-cpu-oper:five-seconds": 2
}
```

### 任务三：使用 RESTCONF 配置 Syslog

**RESTCONF URL：**
```
PUT https://{device_ip}/restconf/data/Cisco-IOS-XE-native:native/logging
```

**要求：**
1. 使用 `requests.put()` 发送 HTTPS PUT 请求
2. 设置 `Content-Type: application/yang-data+json` 头
3. 构造 JSON Payload 包含 trap severity 和 hostip
4. 成功时返回 HTTP 204 No Content
5. 配置后通过 GET 请求验证配置结果

**请求 Payload：**

```json
{
  "Cisco-IOS-XE-native:logging": {
    "trap": {
      "severity": 7
    },
    "hostip": "10.10.1.205"
  }
}
```

**预期输出：**

```
==================================================
RESTCONF SYSLOG配置测试
==================================================

--- 配置SYSLOG ---
[+] 10.10.1.200 SYSLOG配置成功 (204 No Content):
    trap severity: 7
    syslog server: 10.10.1.205
    配置结果: 成功

--- 验证SYSLOG配置 ---
[+] 10.10.1.200 当前SYSLOG配置:
    trap severity: 7
    syslog server: 10.10.1.205
```

## NETCONF vs RESTCONF 对比

| 特性 | DAY6 NETCONF | DAY7 RESTCONF |
|------|-------------|---------------|
| 传输协议 | SSH (TCP 830) | HTTPS (TCP 443) |
| 数据格式 | XML | JSON |
| Python 库 | ncclient | requests |
| 认证方式 | SSH 用户名/密码 | HTTP Basic Auth |
| 读取操作 | `<get>` RPC + filter | GET + URL 路径 |
| 写入操作 | `<edit-config>` RPC | PUT/PATCH + JSON Body |
| 复杂度 | 需要构建 XML 节点 | RESTful 风格，更简洁 |

## 运行步骤

```bash
# 1. 安装依赖
pip install requests urllib3

# 2. 确认设备RESTCONF已启用
# 路由器配置: restconf / ip http secure-server

# 3. 测试RESTCONF获取CPU利用率
cd /netdevops/homework/3.NetDevOps/DAY7/
python task2_monitor_cpu.py

# 4. 测试RESTCONF配置Syslog
python task3_conf_syslog.py

# 5. (可选) 使用Postman/Apifox导入接口集合测试
# 导入文件: NetDevOps_RESTCONF_Collection.json

# 6. 在路由器上验证配置
# ssh admin@10.10.1.200
# show logging | include Trap
```

## 知识点

- RESTCONF 协议架构（基于 HTTPS 的 YANG 数据访问）
- RESTCONF URL 路径结构：`/restconf/data/{module}:{container}/{leaf}`
- `application/yang-data+json` MIME 类型
- HTTP Basic Auth 认证
- HTTPS 自签名证书处理（`verify=False` + `urllib3.disable_warnings()`）
- RESTful 语义：GET 读取 / PUT 替换 / PATCH 部分更新
- HTTP 204 No Content 成功响应
- NETCONF 与 RESTCONF 的对比与选型
- Postman/Apifox 接口集合导入与调试

## 截图清单

1. `task2_monitor_cpu.py` 运行结果（三种监控类型 CPU 利用率）
2. `task3_conf_syslog.py` 运行结果（配置成功 + 验证结果）
3. Postman/Apifox 中 RESTCONF 接口调试截图
4. 路由器 `show logging` 验证 Syslog 配置

## 提交文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `task2_monitor_cpu.py` | Python | RESTCONF 获取 CPU 利用率（GET + JSON） |
| `task3_conf_syslog.py` | Python | RESTCONF 配置 Syslog（PUT + JSON） |
| `NetDevOps_RESTCONF_Collection.json` | JSON | Postman/Apifox 接口调试集合 |
| `README.md` | 文档 | 本文档 |
