import requests
import base64
import os
import sys

if sys.platform == 'linux':
    server_ip = '10.10.1.205'
elif sys.platform == 'win32':
    server_ip = '10.10.1.110'

server_port = '8080'
base_url = 'http://' + server_ip + ':' + server_port + '/'

exec_cmd_url = base_url + 'cmd'         # 执行命令的 URL
upload_url = base_url + 'upload'        # 上传文件的 URL
download_url = base_url + 'download'    # 下载文件的 URL


def json_rpc_client_exec_cmd(exec_cmd):
    """执行命令的客户端函数"""
    response = requests.post(exec_cmd_url, json=exec_cmd)
    result = response.json()

    if 'error' in result:
        error_msg = base64.b64decode(result['error']).decode()
        return error_msg
    elif 'cmd_result' in result:
        cmd_result = base64.b64decode(result['cmd_result']).decode()
        return cmd_result
    else:
        return result


def json_rpc_client_upload(filename):
    """上传文件的客户端函数"""
    if not os.path.exists(filename):
        return {'error': 'file not exist'}

    with open(filename, 'rb') as f:
        file_data = f.read()

    file_bit = base64.b64encode(file_data).decode()
    upload_data = {
        'upload_filename': filename,
        'file_bit': file_bit
    }

    response = requests.post(upload_url, json=upload_data)
    result = response.json()
    return result


def json_rpc_client_download(filename):
    """下载文件的客户端函数"""
    download_data = {'download_filename': filename}
    response = requests.post(download_url, json=download_data)
    result = response.json()

    if 'error' in result:
        error_msg = base64.b64decode(result['error']).decode()
        print(error_msg)
    elif 'file' in result:
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(result['file']))
        print(f'{filename}下载成功!')
    else:
        print(result)


if __name__ == "__main__":
    # 1. 执行正确命令，应该返回正常结果
    exec_cmd = {'cmd': 'ifconfig'}
    print(json_rpc_client_exec_cmd(exec_cmd))

    # 2. 执行错误命令，应该返回错误输出
    exec_cmd = {'cmd': 'pwd1'}
    print(json_rpc_client_exec_cmd(exec_cmd))

    # 3. JSON 键名写错，应该返回 no cmd in json
    exec_cmd = {'cmd1': 'pwd'}
    print(json_rpc_client_exec_cmd(exec_cmd))

    # 4. 上传存在的文件，应该提示上传成功
    print(json_rpc_client_upload('logo.jpg'))

    # 5. 下载存在的文件，应该提示下载成功
    json_rpc_client_download('logo.jpg')

    # 6. 下载不存在的文件，应该提示文件不存在
    json_rpc_client_download('logo1.jpg')
