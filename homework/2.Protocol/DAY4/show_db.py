import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# 【关键】把当前脚本所在目录加入Python搜索路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from create_db import RouterMonitor, Session
from bokeh_line import bokeh_line


def read_data_from_db(hours=1):
    """
    从数据库读取最近N小时的监控数据
    参数：hours: 读取最近多少小时的数据
    返回：(cpu_data, mem_data)，格式：{device_ip: [(time1, value1), ...]}
    """
    # 计算时间阈值：从现在往前推hours小时
    time_threshold = datetime.now() - timedelta(hours=hours)

    # 初始化数据字典
    cpu_data = defaultdict(list)
    mem_data = defaultdict(list)

    # 打开数据库会话
    with Session() as session:
        # 查询最近N小时的记录，按时间升序排列
        records = (session.query(RouterMonitor)
                   .filter(RouterMonitor.record_datetime >= time_threshold)
                   .order_by(RouterMonitor.record_datetime.asc())
                   .all())

        # 遍历记录，按设备IP分组
        for record in records:
            # CPU数据直接使用
            cpu_data[record.device_ip].append(
                (record.record_datetime, record.cpu_useage_percent)
            )

            # 计算内存利用率：已用/总内存*100
            total_mem = record.mem_use + record.mem_free
            if total_mem > 0:
                mem_percent = round((record.mem_use / total_mem) * 100, 2)
            else:
                mem_percent = 0

            mem_data[record.device_ip].append(
                (record.record_datetime, mem_percent)
            )

    return cpu_data, mem_data


def prepare_lines_data(data_dict):
    """
    将数据字典转换为bokeh_line函数需要的格式
    输入：{device_ip: [(time1, value1), ...]}
    输出：[[time_list, value_list, line_name], ...]
    """
    lines_data = []
    for device_ip, records in data_dict.items():
        if not records:
            continue
        # 分离时间和值
        time_list = [r[0] for r in records]
        value_list = [r[1] for r in records]
        lines_data.append([time_list, value_list, device_ip])
        print(f"[*] 设备{device_ip}: 读取 {len(records)} 条记录")
    return lines_data


if __name__ == '__main__':
    # 1. 读取最近1小时的数据
    cpu_data, mem_data = read_data_from_db(hours=1)

    # 2. 绘制CPU利用率趋势图（支持两台设备对比）
    if cpu_data:
        cpu_lines = prepare_lines_data(cpu_data)
        bokeh_line(cpu_lines, title='CPU利用率趋势')

    # 3. 绘制内存利用率趋势图（支持两台设备对比）
    if mem_data:
        mem_lines = prepare_lines_data(mem_data)
        bokeh_line(mem_lines, title='内存利用率趋势')