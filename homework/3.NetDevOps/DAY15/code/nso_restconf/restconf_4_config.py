from pprint import pprint
from module_logging import load_device_logging_info, get_logging_config, push_logging_config
from module_sync import sync_from_device


logging_result_before = []
sync_result = []
logging_result_after = []

for device in load_device_logging_info():
    device_name = device['name']
    logging_payload = device['logging']

    logging_result_before.append(get_logging_config(device_name))
    push_logging_config(device_name, logging_payload)
    sync_result.append(sync_from_device(device_name))
    logging_result_after.append(get_logging_config(device_name))

print('查看设备Logging配置:\n')
pprint(logging_result_before)

print('配置Logging\n')
pprint(None)

print('同步devices:\n')
pprint(sync_result)

print('查看设备Logging配置:\n')
pprint(logging_result_after)
