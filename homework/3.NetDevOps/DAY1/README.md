# NetDevOps DAY1 — Requests 模块：自定义请求头 + HTTPS Basic Auth

## 作业背景

学习使用 `requests` 库发起 HTTP/HTTPS 请求：任务一练习修改请求头部模拟 Chrome 浏览器下载文件；任务二使用 `HTTPBasicAuth` 通过 C8Kv 路由器的 HTTPS REST 接口获取 `show ip interface brief` 信息。

## 实验环境

| 组件 | 版本/说明 |
|------|-----------|
| Python | 3.x |
| 操作系统 | Rocky Linux 9.7 |
| 依赖模块 | `requests` |
| 目标设备 | Cisco C8Kv 10.10.1.200（admin/Cisc0123） |
| 路由器配置 | `ip http secure-server` + `ip http authentication local` |

## 项目结构

```
DAY1/
├── task1_download_logo.py     # 任务一：自定义 Headers 下载图片
├── task2_c8kv_basic_auth.py   # 任务二：HTTPS Basic Auth 获取接口信息
├── chrome_headers.txt          # Chrome F12 导出的请求头
└── qyt_logo.jpg                # 下载的 Logo 图片
```

## 任务说明

### 任务一：修改 HTTP 请求头下载 Logo

1. 使用 Chrome F12 开发者工具获取请求头，保存为 `chrome_headers.txt`
2. 编写函数读取 txt 文件转换为字典
3. 使用自定义 headers 发起 GET 请求下载图片

**预期输出：**
```
步骤1: 读取Chrome头部文件
[+] 成功读取 12 个头部字段

步骤2: 使用自定义头部下载Logo
[*] 正在请求: https://qytsystem.qytang.com/static/images/logo.jpg
[+] 图片下载成功！保存为: qyt_logo.jpg
[+] 图片大小: 15234 字节
```

### 任务二：HTTPS Basic Auth 获取路由器信息

```python
url = f"https://{device_ip}/level/15/exec/-/show/ip/interface/brief/CR"
response = requests.get(url, auth=HTTPBasicAuth(username, password), verify=False)
```

**预期输出：**
```
[+] 认证成功！状态码: 200

提取的接口信息:
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet1       10.10.1.200     YES NVRAM  up                    up
GigabitEthernet2       172.16.1.12     YES manual up                    up
Loopback13             13.13.13.13     YES manual up                    up
```

## 运行步骤

```bash
cd /netdevops/homework/3.NetDevOps/DAY1/

# 任务一：下载 Logo
python3 task1_download_logo.py

# 任务二：Basic Auth 获取接口信息
python3 task2_c8kv_basic_auth.py
```

## 知识点

- `requests.get(url, headers=...)` 自定义请求头
- 文件读取 + 字符串分割转字典
- `response.content`（二进制）vs `response.text`（文本）
- `HTTPBasicAuth(user, pass)` HTTP 基本认证
- `verify=False` 跳过 SSL 证书验证
- `urllib3.disable_warnings()` 禁用 SSL 警告
- Cisco IOS-XE HTTP API URL 格式

## 截图清单

1. `task1_download_logo.py` 运行结果（成功下载图片）
2. `task2_c8kv_basic_auth.py` 运行结果（接口信息输出）

## 提交文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `task1_download_logo.py` | Python | 自定义 Headers 下载图片 |
| `task2_c8kv_basic_auth.py` | Python | HTTPS Basic Auth 获取接口信息 |
| `chrome_headers.txt` | 文本 | Chrome 请求头导出 |
| `README.md` | 文档 | 本文档 |
