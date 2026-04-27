'''
=================================================================
NetDevOps DAY1 任务一
Requests模块使用练习 - 修改HTTP请求头部，模拟PC Chrome浏览器
=================================================================
任务要求:
1. F12获取Chrome头部信息，保存为txt文件 (chrome_headers.txt)
2. 使用自制函数，读取txt文件，转换为字典数据
3. 在requests的请求中调用该头部字典
4. 下载内部系统登录页面的乾颐堂Logo图片
'''

import requests


def headers_txt_to_dict(file_path):
    """
    读取HTTP头部txt文件，转换为字典格式

    参数:
        file_path: 保存HTTP头部的txt文件路径

    返回:
        headers字典，可直接用于requests的请求中
    """
    headers = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过空行和以#开头的注释行
            if not line or line.startswith('#'):
                continue
            # 按第一个冒号分割键值对
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
    return headers


def download_logo(logo_url, headers, save_path='qyt_logo.png'):
    """
    使用自定义HTTP头部下载Logo图片

    参数:
        logo_url: Logo图片的URL地址
        headers: HTTP请求头部字典
        save_path: 图片保存路径
    """
    print(f"[*] 正在请求: {logo_url}")
    print(f"[*] 使用的请求头部:")
    for key, value in headers.items():
        print(f"    {key}: {value}")

    try:
        # 使用自定义headers发起GET请求
        response = requests.get(logo_url, headers=headers, timeout=10)

        # 检查响应状态码
        if response.status_code == 200:
            # 将图片内容写入文件
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"[+] 图片下载成功！保存为: {save_path}")
            print(f"[+] 图片大小: {len(response.content)} 字节")
        else:
            print(f"[-] 请求失败，状态码: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"[-] 请求发生异常: {e}")


if __name__ == '__main__':
    # ======================
    # 配置参数（根据实际情况修改）
    # ======================
    # 1. HTTP头部文件路径
    HEADERS_FILE = 'chrome_headers.txt'

    # 2. Logo图片URL（乾颐堂内部系统登录页面Logo）
    LOGO_URL = 'https://qytsystem.qytang.com/static/images/logo.jpg'

    # 3. 保存文件名
    SAVE_FILE = 'qyt_logo.jpg'

    # 步骤1: 读取HTTP头部文件并转换为字典
    print("=" * 50)
    print("步骤1: 读取Chrome头部文件")
    print("=" * 50)
    chrome_headers = headers_txt_to_dict(HEADERS_FILE)
    print(f"[+] 成功读取 {len(chrome_headers)} 个头部字段\n")

    # 步骤2: 使用自定义头部下载Logo
    print("=" * 50)
    print("步骤2: 使用自定义头部下载Logo")
    print("=" * 50)
    download_logo(LOGO_URL, chrome_headers, SAVE_FILE)
