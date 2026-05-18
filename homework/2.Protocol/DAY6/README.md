# DAY6 - 网络设备接口监控

## 项目概述

本项目实现了一个完整的网络设备接口监控系统，包括：
- SNMP数据采集（支持多设备、多接口）
- SQLite数据库存储
- InfluxDB时序数据库存储
- Bokeh交互式可视化
- Grafana实时监控仪表盘

## 目录结构

```
day6/
├── code/
│   ├── tools/
│   │   ├── day6_snmp_getbulk.py      # SNMP GETBULK 批量采集工具
│   │   └── day6_bokeh_line.py        # Bokeh 折线图工具函数
│   ├── day6_1_create_db.py           # 任务1: 创建 SQLite 数据库表
│   ├── day6_2_write_sqlite.py        # 任务2: SNMP 采集写入 SQLite【Crond 调度】
│   ├── day6_3_show_sqlite.py         # 任务3: 读取 SQLite → Numpy 计算 → Bokeh 出图
│   └── day6_4_write_influxdb.py      # 任务5: SNMP 采集写入 InfluxDB【Crond 调度】
├── outputs/                           # Bokeh 生成的交互式 HTML 图表
├── docker-compose.yaml               # InfluxDB + Grafana 容器编排
├── grafana.md                        # Grafana Dashboard 配置说明
├── Dashboard_Speed.json              # Grafana Dashboard 导入文件
└── README.md                         # 本文件
```

## 快速开始

### 1. 创建数据库

```bash
cd code
python3 day6_1_create_db.py
```

### 2. 测试SNMP采集（手动运行）

```bash
python3 day6_2_write_sqlite.py
```

### 3. 配置Crond定时任务

```bash
sudo vim /etc/crontab
```

添加以下内容：

```bash
# 每分钟执行一次 SNMP 采集写入 SQLite
* * * * * root /netdevops/.venv/bin/python3.11 /netdevops/homework/2.Protocol/DAY6/code/day6_2_write_sqlite.py >> /tmp/day6_sqlite.log 2>&1

# 每分钟执行一次 SNMP 采集写入 InfluxDB
* * * * * root /netdevops/.venv/bin/python3.11 /netdevops/homework/2.Protocol/DAY6/code/day6_4_write_influxdb.py >> /tmp/day6_influx.log 2>&1
```

重启crond：

```bash
sudo systemctl restart crond
```

### 4. 生成Bokeh图表

等待至少10分钟后，运行：

```bash
python3 day6_3_show_sqlite.py
```

图表将保存在 `outputs/` 目录。

### 5. 启动Grafana监控

```bash
docker-compose up -d
```

访问 http://localhost:3000，导入 `Dashboard_Speed.json`。

## 关键技术点

### 1. SNMP GETBULK批量采集

使用IF-MIB标准OID：
- 接口名称 (ifDescr): 1.3.6.1.2.1.2.2.1.2
- 入向字节数 (ifInOctets): 1.3.6.1.2.1.2.2.1.10
- 出向字节数 (ifOutOctets): 1.3.6.1.2.1.2.2.1.16

### 2. Numpy向量化速率计算

```python
# 使用np.diff计算增量
diff_in = np.diff(in_arr)
diff_secs = np.diff(time_arr).astype(np.int64)

# 向量化计算kbps，同时过滤无效数据
valid = (diff_secs > 0) & (diff_in > 0) & (diff_out > 0)
in_kbps = np.round((diff_in[valid] * 8) / (1000 * diff_secs[valid]), 2)
```

### 3. 数据清洗策略

- 过滤时间间隔<=0的异常点
- 过滤字节增量为负的计数器翻转点
- 确保至少2个数据点才能计算速率

### 4. Grafana速率计算

使用InfluxDB的`non_negative_derivative`函数：

```sql
SELECT non_negative_derivative(mean("in_bytes"), 1s) * 8 
FROM "interface_monitor" 
WHERE $timeFilter 
GROUP BY time($__interval), device_ip, interface_name
```

## SNMP设备配置

修改以下文件中的`DEVICE_LIST`配置：
- `day6_2_write_sqlite.py`
- `day6_4_write_influxdb.py`

示例配置：

```python
DEVICE_LIST = [
    {'ip': '10.10.1.200', 'community': 'qytangro'},
    {'ip': '10.10.1.201', 'community': 'qytangro'},
]
```

## 故障排查

### 1. 查看Crond日志

```bash
tail -f /tmp/day6_sqlite.log
tail -f /tmp/day6_influx.log
```

### 2. 检查数据库内容

```python
from day6_1_create_db import InternfaceMonitor, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()
records = session.query(InternfaceMonitor).all()
for r in records:
    print(r)
session.close()
```

### 3. 检查Docker容器状态

```bash
docker-compose ps
docker-compose logs qyt-influx
docker-compose logs qyt-grafana
```

## 注意事项

1. 至少配置2个设备进行采集
2. 确保SNMP团体字正确且设备可达
3. Crond调度后需等待10分钟以上才能生成有意义的图表
4. InfluxDB使用1.8.5版本，兼容InfluxQL查询语言
5. Grafana Dashboard的单位设置为bits/sec(SI)
