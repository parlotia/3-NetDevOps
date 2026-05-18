from bokeh.plotting import figure, output_file, save
from bokeh.models import HoverTool, DatetimeTickFormatter, ColumnDataSource
import os
from pathlib import Path

# 改回原始路径：outputs 在 code 根目录下生成
OUTPUTS_DIR = Path(__file__).resolve().parent.parent / 'outputs'


def bokeh_bar(time_list, value_list, line_name,
              title='利用率柱状图', y_label='利用率 (%)', save_name=None):
    """
    绘制时间序列柱状图
    参数：
        time_list: 时间列表（datetime对象）
        value_list: 对应的值列表
        line_name: 图例名称
        title: 图表标题
        y_label: Y轴标签
        save_name: 保存文件名，None则自动生成
    """
    # 自动计算柱宽：取相邻时间间隔的60%，单位毫秒
    if len(time_list) > 1:
        delta_ms = (time_list[1] - time_list[0]).total_seconds() * 1000 * 0.6
    else:
        delta_ms = 30000

    # 创建数据源
    source = ColumnDataSource(data={
        'time': time_list,
        'time_str': [t.strftime("%Y-%m-%d %H:%M:%S") for t in time_list],
        'value': value_list
    })

    # 创建图表
    p = figure(height=400, width=700, title=f"{title} - {line_name}",
               x_axis_type="datetime", x_axis_label='时间', y_axis_label=y_label,
               y_range=(0, 100))

    # 绘制柱状图
    p.vbar(x='time', top='value', source=source, width=delta_ms,
           color="#e84d60", alpha=0.8, legend_label=line_name)

    # 添加悬停提示
    hover = HoverTool(tooltips=[("时间", "@time_str"), ("值", "@value%")])
    p.add_tools(hover)

    # 美化X轴时间格式
    p.xaxis.formatter = DatetimeTickFormatter(
        minutes="%H:%M", hours="%H:%M", days="%m-%d")
    p.legend.location = "top_right"

    # 确保outputs目录存在
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    # 生成输出文件名
    output_filename = save_name if save_name else str(OUTPUTS_DIR / f"{title}.html")
    output_file(output_filename, title=title)
    save(p)
    print(f"[*] Bokeh 柱状图已生成: {output_filename}")

# 任务一：测试代码
if __name__ == '__main__':
    import random
    from datetime import datetime, timedelta

    # 生成过去1小时，每5分钟一个点的时间序列
    now = datetime.now()
    time_list = [now - timedelta(minutes=i*5) for i in range(12)][::-1]
    # 生成20%-80%的随机CPU利用率
    value_list = [random.randint(20, 80) for _ in range(12)]

    # 生成测试柱状图
    bokeh_bar(time_list, value_list, 'Router1_CPU', title='CPU利用率柱状图')