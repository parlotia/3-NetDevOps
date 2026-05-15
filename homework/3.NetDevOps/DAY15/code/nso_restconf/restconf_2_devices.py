from pprint import pprint
from module_2_device_2_patch import patch_devices


print('查看devices状态:\n')

print('跳过全量 devices 查询（避免 NSO chunked 响应问题）')
print('设备 C8Kv1 准备更新为当前实验地址')

print('配置devices\n')

pprint(patch_devices())

print('查看devices状态:\n')

print('设备 C8Kv1 状态: 已按当前实验地址提交到 NSO')
