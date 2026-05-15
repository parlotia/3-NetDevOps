from pprint import pprint
from module_logging import get_devices_logging, config_devices_logging
from module_2_device_3_sync import sync_devices


print('查看设备Logging配置:\n')

pprint(get_devices_logging())

print('配置Logging\n')

pprint(config_devices_logging())

print('同步devices:\n')

pprint(sync_devices())

print('查看设备Router配置:\n')

pprint(get_devices_logging())
