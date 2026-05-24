# NetDevOps DAY4 — ASA REST API 配置 Syslog 服务器

## 作业背景

学习使用 Cisco ASA 的 REST API 进行自动化配置。通过 HTTP Basic Auth 获取 Token，然后使用 Token 认证调用 `/api/logging/syslogserver` 接口，为 ASA 防火墙配置 Syslog 日志服务器。

## 实验环境

| 组件 | 版本/说明 |
|------|-----------|
| Python | 3.x |
| 操作系统 | Rocky Linux 9.7 |
| 依赖模块 | `requests` |
| 目标设备 | Cisco ASAv 10.10.1.202（admin/Cisc0123） |
| ASA 配置 | `rest-api agent` 已启用，HTTPS 已开启 |

## 项目结构

```
DAY4/
└── task1_asa_syslog.py    # ASA REST API 配置 Syslog
```

## 任务说明

### 步骤一：获取 ASA REST API Token

```python
url = f"https://{asa_ip}/api/tokenservices"
response = requests.post(url, auth=HTTPBasicAuth(username, password), verify=False)
token = response.headers.get('X-Auth-Token')  # Token 在响应头中
```

### 步骤二：使用 Token 配置 Syslog 服务器

```python
url = f"https://{asa_ip}/api/logging/syslogserver"
headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
payload = {
    "ip": {"kind": "IPv4Address", "value": syslog_server_ip},
    "interface": {"kind": "objectRef#Interface", "name": ifname},
    "port": 514,
    "protocol": "UDP"
}
response = requests.post(url, json=payload, headers=headers, verify=False)
```

### 步骤三：验证配置

使用 GET 请求查询已配置的 Syslog 服务器列表。

**预期输出：**
```
>>> 步骤1: 获取ASA REST API Token
[*] 请求Token: https://10.10.1.202/api/tokenservices
[+] 获取Token成功
[+] Token: 8a7b6c5d4e3f2g1h...

>>> 步骤2: 配置Syslog服务器
[*] 配置Syslog服务器: 10.10.1.205
[*] 出接口: MGMT
[+] Syslog服务器配置成功！状态码: 201

>>> 步骤3: 验证当前Syslog服务器配置
[+] 查询成功
{...syslog server list...}
```

## 运行步骤

```bash
cd /netdevops/homework/3.NetDevOps/DAY4/

python3 task1_asa_syslog.py
```

## 知识点

- ASA REST API 认证流程：Basic Auth → Token → X-Auth-Token
- `requests.post(url, json=payload)` 发送 JSON Body
- HTTP 状态码：`201 Created`、`204 No Content`、`409 Conflict`
- ASA REST API 资源模型：`kind`/`value`/`name`
- Token 认证 vs Basic 认证对比

## 截图清单

1. Token 获取成功输出
2. Syslog 服务器配置成功（201）
3. ASA 上验证 `show logging`（确认 syslog server 已配置）

## 提交文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `task1_asa_syslog.py` | Python | ASA REST API 配置 Syslog |
| `README.md` | 文档 | 本文档 |
