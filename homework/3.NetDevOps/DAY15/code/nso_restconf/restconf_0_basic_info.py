from requests.auth import HTTPBasicAuth
import os

nso_username = os.getenv('nso_username')
nso_password = os.getenv('nso_password')
nso_restconf_base_url = os.getenv('nso_restconf_base_url')

auth_info = HTTPBasicAuth(nso_username, nso_password)
headers_json = {
    'Accept': 'application/yang-data+json',
    'Content-Type': 'application/yang-data+json'
}
