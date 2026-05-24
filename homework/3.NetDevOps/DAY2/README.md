# NetDevOps DAY2 — Flask JSON-RPC 远程命令执行与文件传输

## 作业背景

使用 Flask 框架搭建 JSON-RPC 风格的 HTTP 服务端，实现三个 API 接口：远程命令执行（`/cmd`）、文件上传（`/upload`）、文件下载（`/download`）。数据传输使用 Base64 编码，客户端通过 `requests.post()` 调用。

## 实验环境

| 组件 | 版本/说明 |
|------|-----------|
| Python | 3.x |
| 操作系统 | Rocky Linux 9.7 |
| 依赖模块 | `flask`、`requests` |
| 服务端口 | 8080 |

## 项目结构

```
DAY2/
├── json_rpc_server.py    # Flask 服务端（cmd/upload/download）
├── json_rpc_client.py    # requests 客户端
├── uploads/              # 上传文件存储目录（自动创建）
└── logo.jpg              # 测试上传用文件
```

## 任务说明

### API 接口设计

| 接口 | 方法 | 功能 | 请求体 |
|------|------|------|--------|
| `/cmd` | POST | 执行系统命令 | `{"cmd": "ifconfig"}` |
| `/upload` | POST | 上传文件 | `{"upload_filename": "x.jpg", "file_bit": "<base64>"}` |
| `/download` | POST | 下载文件 | `{"download_filename": "x.jpg"}` |

### 数据编码方式

所有二进制数据（文件内容、命令输出、错误信息）均使用 **Base64** 编码传输：
```python
# 编码
base64.b64encode(data.encode()).decode()
# 解码
base64.b64decode(result['cmd_result']).decode()
```

### 客户端测试场景

```python
# 1. 执行正确命令
json_rpc_client_exec_cmd({'cmd': 'ifconfig'})

# 2. 执行错误命令
json_rpc_client_exec_cmd({'cmd': 'pwd1'})

# 3. 上传文件
json_rpc_client_upload('logo.jpg')

# 4. 下载存在的文件
json_rpc_client_download('logo.jpg')

# 5. 下载不存在的文件
json_rpc_client_download('logo1.jpg')
```

## 运行步骤

```bash
cd /netdevops/homework/3.NetDevOps/DAY2/

# 安装依赖
pip install flask requests

# 终端1：启动服务端
python3 json_rpc_server.py

# 终端2：运行客户端测试
python3 json_rpc_client.py
```

## 知识点

- Flask `@app.route()` 路由装饰器
- `request.json` 获取 POST JSON 数据
- `subprocess.run(shell=True, capture_output=True)` 执行系统命令
- `base64.b64encode()`/`b64decode()` 二进制编码
- `requests.post(url, json=data)` 发送 JSON POST 请求
- 文件二进制读写：`open('rb')`/`open('wb')`

## 截图清单

1. 服务端启动输出
2. 客户端执行命令成功（ifconfig 输出）
3. 客户端文件上传/下载成功
4. 错误处理场景（错误命令、不存在文件）

## 提交文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `json_rpc_server.py` | Python | Flask JSON-RPC 服务端 |
| `json_rpc_client.py` | Python | requests 客户端 |
| `README.md` | 文档 | 本文档 |
