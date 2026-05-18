'''
任务一: 安装bokeh模块并测试饼状图
安装依赖:

pip install bokeh pandas
完整的Bokeh饼状图函数 (直接使用即可):

from bokeh.plotting import figure, output_file, save
from bokeh.transform import cumsum
from bokeh.palettes import Category10
import pandas as pd
from math import pi
import os
from pathlib import Path

OUTPUTS_DIR = Path(__file__).resolve().parent / 'outputs'


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
测试代码:

bokeh_bing(['名称1', '名称2', '名称3'], [1000, 123, 444], '测试饼图')
测试饼图效果 (在浏览器中打开生成的HTML文件):


任务二: SSH采集Netflow数据 → 正则提取 → Bokeh饼状图
代码目录结构 (请按此组织你的文件):

day3/
└── code/
    ├── tools/                          # 工具函数目录
    │   ├── day3_ssh_single_cmd.py      # SSH单命令执行函数 (Python基础课程已学)
    │   └── day3_bokeh_bing.py          # Bokeh饼状图函数 (任务一提供)
    ├── 2026_day3_bokeh_netflow.py      # ★ 主程序 (你需要完成的作业)
    └── outputs/                        # 生成的HTML图表存放目录 (自动创建)
第一步: 在路由器上配置Netflow (已配好可跳过)

flow record qytang-record
 match application name
 collect counter bytes
!
flow monitor qytang-monitor
 record qytang-record
!
interface GigabitEthernet1
 ip flow monitor qytang-monitor input
第二步: 使用paramiko SSH登录自己的思科路由器, 执行以下命令获取Netflow数据

show flow monitor name qytang-monitor cache format table
第三步: 用正则表达式从CLI回显中提取APP NAME和bytes

CLI回显示例:

APP NAME                               bytes
================================  ==========
layer7 mdns                            24464
prot icmp                               1425
port ssh                                7085
layer7 igmp                             1760
layer7 unknown                         18529
★ 这是你需要完成的核心代码: 使用 re.match 逐行匹配, 提取出两个列表:

app_name_list: 如 ['layer7 mdns', 'prot icmp', 'port ssh', ...]
app_bytes_list: 如 ['24464', '1425', '7085', ...]
提示: APP NAME由前缀(port / layer7 / prot)加空格加应用名组成, bytes为行末的数字

第四步: 调用任务一的bokeh_bing函数生成饼状图

bokeh_bing(app_name_list, app_bytes_list, 'Netflow应用流量分布')
主程序整体流程 (2026_day3_bokeh_netflow.py):

import re
from tools.day3_ssh_single_cmd import ssh_run
from tools.day3_bokeh_bing import bokeh_bing


def get_netflow_app(host, username, password):
    """SSH登录路由器, 采集Netflow数据, 正则提取, 绘制Bokeh饼状图。"""
    # 1. SSH执行命令获取Netflow数据
    show_result = ssh_run(host, username, password,
                          'show flow monitor name qytang-monitor cache format table')
    print(show_result)

    # 2. ★ 正则提取APP NAME和bytes (你需要完成这部分!)
    app_name_list = []
    app_bytes_list = []
    for line in show_result.strip().split('\n'):
        # 你的正则代码写在这里...
        pass

    # 3. 打印提取结果
    print(f"[*] 提取到 {len(app_name_list)} 条 Netflow 记录")
    for name, byt in zip(app_name_list, app_bytes_list):
        print(f"    {name:<25s} {byt} bytes")

    # 4. 调用bokeh_bing生成饼状图
    bokeh_bing(app_name_list, app_bytes_list, 'Netflow应用流量分布')


if __name__ == "__main__":
    get_netflow_app('你的路由器IP', '用户名', '密码')
期望的终端输出:

[*] 提取到 5 条 Netflow 记录
    layer7 mdns               24464 bytes
    prot icmp                  1425 bytes
    port ssh                   7085 bytes
    layer7 igmp                1760 bytes
    layer7 unknown             18529 bytes
[*] Bokeh 饼状图已生成: .../outputs/Netflow应用流量分布.html
最终Netflow饼状图效果 (在浏览器中打开生成的HTML文件):


'''
import re
from ssh_single_cmd import ssh_run
from bokeh_bing import bokeh_bing


def get_netflow_app(host, username, password):
    """SSH登录路由器, 采集Netflow数据, 正则提取, 绘制Bokeh饼状图。"""
    # ======================
    # 1. SSH执行命令获取Netflow数据
    # ======================
    show_result = ssh_run(host, username, password,
                          'show flow monitor name qytang-monitor cache format table')
    # 打印原始回显，方便调试
    print("="*50 + " 原始Netflow数据 " + "="*50)
    print(show_result)
    print("="*120 + "\n")

    # ======================
    # 2. 正则提取APP NAME和bytes（核心补全部分）
    # ======================
    app_name_list = []
    app_bytes_list = []

    # 正则表达式：匹配有效数据行
    # 命名分组：app_name 匹配应用名，bytes 匹配字节数
    # 匹配规则：行以 layer7/prot/port 开头，中间空格分隔，行末是数字
    netflow_re = re.compile(
        r'^\s*(?P<app_name>(?:layer7|prot|port)\s+\S+)\s+(?P<bytes>\d+)\s*$',
        re.IGNORECASE
    )

    # 逐行处理回显内容
    for line in show_result.strip().split('\n'):
        line_strip = line.strip()
        # 跳过空行、表头行、分隔线行
        if not line_strip:
            continue
        if 'APP NAME' in line_strip or '===' in line_strip:
            continue
        
        # 用正则匹配当前行
        match_result = netflow_re.match(line_strip)
        if match_result:
            # 提取匹配到的应用名和字节数
            app_name = match_result.group('app_name')
            app_bytes = match_result.group('bytes')
            # 添加到列表中
            app_name_list.append(app_name)
            app_bytes_list.append(app_bytes)

    # ======================
    # 3. 打印提取结果
    # ======================
    print(f"[*] 提取到 {len(app_name_list)} 条 Netflow 记录")
    for name, byt in zip(app_name_list, app_bytes_list):
        # 左对齐25个字符，格式化输出
        print(f"    {name:<25s} {byt} bytes")

    # ======================
    # 4. 调用bokeh_bing生成饼状图
    # ======================
    if app_name_list and app_bytes_list:
        bokeh_bing(app_name_list, app_bytes_list, 'Netflow应用流量分布')
    else:
        print("[!] 未提取到有效Netflow数据，无法生成饼图")


if __name__ == "__main__":
    # ======================
    # 【重要】修改为你自己的路由器信息
    # ======================
    ROUTER_IP = '10.10.1.200'    # 路由器IP
    USERNAME = 'admin'              # SSH用户名
    PASSWORD = 'Cisc0123'           # SSH密码

    # 调用主函数
    get_netflow_app(ROUTER_IP, USERNAME, PASSWORD)