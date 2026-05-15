import requests
from restconf_0_basic_info import nso_restconf_base_url, auth_info, headers_json
import sys
from module_3_config_1_interface_1_get import get_devices_interface


def config_devices_interface():
    devices_interface = get_devices_interface()

    for interface_info in devices_interface:
        if not interface_info:
            continue

        interface_payload = interface_info.get('tailf-ned-cisco-ios:interface')
        if not interface_payload:
            continue

        config_device_interface_url = (
            f"{nso_restconf_base_url}tailf-ncs:devices/device=C8Kv1"
            f"/config/tailf-ned-cisco-ios:interface"
        )

        r = requests.put(
            config_device_interface_url,
            auth=auth_info,
            json={'tailf-ned-cisco-ios:interface': interface_payload},
            headers=headers_json,
        )
        if not r.ok:
            try:
                json_result = r.json()
                print(json_result)
            except requests.exceptions.JSONDecodeError:
                pass
            sys.exit(1)
