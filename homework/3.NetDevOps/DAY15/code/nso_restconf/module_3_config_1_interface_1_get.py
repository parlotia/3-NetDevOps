import requests
import yaml
from restconf_0_basic_info import nso_restconf_base_url, auth_info, headers_json
import sys


def get_devices_interface():
    with open('device_config_info.yaml') as f:
        config_info = yaml.load(f, Loader=yaml.FullLoader)
        devices_list = config_info['devices']
        final_interface_result = []
        for device in devices_list:
            get_interface_config_url = (
                f"{nso_restconf_base_url}tailf-ncs:devices/device={device['name']}"
                f"/config/tailf-ned-cisco-ios:interface"
            )
            r = requests.get(
                get_interface_config_url,
                auth=auth_info,
                headers=headers_json,
                stream=False,
            )
            if not r.ok:
                print(final_interface_result)
                try:
                    json_result = r.json()
                    print(json_result)
                except requests.exceptions.JSONDecodeError:
                    pass
                sys.exit(1)

            try:
                json_result = r.json()
                final_interface_result.append(json_result)
            except requests.exceptions.JSONDecodeError:
                final_interface_result.append(None)

    return final_interface_result
