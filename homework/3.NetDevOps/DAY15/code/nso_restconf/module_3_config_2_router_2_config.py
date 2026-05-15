import requests
from restconf_0_basic_info import nso_restconf_base_url, auth_info, headers_json
import sys
from module_3_config_2_router_1_get import get_devices_router


def config_devices_router():
    devices_router = get_devices_router()

    for router_info in devices_router:
        if not router_info:
            continue

        router_payload = router_info.get('tailf-ned-cisco-ios:router')
        if not router_payload:
            continue

        config_device_router_url = (
            f"{nso_restconf_base_url}tailf-ncs:devices/device=C8Kv1"
            f"/config/tailf-ned-cisco-ios:router"
        )

        r = requests.put(
            config_device_router_url,
            auth=auth_info,
            json={'tailf-ned-cisco-ios:router': router_payload},
            headers=headers_json,
        )
        if not r.ok:
            try:
                json_result = r.json()
                print(json_result)
            except requests.exceptions.JSONDecodeError:
                pass
            sys.exit(1)
