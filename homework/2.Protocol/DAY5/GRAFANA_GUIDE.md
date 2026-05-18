# Grafana 配置指南 - 查看路由器监控数据

## 📊 快速开始

### 方法一：导入预配置的 Dashboard（推荐）

#### 1. 添加 InfluxDB 数据源

1. **登录 Grafana**
   - 访问：http://localhost:3000
   - 用户名：`admin`
   - 密码：`admin`

2. **添加数据源**
   - 点击左侧菜单 ⚙️ **Configuration** → **Data Sources**
   - 点击 **Add data source**
   - 选择 **InfluxDB**

3. **配置数据源参数**
   ```
   Name: InfluxDB
   Query Language: InfluxQL
   
   HTTP
   URL: http://qyt-influx:8086
   
   InfluxDB Details
   Database: qytdb
   User: qytdbuser
   Password: Cisc0123
   ```

4. **保存并测试**
   - 点击 **Save & Test**
   - 应该看到 "Data source is working" ✅

#### 2. 导入 Dashboard

1. **导入预配置的 Dashboard**
   - 点击左侧菜单 ➕ **Create** → **Import**
   - 点击 **Upload JSON file**
   - 选择文件：`/netdevops/homework/2.Protocol/DAY5/grafana-dashboard.json`
   - 或者复制 JSON 内容粘贴到文本框

2. **配置导入选项**
   - Dashboard: 保持默认
   - Folder: 选择 General 或创建新文件夹
   - **InfluxDB**: 选择刚才创建的数据源 "InfluxDB"

3. **点击 Import** ✅

#### 3. 查看监控数据

导入成功后，你会看到一个包含以下面板的 Dashboard：

- **CPU利用率趋势**：折线图显示两台路由器的 CPU 使用率变化
- **内存利用率趋势**：折线图显示两台路由器的内存使用率变化
- **当前CPU利用率**：实时显示最新 CPU 数值（带颜色预警）
- **当前内存利用率**：实时显示最新内存数值（带颜色预警）

---

### 方法二：手动创建 Dashboard

如果你想自己从零创建：

#### 1. 创建新 Dashboard

1. 点击 ➕ **Create** → **Dashboard**
2. 点击 **Add new panel**

#### 2. 配置 CPU 利用率面板

**Panel Title**: `CPU利用率趋势`

**Query**:
```sql
SELECT mean("cpu_percent") FROM "router_monitor" 
WHERE ("device_ip" = '10.10.1.200') 
AND $timeFilter 
GROUP BY time($__interval) fill(null)
```

**添加第二条线（10.10.1.201）**:
```sql
SELECT mean("cpu_percent") FROM "router_monitor" 
WHERE ("device_ip" = '10.10.1.201') 
AND $timeFilter 
GROUP BY time($__interval) fill(null)
```

**Visualization**:
- Graph type: Graph (old)
- Lines: ✅ 启用
- Fill: 1
- Y-axis: 0-100, unit: percent

#### 3. 配置内存利用率面板

重复上述步骤，但查询改为：
```sql
SELECT mean("mem_percent") FROM "router_monitor" 
WHERE ("device_ip" = '10.10.1.200') 
AND $timeFilter 
GROUP BY time($__interval) fill(null)
```

#### 4. 保存 Dashboard

- 点击右上角 💾 **Save**
- Dashboard name: `路由器监控`
- 点击 **Save**

---

## 🔍 数据查询示例

### InfluxQL 查询语句

```sql
-- 查看所有数据
SELECT * FROM "router_monitor"

-- 查看最近10条记录
SELECT * FROM "router_monitor" ORDER BY time DESC LIMIT 10

-- 查看特定设备最近1小时数据
SELECT * FROM "router_monitor" 
WHERE "device_ip" = '10.10.1.200' 
AND time > now() - 1h

-- 按设备统计平均CPU
SELECT mean("cpu_percent") FROM "router_monitor" 
GROUP BY "device_ip"

-- 按设备统计平均内存
SELECT mean("mem_percent") FROM "router_monitor" 
GROUP BY "device_ip"
```

### 在 Grafana 中测试查询

1. 进入 Dashboard → 编辑面板
2. 在 Query 选项卡中输入查询
3. 点击 **Run Query** 查看结果
4. 点击 **Query Inspector** 查看详细数据

---

## 📈 Dashboard 功能说明

### 1. 时间范围控制
- 右上角可以选择时间范围
- 常用选项：
  - Last 5 minutes
  - Last 15 minutes
  - Last 1 hour
  - Last 6 hours
  - Last 24 hours

### 2. 自动刷新
- 右上角设置刷新间隔
- 推荐：1m（每分钟刷新）
- 可选：5s, 10s, 30s, 1m, 5m

### 3. 数据展示
- **折线图**：显示历史趋势
- **Stat 面板**：显示当前最新值
- **颜色预警**：
  - 🟢 绿色：正常
  - 🟡 黄色：警告（CPU > 50%, 内存 > 60%）
  - 🔴 红色：危险（CPU > 80%, 内存 > 85%）

---

## 🛠️ 故障排查

### 问题1：数据源连接失败

**检查项**：
```bash
# 检查 InfluxDB 容器是否运行
docker ps | grep influx

# 检查网络连通性
docker exec -it day5-qyt-grafana-1 ping qyt-influx

# 检查 InfluxDB 日志
docker logs day5-qyt-influx-1
```

### 问题2：没有数据显示

**检查项**：
```bash
# 检查 InfluxDB 中是否有数据
docker exec -it day5-qyt-influx-1 influx -database qytdb -username qytdbuser -password Cisc0123 -execute "SELECT * FROM router_monitor LIMIT 5"

# 检查 Crontab 是否正常运行
tail -f /tmp/snmp_influx.log

# 检查 SNMP 采集是否正常
cd /netdevops/homework/2.Protocol/DAY5 && python3 write_influxdb.py
```

### 问题3：查询结果为空

**可能原因**：
- 时间范围选择错误（选择了过去的时间但数据是现在产生的）
- device_ip 标签值错误
- measurement 名称错误（应该是 `router_monitor`）

**解决方法**：
- 设置时间范围为 `Last 1 hour`
- 检查查询语句中的 tag 值
- 在 Query Inspector 中查看详细错误信息

---

## 📝 完整操作流程

```
1. 登录 Grafana (admin/admin)
   ↓
2. 添加 InfluxDB 数据源
   - URL: http://qyt-influx:8086
   - Database: qytdb
   - User: qytdbuser
   - Password: Cisc0123
   ↓
3. 导入 Dashboard (grafana-dashboard.json)
   ↓
4. 选择数据源 "InfluxDB"
   ↓
5. 查看实时监控数据 ✅
```

---

## 🎯 最终效果

成功后你将看到：

```
┌─────────────────────────────────────────────────┐
│  路由器监控 - CPU和内存利用率                    │
├──────────────────────┬──────────────────────────┤
│  CPU利用率趋势       │  内存利用率趋势          │
│  📈 折线图           │  📈 折线图               │
│  - 10.10.1.200       │  - 10.10.1.200          │
│  - 10.10.1.201       │  - 10.10.1.201          │
├──────────────────────┴──────────────────────────┤
│  当前CPU利用率  │  当前内存利用率               │
│  🟢 2%          │  🟡 65%                       │
└─────────────────────────────────────────────────┘
```

数据每分钟自动更新，实时显示路由器的性能状态！
