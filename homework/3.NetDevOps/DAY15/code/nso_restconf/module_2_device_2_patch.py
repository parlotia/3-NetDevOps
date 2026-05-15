import requests
import yaml
import sys
from restconf_0_basic_info import nso_restconf_base_url, auth_info, headers_json

patch_devices_url = nso_restconf_base_url + 'tailf-ncs:devices/device'


def patch_devices():
    with open('device_config_info.yaml') as f:
        config_info = yaml.load(f, Loader=yaml.FullLoader)
        devices_list = config_info['devices']

    final_devices_list = {
        'tailf-ncs:device': [
            {
                'name': device['name'],
                'address': device['ip'],
                'ssh': {
                    'host-key-verification': device['host_key_verification']
                },
                'authgroup': device['authgroup'],
                'device-type': {
                    'cli': {
                        'ned-id': f"{device['ned_id']}:{device['ned_id']}",
                        'protocol': device['protocol']
                    }
                },
                'state': {
                    'admin-state': device['admin_state']
                }
            }
            for device in devices_list
        ]
    }

    r = requests.patch(
        patch_devices_url,
        auth=auth_info,
        json=final_devices_list,
        headers=headers_json,
    )
    if not r.ok:
        try:
            json_result = r.json()
            print(json_result)
        except requests.exceptions.JSONDecodeError:
            pass
        sys.exit(1)

    try:
        return r.json()
    except requests.exceptions.JSONDecodeError:
        return None
