# NetDevOps DAY14 - NSO 安装与 SYSLOG RESTCONF 测试

## 实验环境

| 设备 | IP | 角色 |
|------|-----|------|
| R1 (C8KV-1) | 10.10.1.201 | RESTCONF SYSLOG 配置目标设备 |
| R2 (C8KV-2) | 10.10.1.202 | 对端实验设备 |
| Linux 服务器 | 10.10.1.205 | SYSLOG 服务器 / 实验辅助节点 |
| NSO Controller | 10.10.1.205:8080 | NSO 控制器 |

**NSO Web 登录信息：** `http://10.10.1.205:8080/login.html`，初始账号密码为 `admin / admin`

**实验设备账号信息：** `admin / Cisc0123`

---

## 任务一：安装 NSO 控制器并确认登录页面

**题目**：按照课堂 CI/CD 实验步骤安装 NSO 控制器，并提供登录页面截图。

### 操作步骤

**1. 准备 NSO 安装包**

在课堂提供的 CI/CD 环境中获取 NSO 安装包，并放到非作业目录下进行安装。

```bash
mkdir -p /root/nso_lab_from_teacher
cd /root/nso_lab_from_teacher/netdevops2023_iac_nso_pyats/nso_install_files
chmod +x nso-6.1.8.linux.x86_64.signed.bin
./nso-6.1.8.linux.x86_64.signed.bin
./nso-6.1.8.linux.x86_64.installer.bin --local-install /root/nso-6.1.8-local
```

**2. 初始化运行目录**

```bash
source /root/nso-6.1.8-local/ncsrc
/root/nso-6.1.8-local/bin/ncs-setup --dest /root/nso-6.1.8-run
```

**3. 启动 NSO**

```bash
cd /root/nso-6.1.8-run
/root/nso-6.1.8-local/bin/ncs
/root/nso-6.1.8-local/bin/ncs --status
```

**4. 检查启动结果**

本次实际检查结果如下：

- NSO 版本：6.1.8
- 状态：started
- 已加载模块：backplane、netconf、cdb、cli、snmp、webui
- Web 登录地址：`http://10.10.1.205:8080/login.html`
- NSO 初始登录账号：`admin / admin`

### 验证结果

本次已在本机完成 NSO 安装与启动验证，`ncs --status` 返回 `started`，说明 NSO 服务运行正常；同时已确认 Web 登录入口为 `http://10.10.1.205:8080/login.html`，初始账号密码为 `admin / admin`。

### 截图要求

提交作业时建议提供以下截图：

1. 安装命令执行截图
2. `ncs --status` 成功截图
3. 浏览器访问 `http://10.10.1.205:8080/login.html` 的登录页面截图
4. 使用 `admin / admin` 登录成功后的 Web 页面截图

---

## 任务二：使用 NSO 控制器 CLI 配置 SYSLOG

**题目**：使用 NSO 控制器的 CLI，配置 SYSLOG（server ip, trap level），提供详细配置步骤。

### 实验参数

| 项目 | 值 |
|------|-----|
| 目标设备 | R1 / C8Kv1 (10.10.1.201) |
| NSO 设备名 | C8Kv1 |
| 设备用户名 | admin |
| 设备密码 | Cisc0123 |
| SYSLOG 服务器 IP | 10.10.1.205 |
| Trap Level | informational |

### 详细操作步骤

**步骤 1：加载 NSO 环境并登录 CLI**

```bash
# 加载 NSO 环境变量
source /root/nso-6.1.8-local/ncsrc

# 登录 NSO CLI（使用 --noaaa 跳过 AAA 认证）
/root/nso-6.1.8-local/bin/ncs_cli -C --noaaa
```

**步骤 2：进入配置模式**

```cli
# 进入全局配置模式
config
```

**步骤 3：配置 SYSLOG 服务器 IP**

```cli
# 配置 SYSLOG 服务器地址
devices device C8Kv1 config ios:logging host 10.10.1.205
```

**步骤 4：配置 SYSLOG Trap Level**

```cli
# 配置 SYSLOG trap 级别为 informational
devices device C8Kv1 config ios:logging trap informational
```

**步骤 5：返回顶层并提交配置**

```cli
# 返回配置树顶层
top

# 提交配置到设备
commit
```

**步骤 6：验证配置**

```cli
# 查看设备 SYSLOG 配置
show running-config devices device C8Kv1 config ios:logging
```

### 实际执行结果

**1. NSO CLI 登录成功：**
```
admin connected from 127.0.0.1 using console on localhost
localhost>
```

**2. SYSLOG 配置命令执行：**
```cli
localhost# config
Entering configuration mode terminal
localhost(config)# devices device C8Kv1 config ios:logging host 10.10.1.205
localhost(config)# devices device C8Kv1 config ios:logging trap informational
localhost(config)# top
localhost(config)# commit
Commit complete.
```

**3. 配置验证结果：**
```cli
localhost# show running-config devices device C8Kv1 config ios:logging
devices device C8Kv1
 config
  logging host 10.10.1.205
  logging trap informational
 !
!
```

### 截图要求

1. NSO CLI 登录成功截图
2. 配置 SYSLOG 服务器 IP 命令截图
3. 配置 SYSLOG trap level 命令截图
4. commit 提交成功截图
5. show running-config 验证结果截图

---

## 任务三：为获取和创建 SYSLOG 配置做 RESTCONF 测试

**题目**：为获取和创建 SYSLOG 配置做 RESTCONF 测试，提供"成功"部分的详细截图。

### RESTCONF 测试参数

| 项目 | 值 |
|------|----|
| 设备 IP | 10.10.1.201 |
| 用户名 | admin |
| 密码 | Cisc0123 |
| SYSLOG Server IP | 10.10.1.205 |
| severity | 7 |

### 方法一：使用 APIFOX 集合测试

**完整操作步骤：**

**步骤 1：启动 APIFOX**

在终端中执行以下命令启动 APIFOX（需要添加 `--no-sandbox` 参数）：

```bash
/root/下载/Apifox-linux-latest/Apifox.AppImage --no-sandbox
```

> 注意：如果提示权限问题，先执行 `chmod +x /root/下载/Apifox-linux-latest/Apifox.AppImage`

**步骤 2：创建新项目**

1. APIFOX 启动后，点击左上角"+"号或"新建项目"
2. 项目名称填写：`DAY14 NSO RESTCONF`
3. 点击"创建"

**步骤 3：导入 RESTCONF 集合**

1. 在项目左侧导航栏，点击"导入"按钮（或右键项目 → 导入数据）
2. 选择"导入文件"
3. 点击"选择文件"，找到并选择：`homework/3.NetDevOps/DAY14/NSO_RESTCONF_Collection.json`
4. 导入方式选择"新建接口"
5. 点击"确定"完成导入

**步骤 4：确认集合变量**

1. 导入后，点击项目名称 → "变量"标签页
2. 确认以下变量值正确：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `nso_ip` | 10.10.1.205 | NSO 控制器 IP |
| `device_ip` | 10.10.1.201 | 目标设备 R1 IP |
| `username` | admin | 设备用户名 |
| `password` | Cisc0123 | 设备密码 |
| `severity` | 7 | SYSLOG 严重级别 |
| `syslog_server_ip` | 10.10.1.205 | SYSLOG 服务器 IP |

**步骤 5：关闭 SSL 验证（重要）**

由于设备使用自签名证书，需要关闭 SSL 验证：

1. 点击左上角"设置"图标（齿轮图标）
2. 选择"请求"设置
3. 找到"SSL 验证"选项，将其关闭
4. 或者在每个请求的"设置"中勾选"忽略 SSL 证书验证"

**步骤 6：执行 PUT 创建 SYSLOG 配置**

1. 在左侧接口列表中，展开 `syslog 创建` 文件夹
2. 点击 `成功` 接口
3. 确认请求参数：
   - **方法**：PUT
   - **URL**：`https://{{device_ip}}/restconf/data/Cisco-IOS-XE-native:native/logging`
   - **Headers**：
     - `Content-Type: application/yang-data+json`
     - `Accept: application/yang-data+json`
   - **认证**：Basic Auth，用户名 `{{username}}`，密码 `{{password}}`
   - **Body**（raw JSON）：
     ```json
     {
       "Cisco-IOS-XE-native:logging": {
         "trap": {
           "severity": {{severity}}
         },
         "hostip": "{{syslog_server_ip}}"
       }
     }
     ```
4. 点击右上角 **"发送"** 按钮
5. **成功标识**：返回状态码 `204 No Content`
6. **截图要求**：
   - 截取请求 URL（显示变量已替换为实际值）
   - 截取 Headers 区域
   - 截取 Body JSON 内容
   - 截取返回状态码 204

**步骤 7：执行 GET 获取 SYSLOG 配置**

1. 在左侧接口列表中，展开 `syslog 获取` 文件夹
2. 点击 `成功` 接口
3. 确认请求参数：
   - **方法**：GET
   - **URL**：`https://{{device_ip}}/restconf/data/Cisco-IOS-XE-native:native/logging`
   - **Headers**：
     - `Accept: application/yang-data+json`
   - **认证**：Basic Auth，用户名 `{{username}}`，密码 `{{password}}`
4. 点击右上角 **"发送"** 按钮
5. **成功标识**：返回状态码 `200 OK`，且返回 JSON 包含以下内容：
   ```json
   {
     "Cisco-IOS-XE-native:logging": {
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
6. **截图要求**：
   - 截取请求 URL
   - 截取 Headers 区域
   - 截取返回状态码 200
   - 截取返回的 JSON 内容（需清晰显示 hostip 字段）

**2. 设置集合变量**

在 APIFOX 集合的 Variables 中设置以下变量：

| 变量名 | 值 |
|--------|-----|
| `device_ip` | 10.10.1.201 |
| `username` | admin |
| `password` | Cisc0123 |
| `severity` | 7 |
| `syslog_server_ip` | 10.10.1.205 |

**3. 执行 PUT syslog 创建JSON → 成功**

- 找到集合中的 `PUT syslog 创建JSON` 请求
- 点击"发送"按钮执行请求
- **成功标识**：返回状态码 `204 No Content`

**请求详情：**
```
PUT https://10.10.1.201/restconf/data/Cisco-IOS-XE-native:native/logging
Content-Type: application/yang-data+json
Accept: application/yang-data+json
Authorization: Basic admin:Cisc0123

{
  "Cisco-IOS-XE-native:logging": {
    "trap": {
      "severity": 7
    },
    "hostip": "10.10.1.205"
  }
}
```

**4. 执行 GET syslog 获取 → 成功**

- 找到集合中的 `GET syslog 获取` 请求
- 点击"发送"按钮执行请求
- **成功标识**：返回状态码 `200 OK`，且返回 JSON 包含 SYSLOG 配置

**请求详情：**
```
GET https://10.10.1.201/restconf/data/Cisco-IOS-XE-native:native/logging
Accept: application/yang-data+json
Authorization: Basic admin:Cisc0123
```

**预期返回：**
```json
{
  "Cisco-IOS-XE-native:logging": {
    "console-config": {
      "console": false
    },
    "console-conf": {
      "console": false
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

### 方法二：使用 Python 脚本测试

**1. 准备脚本**

在 DAY14 目录下创建测试脚本或使用以下命令直接测试：

```bash
# 创建 SYSLOG 配置（PUT）
curl -k -X PUT \
  -u admin:Cisc0123 \
  -H "Content-Type: application/yang-data+json" \
  -H "Accept: application/yang-data+json" \
  -d '{
    "Cisco-IOS-XE-native:logging": {
      "trap": { "severity": 7 },
      "hostip": "10.10.1.205"
    }
  }' \
  https://10.10.1.201/restconf/data/Cisco-IOS-XE-native:native/logging

# 获取 SYSLOG 配置（GET）
curl -k -X GET \
  -u admin:Cisc0123 \
  -H "Accept: application/yang-data+json" \
  https://10.10.1.201/restconf/data/Cisco-IOS-XE-native:native/logging
```

修改以下参数：
```python
DEVICE_IP = '10.10.1.201'  # 原为 10.10.1.200
USERNAME = 'admin'
PASSWORD = 'Cisc0123'
SYSLOG_SERVER_IP = '10.10.1.205'
SEVERITY = 7
```

**2. 执行脚本**

```bash
cd homework/3.NetDevOps/DAY7
python3 task3_conf_syslog.py
```

**3. 预期输出**

```
=== 配置 SYSLOG ===
配置 SYSLOG 成功！状态码: 204

=== 验证 SYSLOG 配置 ===
SYSLOG 配置验证成功！
{
  "Cisco-IOS-XE-native:logging": {
    "hostip": "10.10.1.205",
    ...
  }
}
```

### 截图要求

**"成功"部分详细截图：**

1. **PUT syslog 创建JSON → 成功**
   - 请求 URL 截图
   - Headers 截图（Content-Type, Accept, Authorization）
   - Body JSON 截图
   - 返回状态码 204 截图

2. **GET syslog 获取 → 成功**
   - 请求 URL 截图
   - Headers 截图
   - 返回状态码 200 截图
   - 返回 JSON 内容截图（需包含 hostip、trap 等字段）

---

## 参数来源说明

本次 DAY14 所使用参数与前几天作业保持一致，主要依据如下：

- DAY7 RESTCONF 作业：设备 IP `10.10.1.201`（实际环境），SYSLOG `10.10.1.205`
- DAY8 实验记录：R1 `10.10.1.201`，R2 `10.10.1.202`，Linux `10.10.1.205`
- 用户名密码统一为：`admin / Cisc0123`

---

## 踩坑记录

### 1. 不应把临时解压目录放到作业仓库中

**现象**：前面误把 NSO 解压目录放进工作区，导致 Git 状态变乱。

**修复**：后续统一改为在 `/root` 下安装 NSO，作业目录只保留最终整理结果。

### 2. Java 未安装导致 NED 包加载失败

**现象**：NSO 启动后执行 `packages reload` 报错 "Java VM failed to start"。

**修复**：安装 Java 1.8：`yum install -y java-1.8.0-openjdk`

### 3. NSO packages-in-use 符号链接损坏

**现象**：NSO 启动失败，报错 "./state/packages-in-use: Failed to create symlink"。

**修复**：删除损坏的符号链接后重启：`rm -f state/packages-in-use`，然后重新启动 NSO。

### 4. 设备 IP 地址混淆

**现象**：历史文档中 R1 为 10.10.1.200，但实际环境中 R1 为 10.10.1.201。

**修复**：确认实际设备 IP：R1 (C8Kv1) = 10.10.1.201，R2 (C8Kv2) = 10.10.1.202。

### 5. commit 前需要先 sync-from

**现象**：直接执行 commit 报错，提示设备配置不同步。

**修复**：先执行 `sync-from` 同步设备配置，再执行 `commit` 提交成功。

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `README.md` | DAY14 作业主文档 |
| `NSO_RESTCONF_Collection.json` | APIFOX RESTCONF 测试集合 |

---

## 总结

本次作业已完成以下内容：

1. **NSO 安装与启动**：完成 NSO 6.1.8 本地安装，确认 Web 登录入口 `http://10.10.1.205:8080/login.html`，初始账号密码 `admin / admin`

2. **NSO CLI 配置 SYSLOG**：
   - 创建 authgroup `qytadmin`（remote-name: admin, remote-password: Cisc0123）
   - 创建设备 `C8Kv1`（address: 10.10.1.201, NED: cisco-ios-cli-3.8）
   - 设备连接成功并同步配置
   - 通过 CLI 配置 SYSLOG：`logging host 10.10.1.205`，`logging trap informational`
   - 配置验证成功

3. **RESTCONF 测试文档**：
   - 整理 Day 7 APIFOX 集合使用方法
   - 整理 Day 7 Python 脚本测试方法
   - 提供详细的请求参数、Headers、Body 和预期返回

4. **踩坑记录**：记录 Java 安装、符号链接修复、设备 IP 确认等实际问题

提交作业时，请根据文档中的"截图要求"部分补充实际执行截图。
