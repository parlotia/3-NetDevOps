import requests
import sys
from restconf_0_basic_info import nso_restconf_base_url, auth_info, headers_json

get_authgroup_url = nso_restconf_base_url + 'tailf-ncs:devices/authgroups'


def get_authgroup():
    r = requests.get(get_authgroup_url,
                     auth=auth_info,
                     headers=headers_json)

    if not r.ok:
        try:
            json_result = r.json()
            print(json_result)
        except requests.exceptions.JSONDecodeError:
            pass
        sys.exit(1)

    try:
        json_result = r.json()
        return json_result
    except requests.exceptions.JSONDecodeError:
        return None
