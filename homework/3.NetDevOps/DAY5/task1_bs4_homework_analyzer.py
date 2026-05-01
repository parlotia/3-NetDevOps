'''
=================================================================
NetDevOps DAY5 任务一
使用BS4爬虫技术分析自己的Python作业情况
=================================================================
任务要求:
1. 使用requests登录乾颐堂作业系统
2. 使用BeautifulSoup解析"我的作业"页面表格数据
3. 使用matplotlib生成两张饼图:
   - 课程分数分布图
   - 课程作业分布图
'''

import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from collections import Counter
import os


# ======================
# 配置参数
# ======================
LOGIN_URL = 'https://qytsystem.qytang.com/accounts/login/'
HOMEWORK_URL = 'https://qytsystem.qytang.com/python_enhance/python_enhance_homework'
USERNAME = 'pye_zhufs'
PASSWORD = '2Sx-66coR'
LOCAL_HTML = '/netdevops/homework/3.NetDevOps/DAY5/1. httpsqytsystem.qytang.compython_.txt'
OUTPUT_DIR = '/netdevops/homework/3.NetDevOps/DAY5'


def setup_chinese_font():
    """
    配置matplotlib中文字体支持
    """
    # Noto Sans CJK JP 同样支持中文显示
    plt.rcParams['font.family'] = ['Noto Sans CJK JP', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False


def login_and_fetch():
    """
    登录乾颐堂系统并获取"我的作业"页面HTML

    返回:
        作业页面的HTML文本
    """
    session = requests.Session()

    # 步骤1: 访问登录页面，获取CSRF Token
    print("[*] 步骤1: 访问登录页面获取CSRF Token...")
    login_page = session.get(LOGIN_URL, timeout=10)
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})

    if csrf_input and csrf_input.get('value'):
        csrf_token = csrf_input['value']
    else:
        # 从cookie中获取
        csrf_token = session.cookies.get('csrftoken', '')

    print(f"[+] CSRF Token: {csrf_token[:20]}...")

    # 步骤2: 提交登录表单
    print("[*] 步骤2: 提交登录表单...")
    login_data = {
        'csrfmiddlewaretoken': csrf_token,
        'username': USERNAME,
        'password': PASSWORD,
    }
    headers = {
        'Referer': LOGIN_URL,
    }
    login_resp = session.post(LOGIN_URL, data=login_data, headers=headers, timeout=10)

    # 检查是否登录成功（通过状态码或页面内容判断）
    if login_resp.status_code == 200:
        print(f"[+] 登录请求成功，状态码: {login_resp.status_code}")
    else:
        raise Exception(f"登录失败，状态码: {login_resp.status_code}")

    # 步骤3: 获取"我的作业"页面
    print("[*] 步骤3: 获取'我的作业'页面...")
    hw_resp = session.get(HOMEWORK_URL, timeout=10)

    if hw_resp.status_code == 200:
        print(f"[+] 成功获取作业页面，内容长度: {len(hw_resp.text)} 字符")
        return hw_resp.text
    else:
        raise Exception(f"获取作业页面失败，状态码: {hw_resp.status_code}")


def parse_homework_table(html_content):
    """
    使用BeautifulSoup解析作业表格数据

    参数:
        html_content: 作业页面的HTML文本

    返回:
        作业记录列表，每条记录为字典
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 定位表格
    table = soup.find('table', {'id': 'table-for-student'})
    if not table:
        raise Exception("未找到id='table-for-student'的表格")

    tbody = table.find('tbody')
    if not tbody:
        raise Exception("未找到表格的tbody")

    rows = tbody.find_all('tr')
    homework_data = []

    for idx, row in enumerate(rows, 1):
        tds = row.find_all('td')
        if len(tds) < 9:
            continue

        # 提取各列数据（使用get_text清理标签）
        record = {
            '编号': tds[0].get_text(strip=True),
            '课程': tds[1].get_text(strip=True),
            '第几天': tds[2].get_text(strip=True),
            '作业日期': tds[3].get_text(strip=True),
            '上传时间': tds[4].get_text(strip=True),
            '批阅状态': tds[5].get_text(strip=True),
            '批阅时间': tds[6].get_text(strip=True),
            '成绩': tds[7].get_text(strip=True),
            '随机分': tds[8].get_text(strip=True),
        }
        homework_data.append(record)

    return homework_data


def generate_score_distribution_chart(data, output_path):
    """
    生成课程分数分布饼图

    参数:
        data: 作业记录列表
        output_path: 图片保存路径
    """
    # 只统计已批改的成绩（排除"未知"和空值）
    valid_grades = [d['成绩'] for d in data if d['成绩'] not in ['未知', '']]
    grade_counter = Counter(valid_grades)

    if not grade_counter:
        print("[-] 没有有效的成绩数据，跳过分数分布图")
        return

    # 定义所有可能的成绩等级和颜色映射
    all_grades = ['A', 'A-', 'B+', 'B', 'C']
    color_map = {
        'A': '#d62728',    # 红色
        'A-': '#9467bd',   # 紫色
        'B+': '#2ca02c',   # 绿色
        'B': '#1f77b4',    # 蓝色
        'C': '#ff7f0e',    # 橙色
    }

    # 只保留数据中存在的成绩，但按固定顺序排列
    present_grades = [g for g in all_grades if g in grade_counter]
    present_values = [grade_counter[g] for g in present_grades]
    present_colors = [color_map[g] for g in present_grades]

    # 创建饼图
    fig, ax = plt.subplots(figsize=(10, 7))
    wedges, texts, autotexts = ax.pie(
        present_values,
        labels=present_grades,
        autopct='%1.1f%%',
        startangle=90,
        colors=present_colors,
        textprops={'fontsize': 12}
    )

    # 设置百分比文字样式
    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_color('black')

    ax.set_title('课程分数分布图', fontsize=16, fontweight='bold')

    # 图例显示所有等级（包括数量为0的），方便查看颜色对应关系
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=color_map[g], label=g) for g in all_grades]
    ax.legend(
        handles=legend_elements,
        title="成绩",
        loc="upper left",
        bbox_to_anchor=(1.02, 1)
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[+] 课程分数分布图已保存: {output_path}")


def generate_course_distribution_chart(data, output_path):
    """
    生成课程作业分布饼图

    参数:
        data: 作业记录列表
        output_path: 图片保存路径
    """
    course_counter = Counter([d['课程'] for d in data])

    if not course_counter:
        print("[-] 没有课程数据，跳过课程分布图")
        return

    # 定义颜色映射
    color_map = {
        'Python基础': '#1f77b4',      # 蓝色
        '经典自动化协议': '#ff7f0e',   # 橙色
        'NetDevOps': '#2ca02c',        # 绿色
        'Python经典协议': '#ff7f0e',   # 兼容旧名称
        'Django': '#2ca02c',           # 兼容旧名称
    }
    colors = [color_map.get(c, '#9467bd') for c in course_counter.keys()]

    # 创建饼图
    fig, ax = plt.subplots(figsize=(10, 7))
    wedges, texts, autotexts = ax.pie(
        course_counter.values(),
        labels=course_counter.keys(),
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 12}
    )

    # 设置百分比文字样式
    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_color('black')

    ax.set_title('课程作业分布图', fontsize=16, fontweight='bold')
    ax.legend(
        wedges,
        course_counter.keys(),
        title="课程",
        loc="upper left",
        bbox_to_anchor=(1.02, 1)
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[+] 课程作业分布图已保存: {output_path}")


def print_data_summary(data):
    """
    打印数据统计摘要
    """
    print("\n" + "=" * 50)
    print("作业数据统计摘要")
    print("=" * 50)
    print(f"总作业数: {len(data)}")

    # 按课程统计
    course_counter = Counter([d['课程'] for d in data])
    print(f"\n课程分布:")
    for course, count in course_counter.most_common():
        print(f"  {course}: {count} 份作业")

    # 成绩统计
    valid_grades = [d['成绩'] for d in data if d['成绩'] not in ['未知', '']]
    grade_counter = Counter(valid_grades)
    print(f"\n成绩分布:")
    for grade, count in grade_counter.most_common():
        print(f"  {grade}: {count} 次")

    # 显示前5条记录
    print(f"\n前5条作业记录:")
    for d in data[:5]:
        print(f"  编号{d['编号']}: {d['课程']} 第{d['第几天']}天 - 成绩: {d['成绩']}")
    print("=" * 50 + "\n")


def main():
    print("=" * 50)
    print("NetDevOps DAY5 - BS4爬虫作业分析")
    print("=" * 50)

    # 配置中文字体
    setup_chinese_font()

    # 步骤1: 获取HTML内容（优先网络爬取，失败则使用本地文件）
    html_content = None

    try:
        print("\n[*] 尝试网络登录爬取...")
        html_content = login_and_fetch()
    except Exception as e:
        print(f"[-] 网络爬取失败: {e}")
        print(f"[*] 回退到本地HTML文件...")
        if os.path.exists(LOCAL_HTML):
            with open(LOCAL_HTML, 'r', encoding='utf-8') as f:
                html_content = f.read()
            print(f"[+] 已加载本地HTML文件，内容长度: {len(html_content)} 字符")
        else:
            print(f"[-] 本地文件不存在: {LOCAL_HTML}")
            return

    # 步骤2: 解析表格数据
    print("\n[*] 使用BeautifulSoup解析作业表格...")
    homework_data = parse_homework_table(html_content)
    print(f"[+] 共解析到 {len(homework_data)} 条作业记录")

    # 步骤3: 打印统计摘要
    print_data_summary(homework_data)

    # 步骤4: 生成饼图
    print("[*] 生成统计图表...")

    score_chart_path = os.path.join(OUTPUT_DIR, 'score_distribution.png')
    course_chart_path = os.path.join(OUTPUT_DIR, 'course_homework_distribution.png')

    generate_score_distribution_chart(homework_data, score_chart_path)
    generate_course_distribution_chart(homework_data, course_chart_path)

    print("\n[+] 全部完成！输出文件:")
    print(f"    - 课程分数分布图: {score_chart_path}")
    print(f"    - 课程作业分布图: {course_chart_path}")


if __name__ == '__main__':
    main()
