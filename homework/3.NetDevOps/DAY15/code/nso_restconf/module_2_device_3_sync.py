import requests
import yaml
from restconf_0_basic_info import nso_restconf_base_url, auth_info, headers_json
import sys


def sync_devices():
    with open(f'device_config_info.yaml') as f:
        config_info = yaml.load(f, Loader=yaml.FullLoader)
        devices_list = config_info['devices']
        final_sync_result = []
        for device in devices_list:
            sync_device_url = f"{nso_restconf_base_url}tailf-ncs:devices/device={device['name']}/sync-from"
            r = requests.post(sync_device_url,
                              auth=auth_info,
                              headers=headers_json)

            if not r.ok:
                print(final_sync_result)
                try:
                    json_result = r.json()
                    print(json_result)
                except requests.exceptions.JSONDecodeError:
                    pass
                sys.exit(1)

            try:
                json_result = r.json()
                final_sync_result.append(json_result)
            except requests.exceptions.JSONDecodeError:
                final_sync_result.append(None)

    return final_sync_result
