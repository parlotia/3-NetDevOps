from bokeh.plotting import figure, output_file, save
from bokeh.transform import cumsum
from bokeh.palettes import Category10
import pandas as pd
from math import pi
import os
from pathlib import Path

# 修正路径：outputs目录在code根目录下，而非tools目录
OUTPUTS_DIR = Path(__file__).resolve().parent.parent / 'outputs'


def bokeh_bing(name_list, count_list, bing_name, save_name=None):
    """使用 Bokeh 绘制饼状图, 生成交互式 HTML 文件。"""
    # 构建数据字典, 转换为 DataFrame
    data_dict = dict(zip(name_list, [float(c) for c in count_list]))
    data = pd.Series(data_dict).reset_index(name='bytes').rename(columns={'index': 'application'})

    # 计算每个扇形的角度
    data['angle'] = data['bytes'] / data['bytes'].sum() * 2 * pi

    # 分配颜色
    num = len(data_dict)
    if num <= 2:
        data['color'] = Category10[3][:num]
    elif num <= 10:
        data['color'] = Category10[num]
    else:
        data['color'] = (Category10[10] * ((num // 10) + 1))[:num]

    # 计算百分比
    data['percentage'] = (data['bytes'] / data['bytes'].sum() * 100).round(2).astype(str) + '%'

    # 创建图表
    p = figure(height=500, width=700, title=bing_name, toolbar_location="right",
               tools="hover,pan,wheel_zoom,box_zoom,reset,save",
               tooltips="@application: @bytes (@percentage)", x_range=(-0.5, 1.0))

    # 绘制饼图
    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='application', source=data)

    # 美化
    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    p.title.text_font_size = '16pt'
    p.legend.label_text_font_size = '12pt'
    p.legend.location = "center_right"

    # 输出到 outputs 目录
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    output_filename = save_name if save_name else str(OUTPUTS_DIR / f"{bing_name}.html")
    output_file(output_filename, title=bing_name)
    save(p)
    print(f"[*] Bokeh 饼状图已生成: {output_filename}")

# 测试代码（运行此文件可直接生成测试饼图）
if __name__ == '__main__':
    bokeh_bing(['名称1', '名称2', '名称3'], [1000, 123, 444], '测试饼图')