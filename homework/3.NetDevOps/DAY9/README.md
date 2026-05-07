# DAY9 增强版 ZTP 双层配置分离作业

## 一、作业目标

实现增强版 ZTP（零接触部署）系统，核心改进是**配置数据构建方式的分离**：

- **设备类型通用配置**：同类型设备共享的通用配置（C8000V.template + C8000V.yaml）
- **设备特殊配置**：单台设备（通过序列号唯一标识）独有的配置（序列号.yaml + 接口/OSPF模板）

设备通过 DHCP Option 67 获取 bootfile URL，自动下载 Python 脚本并在 Guestshell 中执行，完成全自动配置下发。

## 二、目录结构

```
DAY9/
├── README.md                          # 本文件
└── code/
    ├── deploy.sh                      # 一键部署脚本
    ├── dhcpd_dir/
    │   └── dnsmasq_ztp.conf           # dnsmasq DHCP + ZTP 配置
    ├── html/
    │   └── day9_ztp.html              # ZTP 服务说明页面
    └── http_dir/
        ├── flask_server.py            # Flask HTTP 服务（/device_config_json）
        ├── ztp_server.py              # 服务端配置生成（Jinja2 + YAML）
        ├── ztp_device.py              # 设备端 ZTP 脚本（guestshell 执行）
        ├── ztp_apache.conf            # Apache 反向代理 + 静态文件配置
        ├── device_type_config/        # 设备类型通用配置
        │   ├── device_type_data/
        │   │   └── C8000V.yaml
        │   └── device_type_template_dir/
        │       └── C8000V.template
        └── specific_device_config/    # 设备特殊配置
            ├── device_config_data/
            │   ├── 94CSC2OWS8U.yaml   # C8Kv1 实际 SN（注意是字母 O）
            │   └── 9HC4DN3P6RT.yaml
            └── device_config_template_dir/
                ├── cisco_ios_interface.template
                └── cisco_ios_ospf.template
```

## 三、核心问题诊断与修复

### 3.1 原始代码问题清单

| 问题 | 影响 | 修复方案 |
|------|------|----------|
| dhcpd.conf 使用 ISC DHCP 语法 | dnsmasq 无法识别，DHCP 服务不工作 | 重写为 dnsmasq 格式 |
| Flask 开发服务器提供 bootfile 下载 | IOS-XE ZTP 下载器不兼容 HTTP/1.0 响应 | 改用 Apache 提供静态文件 |
| `send_file(as_attachment=True)` | Content-Disposition 头可能导致设备解析失败 | Apache 直接提供文件 |
| HTML 示例端口写 8080 | 与 Flask 实际 80 端口不一致 | 修正为默认 80 端口 |
| 默认网关 10.10.1.1 | 网络中不存在该地址，设备无法路由 | 改为 10.10.1.205（服务器自身） |

### 3.2 修复后的服务架构

```
+-------------+     DHCP Option 67      +------------------+
|   C8000V    | <---------------------->|    dnsmasq       |
|  (Router)   |   bootfile URL          |  (UDP 67/68)     |
+------+------+                         +------------------+
       |                                         |
       | HTTP GET /download/ztp_device.py        | DHCP 地址分配
       v                                         v
+------+------------------+              +------------------+
|      Apache (httpd)     |              |   10.10.1.100-199 |
|       Port 80           |              |   gateway:        |
+-------------------------+              |   10.10.1.205     |
|  /download/*  ------>   | 静态文件直供  +------------------+
|  /device_config_json -> | 反向代理
+------------+------------+
             |
             | ProxyPass
             v
+------------+------------+
|    Flask (Port 5000)    |
+-------------------------+
|  /device_config_json    |
|  接收 SN，调用 ztp_server|
|  返回 JSON 配置列表      |
+-------------------------+
```

## 四、做题步骤

### 步骤 1：检查原始代码问题

1. 查看 `dhcpd_dir/dhcpd.conf`，发现使用 ISC DHCP 语法（`subnet`、`option bootfile-name`）
2. 查看 `http_dir/flask_server.py`，发现 `/download` 路由使用 `send_file(as_attachment=True)`，且 `app.run(port=80, debug=True)`
3. 查看 `html/day9_ztp.html`，发现示例 URL 端口为 8080

### 步骤 2：重写 DHCP 配置（dnsmasq 格式）

删除 `dhcpd.conf`，创建 `dnsmasq_ztp.conf`：

```conf
# DHCP 地址池
dhcp-range=10.10.1.100,10.10.1.199,255.255.255.0,12h

# 默认网关（服务器自身 IP）
dhcp-option=option:router,10.10.1.205

# DNS 服务器
dhcp-option=option:dns-server,10.10.1.205

# 域名
dhcp-option=option:domain-name,netdevops.com

# ZTP bootfile（DHCP Option 67）
dhcp-boot=http://10.10.1.205/download/ztp_device.py
```

### 步骤 3：创建 Apache 配置

创建 `http_dir/ztp_apache.conf`：

```apache
<VirtualHost *:80>
    ServerName 10.10.1.205

    # bootfile 静态文件直供
    Alias /download /netdevops/homework/3.NetDevOps/DAY9/code/http_dir
    <Directory /netdevops/homework/3.NetDevOps/DAY9/code/http_dir>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>

    # 动态路由反向代理到 Flask
    ProxyPreserveHost On
    ProxyPass /download !
    ProxyPass /ztp http://127.0.0.1:5000/ztp
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
</VirtualHost>
```

### 步骤 4：修改 Flask 服务

修改 `http_dir/flask_server.py`：

1. 移除 `send_file` 导入和 `/download` 路由
2. 端口改为 5000（由 Apache 反向代理）
3. 添加注释说明 bootfile 已由 Apache 提供

### 步骤 5：修正 HTML 页面

修改 `html/day9_ztp.html`，将示例 URL 中的 `:8080` 去掉。

### 步骤 6：部署服务

执行 `code/deploy.sh` 或手动执行：

```bash
# 1. 部署 dnsmasq 配置
cp code/dhcpd_dir/dnsmasq_ztp.conf /etc/dnsmasq.d/ztp.conf

# 2. 配置 dnsmasq 监听 ens160
sed -i 's/^interface=lo/interface=lo\ninterface=ens160/' /etc/dnsmasq.conf

# 3. 部署 Apache 配置
cp code/http_dir/ztp_apache.conf /etc/httpd/conf.d/ztp_apache.conf

# 4. 开启 IP 转发
sysctl -w net.ipv4.ip_forward=1

# 5. 放行防火墙
firewall-cmd --add-service=dhcp --permanent
firewall-cmd --add-service=http --permanent
firewall-cmd --add-port=5000/tcp --permanent
firewall-cmd --reload

# 6. 启动服务
systemctl restart dnsmasq
systemctl restart httpd

# 7. 启动 Flask（无 debug 模式）
cd code/http_dir
python3 -c "from flask_server import app; app.run(host='0.0.0.0', port=5000, debug=False)"
```

### 步骤 7：验证

1. **DHCP 验证**：重启路由器，确认获取到 `10.10.1.xxx` 地址和 bootfile URL
2. **Bootfile 下载验证**：确认路由器能下载 `http://10.10.1.205/download/ztp_device.py`
3. **动态配置验证**：服务端测试 `curl -X POST -H "Content-Type: application/json" -d '{"device_sn":"<SN>"}' http://10.10.1.205/device_config_json`

## 五、关键踩坑记录

### 5.1 网关地址不存在

**现象**：路由器拿到 IP 后，持续 ARP 查找 `10.10.1.1`，没有任何 HTTP 请求。

**根因**：`dhcp-option=option:router,10.10.1.1` 指向的网关在物理网络中不存在，设备无法完成路由。

**修复**：将网关改为服务器自身 IP `10.10.1.205`，并开启 `net.ipv4.ip_forward=1`。

### 5.2 Flask debug 模式后台运行超时

**现象**：Flask 在后台运行时，`curl` 请求超时无响应。

**根因**：`app.run(debug=True)` 的 reloader 在后台进程环境下工作异常。

**修复**：生产环境使用 `debug=False`。

### 5.3 设备 bootfile 路径兼容性

**现象**：`http://10.10.1.205/download/ztp_device.py` 下载失败。

**根因**：某些 IOS-XE 版本的 ZTP 下载器对带路径的 URL 支持有问题，或 Apache 未正确配置静态文件 Alias。

**修复**：Apache 配置 `Alias /download` 指向 `http_dir` 目录，bootfile 通过 `/download/ztp_device.py` 访问。

## 六、配置数据说明

### 6.1 设备类型通用配置

`device_type_config/device_type_data/C8000V.yaml`：定义通用参数（账号、DNS、NTP、gRPC 订阅等）

`device_type_config/device_type_template_dir/C8000V.template`：Jinja2 模板，渲染通用 CLI 配置

### 6.2 设备特殊配置

`specific_device_config/device_config_data/<SN>.yaml`：定义该设备独有的参数（接口 IP、OSPF 网络等）

`specific_device_config/device_config_template_dir/*.template`：Jinja2 模板，渲染设备特殊配置

### 6.3 动态配置接口

设备端通过 HTTP POST 向 `/device_config_json` 提交 SN 和 IP，服务端返回 JSON 格式的配置列表：

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"device_sn":"94CSC2OWS8U","device_ip":"10.10.1.121"}' \
  http://10.10.1.205/device_config_json
```

## 七、关键踩坑补充

### 7.1 SN 中字母 O 与数字 0 混淆

**现象**：通用配置下发成功，但接口/OSPF 等特殊配置始终缺失，服务端返回仅 39 行。

**根因**：`show version` 提取的 SN 为 `94CSC2OWS8U`（字母 O），但配置文件名写成 `94CSC20WS8U.yaml`（数字 0），`config_generator.py` 找不到匹配文件，跳过特殊配置生成。

**修复**：务必以设备实际上报的 SN 为准创建 YAML 文件，可通过服务端日志或 `repr()` 确认实际字符。

### 7.2 子命令缩进被 `.strip()` 破坏

**现象**：接口 IP、`no shutdown` 等子命令未生效，`cli.configurep()` 报错或跳过后续配置。

**根因**：`config_generator.py` 中将模板渲染后的行用 `.strip()` 处理，去掉了子命令前导空格，导致 `cli.configurep()` 无法识别配置层级。

**修复**：保留模板原始缩进，使用 `device_config_list.append(line)` 而非 `line.strip()`。

### 7.3 Flask Python 缓存未刷新

**现象**：修改 `config_generator.py` 后，设备端仍收到旧版本配置（39 行）。

**根因**：Python 运行时缓存了旧的 `.pyc` 字节码，Flask 进程未重新加载修改后的源码。

**修复**：`find . -name "*.pyc" -delete && find . -name "__pycache__" -type d -exec rm -rf {} +`，然后重启 Flask。
