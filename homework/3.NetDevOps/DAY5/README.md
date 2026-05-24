# NetDevOps DAY5 — BS4 爬虫分析乾颐堂作业系统

## 作业背景

使用 Python `requests` 库模拟登录乾颐堂作业系统（处理 CSRF Token），再通过 `BeautifulSoup` 解析"我的作业"页面 HTML 表格，提取作业数据后用 `matplotlib` 生成两张可视化饼图：课程分数分布图与课程作业分布图。

## 实验环境

| 组件 | 版本/地址 |
|------|-----------|
| Linux 服务器 | 10.10.1.205 (Rocky Linux 9.7) |
| Python | 3.x |
| 目标网站 | https://qytsystem.qytang.com |
| 关键依赖 | requests / beautifulsoup4 / matplotlib |
| 中文字体 | Noto Sans CJK JP |

## 项目结构

```
DAY5/
├── task1_bs4_homework_analyzer.py          # 主程序：登录+解析+绘图
├── 1. httpsqytsystem.qytang.compython_.txt # 离线HTML备份（网络不可达时使用）
├── score_distribution.png                  # 输出：课程分数分布饼图
├── course_homework_distribution.png        # 输出：课程作业分布饼图
└── README.md                               # 本文档
```

## 任务说明

### 任务一：爬虫分析作业数据并生成可视化图表

**要求：**
1. 使用 `requests.Session()` 访问登录页面，提取 CSRF Token
2. POST 登录表单（携带 csrfmiddlewaretoken / username / password / Referer）
3. GET 获取"我的作业"页面 HTML
4. 使用 `BeautifulSoup` 定位 `<table id="table-for-student">`，逐行解析 9 列数据
5. 使用 `matplotlib` 生成两张饼图并保存为 PNG
6. 网络不可达时自动回退到本地 HTML 文件解析

**表格字段解析：**

| 列序号 | 字段 | 说明 |
|--------|------|------|
| 0 | 编号 | 作业序号 |
| 1 | 课程 | Python基础 / 经典自动化协议 / NetDevOps |
| 2 | 第几天 | DAY编号 |
| 3 | 作业日期 | 日期字符串 |
| 4 | 上传时间 | 提交时间戳 |
| 5 | 批阅状态 | 是否已批改 |
| 6 | 批阅时间 | 老师批改时间 |
| 7 | 成绩 | A / A- / B+ / B / C |
| 8 | 随机分 | 附加评分 |

**预期输出：**

```
==================================================
NetDevOps DAY5 - BS4爬虫作业分析
==================================================

[*] 尝试网络登录爬取...
[*] 步骤1: 访问登录页面获取CSRF Token...
[+] CSRF Token: aBcDeFgHiJkLmNoPqRsT...
[*] 步骤2: 提交登录表单...
[+] 登录请求成功，状态码: 200
[*] 步骤3: 获取'我的作业'页面...
[+] 成功获取作业页面，内容长度: 85432 字符

[*] 使用BeautifulSoup解析作业表格...
[+] 共解析到 42 条作业记录

==================================================
作业数据统计摘要
==================================================
总作业数: 42

课程分布:
  Python基础: 16 份作业
  经典自动化协议: 10 份作业
  NetDevOps: 16 份作业

成绩分布:
  A: 20 次
  A-: 12 次
  B+: 8 次
  B: 2 次
==================================================

[*] 生成统计图表...
[+] 课程分数分布图已保存: /netdevops/homework/3.NetDevOps/DAY5/score_distribution.png
[+] 课程作业分布图已保存: /netdevops/homework/3.NetDevOps/DAY5/course_homework_distribution.png

[+] 全部完成！输出文件:
    - 课程分数分布图: score_distribution.png
    - 课程作业分布图: course_homework_distribution.png
```

## 核心代码逻辑

### 登录流程（CSRF + Session）

```python
session = requests.Session()
# 1. GET登录页 -> 解析hidden input获取csrfmiddlewaretoken
login_page = session.get(LOGIN_URL)
soup = BeautifulSoup(login_page.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

# 2. POST登录（必须带Referer头）
login_data = {'csrfmiddlewaretoken': csrf_token, 'username': USERNAME, 'password': PASSWORD}
session.post(LOGIN_URL, data=login_data, headers={'Referer': LOGIN_URL})
```

### 饼图颜色映射

```python
# 分数分布 - 固定颜色映射
color_map = {'A': '#d62728', 'A-': '#9467bd', 'B+': '#2ca02c', 'B': '#1f77b4', 'C': '#ff7f0e'}

# 课程分布 - 按课程名称映射
color_map = {'Python基础': '#1f77b4', '经典自动化协议': '#ff7f0e', 'NetDevOps': '#2ca02c'}
```

## 运行步骤

```bash
# 1. 安装依赖
pip install requests beautifulsoup4 matplotlib

# 2. 确认中文字体可用
fc-list | grep -i "noto.*cjk"

# 3. 运行主程序
cd /netdevops/homework/3.NetDevOps/DAY5/
python task1_bs4_homework_analyzer.py

# 4. 查看输出图片
ls -la *.png
```

## 知识点

- `requests.Session()` 会话保持（Cookie 自动管理）
- Django CSRF Token 防护机制与绕过
- `BeautifulSoup` HTML 表格解析（find / find_all / get_text）
- `matplotlib.pyplot.pie()` 饼图绑定与百分比标注
- `collections.Counter` 数据统计
- `plt.rcParams` 中文字体全局配置
- 网络爬取失败时的本地文件 fallback 策略

## 截图清单

1. 程序运行终端输出（含登录、解析、统计摘要）
2. `score_distribution.png` 课程分数分布饼图
3. `course_homework_distribution.png` 课程作业分布饼图

## 提交文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `task1_bs4_homework_analyzer.py` | Python | 主程序：登录+BS4解析+matplotlib绘图 |
| `score_distribution.png` | 图片 | 课程分数分布饼图（A/A-/B+/B/C） |
| `course_homework_distribution.png` | 图片 | 课程作业数量分布饼图 |
| `README.md` | 文档 | 本文档 |
