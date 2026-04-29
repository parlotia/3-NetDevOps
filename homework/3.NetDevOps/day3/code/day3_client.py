#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import requests
import base64


server_ip = 'fastapi.netdevops.com'
base_url = f'https://{server_ip}/'
exec_cmd_url = base_url + 'cmd'         # 执行命令的URL


# 执行命令的函数
def json_rpc_client_exec_cmd(obj):
    # 向执行命令的url"exec_cmd_url"发起POST请求, 并且把返回的JSON, 转换为Python字典
    return_json = requests.post(exec_cmd_url, json=obj).json()
    # 如果有键"cmd_result", 就表示命令执行成功, 就提取其值然后打印命令执行结果
    if return_json.get('cmd_result'):
        # 由于命令执行结果可能包含任意字符,所以服务器采用了base64编码,客户端需要进行base64解码
        return base64.b64decode(return_json.get('cmd_result')).decode('utf-8')
    # 如果没有键"cmd_result", 就表示命令执行失败, 就提取其值然后打印错误信息
    else:
        # 由于命令执行结果可能包含任意字符,所以服务器采用了base64编码,客户端需要进行base64解码
        return base64.b64decode(return_json.get('error')).decode('utf-8')


if __name__ == "__main__":
    # 1. 执行正确命令，应该返回正常结果
    exec_cmd = {'cmd': 'ifconfig'}
    print(json_rpc_client_exec_cmd(exec_cmd))

    # 2. 执行错误命令，应该返回错误输出
    exec_cmd = {'cmd': 'ipconfig'}
    print(json_rpc_client_exec_cmd(exec_cmd))
