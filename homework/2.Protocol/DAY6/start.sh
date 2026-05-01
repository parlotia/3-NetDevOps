#!/bin/bash
# DAY6 快速启动脚本

echo "=========================================="
echo "  DAY6 网络设备接口监控系统"
echo "=========================================="
echo ""

# 检查Python虚拟环境
if [ ! -d "/netdevops/.venv" ]; then
    echo "[!] 错误: 未找到Python虚拟环境 /netdevops/.venv"
    exit 1
fi

source /netdevops/.venv/bin/activate

# 1. 创建数据库
echo "[1/4] 创建SQLite数据库..."
cd /netdevops/homework/2.Protocol/DAY6/code
python3 day6_1_create_db.py
echo ""

# 2. 测试SNMP采集
echo "[2/4] 测试SNMP采集（首次运行）..."
python3 day6_2_write_sqlite.py
echo ""

# 3. 提示配置Crond
echo "[3/4] Crond配置提示"
echo "请将以下内容添加到 /etc/crontab:"
echo ""
echo "# 每分钟执行一次 SNMP 采集写入 SQLite"
echo "* * * * * root /netdevops/.venv/bin/python3.11 /netdevops/homework/2.Protocol/DAY6/code/day6_2_write_sqlite.py >> /tmp/day6_sqlite.log 2>&1"
echo ""
echo "# 每分钟执行一次 SNMP 采集写入 InfluxDB"
echo "* * * * * root /netdevops/.venv/bin/python3.11 /netdevops/homework/2.Protocol/DAY6/code/day6_4_write_influxdb.py >> /tmp/day6_influx.log 2>&1"
echo ""

# 4. 启动Docker服务
echo "[4/4] 启动InfluxDB和Grafana..."
cd /netdevops/homework/2.Protocol/DAY6
docker-compose up -d
echo ""

echo "=========================================="
echo "  启动完成！"
echo "=========================================="
echo ""
echo "下一步操作："
echo "1. 等待10-15分钟让Crond收集数据"
echo "2. 运行 python3 day6_3_show_sqlite.py 生成Bokeh图表"
echo "3. 访问 http://localhost:3000 配置Grafana"
echo "4. 导入 Dashboard_Speed.json 文件"
echo ""
echo "查看日志："
echo "  tail -f /tmp/day6_sqlite.log"
echo "  tail -f /tmp/day6_influx.log"
echo ""
