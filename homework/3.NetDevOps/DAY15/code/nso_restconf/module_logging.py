import sys
import yaml
import requests
from restconf_0_basic_info import nso_restconf_base_url, auth_info, headers_json


def get_logging_config(device_name):
    url = (
        f"{nso_restconf_base_url}tailf-ncs:devices/device={device_name}"
        f"/config/tailf-ned-cisco-ios:logging"
    )
    response = requests.get(url, auth=auth_info, headers=headers_json)
    if response.status_code == 404:
        return {}
    if not response.ok:
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print(response.text)
        sys.exit(1)
    return response.json()


def push_logging_config(device_name, logging_payload):
    url = (
        f"{nso_restconf_base_url}tailf-ncs:devices/device={device_name}"
        f"/config/tailf-ned-cisco-ios:logging"
    )
    payload = {'tailf-ned-cisco-ios:logging': logging_payload}
    response = requests.put(url, auth=auth_info, json=payload, headers=headers_json)
    if not response.ok:
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print(response.text)
        sys.exit(1)


def load_device_logging_info():
    with open('device_config_info.yaml') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data.get('devices', [])
