#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import pygal
import os
from pathlib import Path
import cairosvg

# 输出目录: 当前文件上两级目录下的 outputs/
OUTPUTS_DIR = Path(__file__).resolve().parent.parent / 'outputs'


def pygal_pie(name_list, count_list, title, save_name=None):
    """使用 Pygal 绘制交互式饼状图，并返回 PNG 路径用于邮件内嵌。"""

    # 创建饼图对象，inner_radius 设置为环形图（如果不需要环形可以设为 0）
    from pygal.style import Style
    custom_style = Style(
        font_family='Noto Sans CJK SC'
    )
    pie_chart = pygal.Pie(inner_radius=0.4, title=title, style=custom_style)

    # 添加数据
    for name, count in zip(name_list, count_list):
        pie_chart.add(name, count)

    # 保存为单独的 SVG 文件
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # 将 SVG 转换为 PNG 用于邮件内嵌
    png_filename = save_name if save_name else str(OUTPUTS_DIR / f"{title}.png")
    cairosvg.svg2png(bytestring=pie_chart.render(), write_to=png_filename)

    print(f"[*] Pygal 饼状图已生成 PNG: {png_filename}")

    return png_filename


if __name__ == '__main__':
    # 测试代码
    names = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
    counts = [150, 45, 12, 3]
    pygal_pie(names, counts, 'SYSLOG严重级别分布图测试')
