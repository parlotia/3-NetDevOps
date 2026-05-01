#!/bin/bash

echo "=========================================="
echo "DAY5 - InfluxDB + Grafana 启动脚本"
echo "=========================================="
echo ""

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "[错误] Docker 未运行，请先启动 Docker 服务"
    exit 1
fi

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "[错误] docker-compose 未安装"
    exit 1
fi

echo "[1/3] 检查并拉取镜像..."
docker-compose pull

echo ""
echo "[2/3] 启动服务..."
docker-compose up -d

echo ""
echo "[3/3] 等待服务启动..."
sleep 10

echo ""
echo "=========================================="
echo "服务状态:"
echo "=========================================="
docker-compose ps

echo ""
echo "=========================================="
echo "访问地址:"
echo "=========================================="
echo "InfluxDB: http://localhost:8086"
echo "  用户名: admin"
echo "  密码: admin123456"
echo ""
echo "Grafana: http://localhost:3000"
echo "  用户名: admin"
echo "  密码: admin"
echo "=========================================="
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
echo ""
