#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZTP Flask HTTP Service
ZTP 服务端 HTTP 接口

职责：
  1. 提供 /device_config_json POST 接口，接收设备 SN 和 IP，返回 JSON 配置列表
  2. 提供 /ztp/<type>/<sn>/<ifs> GET 接口（调试用途），返回纯文本配置
  3. 提供首页 /，返回 ZTP 说明页面

部署：由 Apache 反向代理（Port 80）→ Flask（Port 5000）
      静态文件（bootfile）由 Apache 直接提供，不经过 Flask
"""

from flask import Flask, Response, request
import os
import sys
import json

# 将当前目录加入 sys.path，确保能导入同目录的 ztp_server
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir)

# 导入服务端配置生成模块
from ztp_server import get_device_config_list

app = Flask(__name__)


@app.route('/')
def index():
    """首页：返回 ZTP 说明 HTML 页面"""
    html_path = os.path.join(current_dir, '..', 'html', 'day9_ztp.html')
    if os.path.exists(html_path):
        with open(html_path, encoding='utf-8') as f:
            return f.read()
    return '<h1>QYTang ZTP Server</h1>'


@app.route('/ztp/<device_type>/<device_sn>/<path:interfaces>')
def ztp_config(device_type, device_sn, interfaces):
    """
    调试接口：返回纯文本格式的配置（浏览器直接查看）
    URL 示例：/ztp/C8000V/94CSC2OWS8U/GigabitEthernet1,GigabitEthernet2,GigabitEthernet3
    """
    device_if_list = interfaces.split(',')
    config_list = get_device_config_list(device_type, device_if_list, device_sn)
    return Response('\n'.join(config_list), mimetype='text/plain')


@app.route('/device_config_json', methods=['POST'])
def device_config_json():
    """
    核心接口：设备端 ZTP 脚本通过 POST 提交 SN，返回 JSON 格式配置列表

    请求体示例：{"device_sn": "94CSC2OWS8U", "device_ip": "10.10.1.121"}
    响应体示例：{"config": ["hostname C8Kv1", "interface GigabitEthernet1", " ip address ...", ...]}
    """
    client_post_data = request.json
    if client_post_data:
        device_sn = client_post_data.get('device_sn')
        # C8000V 默认接口列表（设备端 guestshell 无法准确获取所有接口名，服务端固定）
        device_if_list = ['GigabitEthernet1', 'GigabitEthernet2', 'GigabitEthernet3']
        config_list = get_device_config_list('C8000V', device_if_list, device_sn)
        # 调试日志：记录收到的 SN 和返回的配置行数，便于排查 SN 匹配问题
        with open('/tmp/ztp_debug.log', 'a') as f:
            f.write('SN received: {!r}, len: {}\n'.format(device_sn, len(config_list)))
        return Response(json.dumps({'config': config_list}), mimetype='application/json')
    return Response(json.dumps({'config': []}), mimetype='application/json')


if __name__ == '__main__':
    # host='0.0.0.0' 允许外部访问，port=5000 与 Apache ProxyPass 对应
    app.run(host='0.0.0.0', port=5000, debug=True)
