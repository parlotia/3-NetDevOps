#!/usr/bin/env python3
"""
Bokeh 折线图工具函数
用于绘制接口速率趋势图
"""
import os
from bokeh.plotting import figure, output_file, show
from bokeh.models import DatetimeTickFormatter, HoverTool
from datetime import datetime


def bokeh_line(data_lines, title='接口速率趋势', filename=None):
    """
    绘制多条折线图
    参数：
        data_lines: [[时间列表, 数值列表, 标签], ...]
        title: 图表标题
        filename: 输出文件名（可选）
    """
    if not filename:
        # 自动生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"interface_speed_{timestamp}.html"
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    output_file(output_path, title=title)
    
    # 创建图表
    p = figure(
        title=title,
        x_axis_label='时间',
        y_axis_label='速率 (kbps)',
        x_axis_type='datetime',
        width=1200,
        height=600,
        tools='pan,wheel_zoom,box_zoom,reset,save'
    )
    
    # 添加hover工具
    p.add_tools(HoverTool(
        tooltips=[
            ('时间', '@x{%Y-%m-%d %H:%M:%S}'),
            ('速率', '@y{0.00} kbps'),
        ],
        formatters={'@x': 'datetime'}
    ))
    
    # 绘制每条线
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    for idx, line_data in enumerate(data_lines):
        times, values, label = line_data
        color = colors[idx % len(colors)]
        
        p.line(times, values, legend_label=label, line_width=2, color=color)
        p.scatter(times, values, size=4, color=color, marker='circle')
    
    # 格式化时间轴
    p.xaxis.formatter = DatetimeTickFormatter(
        hours='%H:%M',
        minutes='%H:%M',
        seconds='%H:%M:%S'
    )
    
    p.legend.location = 'top_left'
    p.legend.click_policy = 'hide'
    
    print(f"[*] 生成图表: {output_path}")
    show(p)


if __name__ == '__main__':
    # 测试代码
    from datetime import datetime, timedelta
    import random
    
    # 生成测试数据
    base_time = datetime.now() - timedelta(minutes=10)
    times = [base_time + timedelta(minutes=i) for i in range(11)]
    
    data = [
        [times, [random.randint(100, 1000) for _ in range(11)], '测试线路1'],
        [times, [random.randint(200, 800) for _ in range(11)], '测试线路2'],
    ]
    
    bokeh_line(data, title='测试折线图', filename='test_line.html')
