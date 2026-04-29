# 解决 requests 访问 HTTPS 自签名证书问题

## 问题现象

使用 requests 访问自签名证书的 HTTPS 服务时，会抛出 `SSLCertVerificationError`：

```
requests.exceptions.SSLError: HTTPSConnectionPool(...): 
    [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate
```

## 解决方案

### 方案一：临时跳过验证（开发/测试环境）

在 `requests.post()` 或 `requests.get()` 中传入 `verify=False`：

```python
import requests

response = requests.post(url, json=data, verify=False)
```

> 注意：此方法会跳过所有证书验证，存在中间人攻击风险，仅限内网测试使用。

### 方案二：指定自签名证书文件（推荐）

将服务端的 `.crt` 证书文件拷贝到客户端，通过 `verify` 参数指定：

```python
import requests

response = requests.post(url, json=data, verify='/path/to/fastapi.crt')
```

### 方案三：关闭 urllib3 的警告（配合方案一使用）

使用 `verify=False` 时，requests 会输出 `InsecureRequestWarning` 警告，可通过以下方式关闭：

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

### 方案四：将自签名证书加入系统信任库（生产环境）

将 `fastapi.crt` 复制到系统 CA 证书目录：

```bash
# CentOS/RHEL
cp fastapi.crt /etc/pki/ca-trust/source/anchors/
update-ca-trust extract

# Ubuntu/Debian
cp fastapi.crt /usr/local/share/ca-certificates/
update-ca-certificates
```

## 本项目建议

本项目的 FastAPI 服务使用自签名证书，客户端测试时可直接使用 **方案一（verify=False）** 快速验证功能。若需长期稳定运行，建议采用 **方案二或方案四**。
