import sys
import requests
from restconf_0_basic_info import nso_restconf_base_url, auth_info, headers_json


def sync_from_device(device_name):
    url = (
        f"{nso_restconf_base_url}tailf-ncs:devices/device={device_name}/"
        f"sync-from"
    )
    response = requests.post(url, auth=auth_info, headers=headers_json)
    if not response.ok:
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print(response.text)
        sys.exit(1)
    return response.json()
