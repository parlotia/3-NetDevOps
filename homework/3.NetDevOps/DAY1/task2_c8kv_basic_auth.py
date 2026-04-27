'''
=================================================================
NetDevOps DAY1 任务二
使用requests发起https请求，通过基本认证获取路由器信息
=================================================================
任务要求:
1. 确保C8Kv已配置基本认证:
    username admin privilege 15 password 0 Cisc0123
    ip http secure-server
    ip http authentication local
2. 使用requests的HTTPBasicAuth进行认证
3. 请求URL: https://[C8Kv IP]/level/15/exec/-/show/ip/interface/brief/CR
4. 打印返回的show ip interface brief结果
'''

import requests
from requests.auth import HTTPBasicAuth
import urllib3

# 禁用SSL警告（测试环境使用自签名证书时需要）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_interface_brief(device_ip, username, password):
    """
    通过C8Kv的HTTPS REST API获取show ip interface brief结果

    参数:
        device_ip: C8Kv的管理IP地址
        username: 认证用户名
        password: 认证密码

    返回:
        路由器返回的HTML响应文本
    """
    # 构造请求URL
    # /level/15/exec/-/show/ip/interface/brief/CR
    # level/15 表示特权级别15
    # CR 表示Carriage Return（回车执行命令）
    url = f"https://{device_ip}/level/15/exec/-/show/ip/interface/brief/CR"

    print(f"[*] 目标设备: {device_ip}")
    print(f"[*] 请求URL: {url}")
    print(f"[*] 认证用户: {username}")
    print("-" * 50)

    try:
        # 使用HTTPBasicAuth进行基本认证
        # verify=False 表示不验证SSL证书（测试环境）
        response = requests.get(
            url,
            auth=HTTPBasicAuth(username, password),
            verify=False,
            timeout=10
        )

        # 检查响应状态
        if response.status_code == 200:
            print(f"[+] 认证成功！状态码: {response.status_code}")
            return response.text
        elif response.status_code == 401:
            print(f"[-] 认证失败(401): 用户名或密码错误")
            return None
        else:
            print(f"[-] 请求失败，状态码: {response.status_code}")
            return None

    except requests.exceptions.SSLError as e:
        print(f"[-] SSL连接错误: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[-] 连接错误: 无法连接到设备 {device_ip}")
        return None
    except requests.exceptions.Timeout:
        print(f"[-] 请求超时")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[-] 请求异常: {e}")
        return None


def parse_interface_output(html_content):
    """
    简单解析HTML输出，提取接口信息部分

    参数:
        html_content: 路由器返回的HTML内容
    """
    print("\n" + "=" * 50)
    print("路由器原始响应内容:")
    print("=" * 50)
    print(html_content)

    # 尝试提取<PRE>标签内的纯文本输出
    import re
    pre_match = re.search(r'<PRE>(.*?)</PRE>', html_content, re.DOTALL)
    if pre_match:
        print("\n" + "=" * 50)
        print("提取的接口信息:")
        print("=" * 50)
        print(pre_match.group(1))


if __name__ == '__main__':
    # ======================
    # 配置参数（根据实际环境修改）
    # ======================
    # 1. C8Kv的管理IP地址
    C8KV_IP = "10.10.1.200"

    # 2. 认证凭据（与路由器配置一致）
    USERNAME = "admin"
    PASSWORD = "Cisc0123"

    # 执行请求
    print("=" * 50)
    print("C8Kv HTTPS 基本认证测试")
    print("=" * 50)

    result = get_interface_brief(C8KV_IP, USERNAME, PASSWORD)

    if result:
        parse_interface_output(result)
    else:
        print("\n[-] 未能获取到接口信息")
