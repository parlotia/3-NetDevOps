# DAY5 - InfluxDB + Grafana 监控平台

## 服务说明

### InfluxDB 1.8.5 (时序数据库)
- **容器名**: qyt-influx
- **端口**: 8086
- **访问地址**: http://localhost:8086
- **数据库**: qytdb
- **管理员账号**:
  - 用户名: `admin`
  - 密码: `Cisc0123`
- **普通用户**:
  - 用户名: `qytdbuser`
  - 密码: `Cisc0123`

### Grafana 7.5.11 (数据可视化)
- **容器名**: qyt-grafana
- **端口**: 3000
- **访问地址**: http://localhost:3000
- **默认账号**:
  - 用户名: `admin`
  - 密码: `admin`

## 快速启动

### 1. 启动服务
```bash
cd /netdevops/homework/2.Protocol/DAY5
docker-compose up -d
```

### 2. 查看服务状态
```bash
docker-compose ps
```

### 3. 查看日志
```bash
# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f influxdb
docker-compose logs -f grafana
```

### 4. 停止服务
```bash
docker-compose down
```

### 5. 停止并删除数据卷（重置所有数据）
```bash
docker-compose down -v
```

## 配置 Grafana 连接 InfluxDB

1. 访问 http://localhost:3000
2. 使用 admin/admin 登录
3. 点击 Configuration → Data Sources
4. 点击 Add data source → 选择 InfluxDB
5. 配置如下：
   - **URL**: http://qyt-influx:8086
   - **Database**: qytdb
   - **User**: qytdbuser
   - **Password**: Cisc0123
6. 点击 Save & Test

## 目录结构

```
DAY5/
├── docker-compose.yml              # Docker Compose 配置文件
├── README.md                       # 使用说明
├── start.sh                        # 快速启动脚本
└── qyt_influxdb/
    └── init-influxdb.sh           # InfluxDB 初始化脚本
```

## 数据持久化

所有数据都保存在宿主机目录中：
- `/data/influxdb`: InfluxDB 数据文件
- `/data/grafana`: Grafana 配置和仪表盘

## 网络配置

两个容器在同一个 `monitoring` 网络中，可以通过服务名互相访问。

## 常见问题

### 端口被占用
如果 8086 或 3000 端口被占用，修改 docker-compose.yml 中的端口映射：
```yaml
ports:
  - "8087:8086"  # 改为 8087
  - "3001:3000"  # 改为 3001
```

### 重置数据
```bash
docker-compose down -v
docker-compose up -d
```
