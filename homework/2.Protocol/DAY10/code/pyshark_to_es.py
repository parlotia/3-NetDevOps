#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""Day 10 - 使用 PyShark 解析 PCAP 并写入 Elasticsearch"""

import json
import time
from datetime import timedelta
from datetime import timezone
from pathlib import Path
from urllib import error
from urllib import request

import pyshark


# 设置时区为 UTC
TZUTC_0 = timezone(timedelta(hours=0))
CURRENT_DIR = Path(__file__).resolve().parent
PCAP_FILE = CURRENT_DIR / 'pkt.pcap'
ES_URL = 'http://127.0.0.1:9200'
INDEX_NAME = 'zfs-pyshark-index'


def es_request(method, path, payload=None):
    """通过 Elasticsearch HTTP API 发送请求。"""
    data = None

    if payload is not None:
        data = json.dumps(payload).encode('utf-8')

    req = request.Request(
        f'{ES_URL}{path}',
        data=data,
        headers={'Content-Type': 'application/json'},
        method=method,
    )

    try:
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except error.HTTPError as http_error:
        error_body = http_error.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f'Elasticsearch 请求失败: {http_error.code} {error_body}') from http_error


def get_layer_fields(layer):
    """提取单个协议层的字段字典。"""
    layer_fields = getattr(layer, '_all_fields', {})

    if isinstance(layer_fields, dict):
        return layer_fields

    return {}


def normalize_packet(pkt):
    """把单个数据包整理为适合写入 Elasticsearch 的字典。"""
    pkt_dict = {}

    # 遍历全部协议层, 把字段合并到 pkt_dict
    for layer in pkt.layers:
        fields = get_layer_fields(layer)
        for field_name, field_value in fields.items():
            pkt_dict[field_name] = field_value

    pkt_dict_final = {}

    # 去掉空键, 并把字段名中的 . 替换为 _
    for key, value in pkt_dict.items():
        if key:
            clean_key = key.replace('.', '_')
            pkt_dict_final[clean_key] = value

    pkt_dict_final['sniff_time'] = pkt.sniff_time.astimezone(TZUTC_0).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    pkt_dict_final['highest_layer'] = pkt.highest_layer

    ip_len = pkt_dict_final.get('ip_len')

    if ip_len is not None:
        try:
            pkt_dict_final['ip_len'] = int(ip_len)
        except (TypeError, ValueError):
            pass

    return pkt_dict_final


def process_pcap():
    """读取 PCAP 文件并写入 Elasticsearch。"""
    if not PCAP_FILE.exists():
        print(f'[!] 未找到 PCAP 文件: {PCAP_FILE}')
        print('[!] 请将测试抓包文件放到脚本同级目录下。')
        return

    # 提前创建索引并放宽字段数限制，防止 PyShark 解析出的字段过多导致写入失败
    es_request('PUT', f'/{INDEX_NAME}', payload={
        'settings': {
            'index.mapping.total_fields.limit': 10000
        }
    })

    cap = pyshark.FileCapture(str(PCAP_FILE), keep_packets=False)
    success_count = 0

    try:
        for packet_id, pkt in enumerate(cap, start=1):
            packet_data = normalize_packet(pkt)

            # 调用 HTTP API 把 packet_data 写入 Elasticsearch 索引
            result = es_request('PUT', f'/{INDEX_NAME}/_doc/{packet_id}', packet_data)

            # 写入成功后打印结果, 并统计 success_count
            if result.get('result') in ('created', 'updated'):
                success_count += 1
                print(result.get('result'))
    finally:
        cap.close()

    print(f'[+] 共写入 {success_count} 个数据包到 {INDEX_NAME}')

    # 等待 Elasticsearch 刷新后查询文档总数
    time.sleep(1)
    stats = es_request('GET', f'/{INDEX_NAME}/_count')
    total = stats.get('count', 0)
    print(f'[+] 当前索引文档总数: {total}')


if __name__ == '__main__':
    info = es_request('GET', '/')
    version = info.get('version', {}).get('number', 'unknown')
    print(f'[+] Elasticsearch 版本: {version}')

    process_pcap()
