# Grafana Dashboard 配置说明

## 1. 启动InfluxDB和Grafana

使用docker-compose启动服务：

```bash
cd /netdevops/homework/2.Protocol/DAY6
docker-compose up -d
```

## 2. 配置Grafana数据源

1. 访问 Grafana: http://localhost:3000
2. 默认登录账号: admin / admin
3. 进入 Configuration → Data Sources
4. 点击 "Add data source"
5. 选择 InfluxDB
6. 配置如下：
   - Name: InfluxDB
   - URL: http://qyt-influx:8086
   - Database: qytdb
   - User: qytdbuser
   - Password: Cisc0123
7. 点击 "Save & Test"

## 3. 导入Dashboard

### 方法一：导入JSON文件

1. 进入 Grafana 主页
2. 点击 "+" → Import
3. 上传 `Dashboard_Speed.json` 文件
4. 选择数据源为刚配置的 InfluxDB
5. 点击 "Import"

### 方法二：手动创建Dashboard

#### 创建入向速率面板

1. 点击 "+" → Dashboard → Add new panel
2. 配置Query：
   - Query模式：InfluxDB
   - Query语句：
   ```sql
   SELECT non_negative_derivative(mean("in_bytes"), 1s) * 8 FROM "interface_monitor" WHERE $timeFilter GROUP BY time($__interval), device_ip, interface_name
   ```
   - Alias: `[[tag_device_ip]]--[[tag_interface_name]]`
   - Unit: bits/sec(SI)
3. 设置面板标题：接口入向速率 (RX)

#### 创建出向速率面板

1. 在同一Dashboard中添加新面板
2. 配置Query：
   - Query模式：InfluxDB
   - Query语句：
   ```sql
   SELECT non_negative_derivative(mean("out_bytes"), 1s) * 8 FROM "interface_monitor" WHERE $timeFilter GROUP BY time($__interval), device_ip, interface_name
   ```
   - Alias: `[[tag_device_ip]]--[[tag_interface_name]]`
   - Unit: bits/sec(SI)
3. 设置面板标题：接口出向速率 (TX)

## 4. 配置Crond定时任务

编辑crontab：

```bash
vim /etc/crontab
```

添加以下行（每分钟执行一次）：

```bash
# 每分钟执行一次 SNMP 采集写入 SQLite
* * * * * root /netdevops/.venv/bin/python3.11 /netdevops/homework/2.Protocol/DAY6/code/day6_2_write_sqlite.py >> /tmp/day6_sqlite.log 2>&1

# 每分钟执行一次 SNMP 采集写入 InfluxDB
* * * * * root /netdevops/.venv/bin/python3.11 /netdevops/homework/2.Protocol/DAY6/code/day6_4_write_influxdb.py >> /tmp/day6_influx.log 2>&1
```

重启crond服务：

```bash
systemctl restart crond
```

查看日志：

```bash
tail -f /tmp/day6_sqlite.log
tail -f /tmp/day6_influx.log
```

## 5. 查看Bokeh图表

运行任务3生成Bokeh交互式图表：

```bash
cd /netdevops/homework/2.Protocol/DAY6/code
python3 day6_3_show_sqlite.py
```

图表将保存在 `outputs/` 目录下：
- `interface_rx_speed.html` - 入向速率图
- `interface_tx_speed.html` - 出向速率图

## 6. 注意事项

1. 确保InfluxDB和Grafana容器正常运行
2. 确保SNMP配置正确，设备可达
3. 至少等待10分钟让Crond收集足够数据点
4. Grafana的non_negative_derivative函数会自动处理计数器翻转
5. 时间范围选择建议：最近1小时或最近30分钟
