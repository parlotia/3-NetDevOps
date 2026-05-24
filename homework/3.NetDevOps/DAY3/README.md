# NetDevOps DAY3 — FastAPI HTTPS 远程命令执行服务（Docker 部署）

## 作业背景

使用 FastAPI 框架构建一个 HTTPS 远程命令执行 API 服务，通过 Docker Compose 容器化部署，配合自签名 SSL 证书实现加密通信。客户端使用 `requests` 库调用 API 执行系统命令，命令结果采用 Base64 编码传输以支持任意字符。

## 实验环境

| 组件 | 版本/地址 |
|------|-----------|
| Linux 服务器 | 10.10.1.205 (Rocky Linux 9.7) |
| Docker/Compose | Docker Compose v3.9 |
| FastAPI 容器 | fastapi.netdevops.com:443 (HTTPS) |
| Python 基础镜像 | python:3.11-slim |
| Web 框架 | FastAPI + Uvicorn |
| SSL 证书 | 自签名（fastapi.crt / fastapi.key） |
| 客户端 | requests + base64 |

## 项目结构

```
DAY3/
└── code/
    ├── docker-compose.yaml           # Docker Compose 编排文件
    ├── DAY3_client.py                # 客户端：调用API执行远程命令
    ├── __init__.py                   # 包标识文件
    ├── 解决requests证书问题.md       # SSL证书问题解决方案文档
    └── fastapi/
        ├── Dockerfile                # FastAPI 容器构建文件
        ├── main.py                   # FastAPI 服务端：命令执行API
        ├── requirements.txt          # Python 依赖（fastapi/uvicorn/pydantic）
        ├── fastapi.crt               # 自签名 SSL 证书
        ├── fastapi.key               # SSL 私钥
        └── __init__.py               # 包标识文件
```

## 任务说明

### 任务一：FastAPI HTTPS 服务端

**要求：**
1. 使用 FastAPI 框架定义 `POST /cmd` 接口
2. 接收 JSON 请求体 `{"cmd": "ifconfig"}`
3. 使用 `subprocess.Popen` 执行系统命令
4. 命令结果使用 Base64 编码后返回
5. 区分 stdout（成功）和 stderr（错误）分别返回不同模型
6. 使用 Uvicorn 启动，绑定自签名 SSL 证书监听 443 端口

**API 接口定义：**

| 方法 | 路径 | 请求体 | 成功响应 | 失败响应 |
|------|------|--------|----------|----------|
| POST | `/cmd` | `{"cmd": "string"}` | `{"cmd": "...", "cmd_result": "base64..."}` | `{"error": "base64..."}` |

**Pydantic 数据模型：**

```python
class PostCMD(BaseModel):
    cmd: str = Field(title='执行的命令')

class ReturnCMD(BaseModel):
    cmd: str = Field(title='执行的命令')
    cmd_result: str = Field(title='执行的命令返回的结果, 已经被Base64编码')

class ERROR(BaseModel):
    error: str = Field(title='错误消息')
```

### 任务二：Docker Compose 容器化部署

**要求：**
1. 编写 Dockerfile 基于 `python:3.11-slim` 构建 FastAPI 镜像
2. 使用 Docker Compose 编排容器，映射 443 端口
3. Uvicorn 启动参数包含 `--ssl-keyfile` 和 `--ssl-certfile`
4. 容器启用 `privileged: true`（用于执行系统命令）

**docker-compose.yaml：**

```yaml
version: '3.9'
services:
  fastapi:
    build:
      context: fastapi
    privileged: true
    ports:
      - "443:443"
    restart: always
```

### 任务三：requests 客户端调用

**要求：**
1. 使用 `requests.post()` 向 HTTPS API 发送 JSON 命令
2. 接收 Base64 编码的结果并解码显示
3. 处理自签名证书的 SSL 验证问题

**预期输出：**

```
# 执行正确命令
$ python DAY3_client.py
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.18.0.2  netmask 255.255.0.0  broadcast 172.18.255.255
        ...

# 执行错误命令
bash: ipconfig: command not found
```

## SSL 证书问题解决方案

| 方案 | 适用场景 | 代码 |
|------|---------|------|
| `verify=False` | 开发/测试环境 | `requests.post(url, json=data, verify=False)` |
| 指定证书文件 | 推荐方案 | `requests.post(url, json=data, verify='/path/to/fastapi.crt')` |
| 关闭警告 | 配合方案一 | `urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)` |
| 加入系统信任库 | 生产环境 | `cp fastapi.crt /etc/pki/ca-trust/source/anchors/ && update-ca-trust` |

## 运行步骤

```bash
# 1. 进入代码目录
cd /netdevops/homework/3.NetDevOps/DAY3/code/

# 2. 配置hosts解析（客户端需要）
echo "10.10.1.205 fastapi.netdevops.com" >> /etc/hosts

# 3. Docker Compose 构建并启动
docker compose up -d --build

# 4. 验证容器运行
docker compose ps

# 5. 测试API（跳过证书验证）
curl -k -X POST https://fastapi.netdevops.com/cmd \
  -H "Content-Type: application/json" \
  -d '{"cmd": "ifconfig"}'

# 6. 使用Python客户端测试
python DAY3_client.py
```

## 知识点

- FastAPI 框架 + Pydantic 数据模型验证
- Uvicorn ASGI 服务器 + SSL/TLS 加密
- Docker 多阶段构建（Dockerfile）
- Docker Compose 服务编排
- `subprocess.Popen` 系统命令执行（stdout/stderr 分离）
- Base64 编解码（支持任意字符安全传输）
- 自签名证书生成与 HTTPS 配置
- `requests` 库 SSL 证书验证策略

## 截图清单

1. `docker compose up -d` 容器启动成功
2. `curl` 或 Python 客户端执行正确命令的返回结果
3. Python 客户端执行错误命令的返回结果
4. FastAPI 自动文档页面 `https://fastapi.netdevops.com/docs`

## 提交文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `code/fastapi/main.py` | Python | FastAPI 服务端：POST /cmd 命令执行接口 |
| `code/fastapi/Dockerfile` | Docker | 容器构建文件（python:3.11-slim + uvicorn SSL） |
| `code/fastapi/requirements.txt` | 配置 | Python 依赖清单 |
| `code/fastapi/fastapi.crt` | 证书 | 自签名 SSL 证书 |
| `code/fastapi/fastapi.key` | 密钥 | SSL 私钥 |
| `code/docker-compose.yaml` | YAML | Docker Compose 编排配置 |
| `code/DAY3_client.py` | Python | 客户端：requests 调用远程命令 API |
| `code/解决requests证书问题.md` | 文档 | SSL 证书验证问题解决方案 |
| `README.md` | 文档 | 本文档 |
