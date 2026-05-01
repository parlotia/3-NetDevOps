from bokeh.plotting import figure, output_file, save
from bokeh.models import HoverTool, DatetimeTickFormatter, ColumnDataSource
import os
from pathlib import Path

# 改回原始路径：outputs 在 code 根目录下生成
OUTPUTS_DIR = Path(__file__).resolve().parent.parent / 'outputs'

# 折线颜色列表
LINE_COLORS = ['red', 'blue', 'green', 'orange', 'purple', 'brown']


def bokeh_line(lines_data, title='利用率趋势', y_label='利用率 (%)', save_name=None):
    """
    绘制多条折线的时间序列图
    参数：
        lines_data: 多条线的数据，格式：[[time_list, value_list, line_name], ...]
        title: 图表标题
        y_label: Y轴标签
        save_name: 保存文件名
    """
    # 创建图表
    p = figure(height=400, width=700, title=title,
               x_axis_type="datetime", x_axis_label='时间', y_axis_label=y_label,
               y_range=(0, 100))

    # 循环绘制每条折线
    for i, (time_list, value_list, line_name) in enumerate(lines_data):
        color = LINE_COLORS[i % len(LINE_COLORS)]
        source = ColumnDataSource(data={
            'time': time_list,
            'time_str': [t.strftime("%Y-%m-%d %H:%M:%S") for t in time_list],
            'value': value_list
        })
        # 绘制折线
        p.line(x='time', y='value', source=source, line_width=2,
               color=color, legend_label=line_name)
        # 绘制散点（Bokeh 3.4+ 使用 scatter 并指定 marker）
        p.scatter(x='time', y='value', source=source, size=5,
               marker='circle', color=color, alpha=0.5)

    # 添加悬停提示（垂直模式）
    hover = HoverTool(tooltips=[("时间", "@time_str"), ("值", "@value%")], mode='vline')
    p.add_tools(hover)

    # 美化X轴时间格式
    p.xaxis.formatter = DatetimeTickFormatter(
        minutes="%H:%M",
        hours="%H:%M",
        days="%m-%d"
    )
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"  # 点击图例可隐藏线条

    # 确保outputs目录存在
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    output_filename = save_name if save_name else str(OUTPUTS_DIR / f"{title}.html")
    output_file(output_filename, title=title)
    save(p)
    print(f"[*] Bokeh 折线图已生成: {output_filename}")

# 任务二：测试代码
if __name__ == '__main__':
    import random
    from datetime import datetime, timedelta

    # 生成时间序列
    now = datetime.now()
    time_list = [now - timedelta(minutes=i*5) for i in range(12)][::-1]

    # 生成两台设备的随机CPU数据
    value_list1 = [random.randint(20, 80) for _ in range(12)]
    value_list2 = [random.randint(30, 90) for _ in range(12)]

    # 准备数据格式
    lines_data = [
        [time_list, value_list1, 'Router1_CPU'],
        [time_list, value_list2, 'Router2_CPU']
    ]

    # 生成测试折线图
    bokeh_line(lines_data, title='CPU利用率趋势')