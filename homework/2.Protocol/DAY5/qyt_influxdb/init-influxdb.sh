#!/bin/bash

# InfluxDB 初始化脚本
# 此脚本会在容器首次启动时自动执行

echo "=========================================="
echo "InfluxDB 初始化开始"
echo "=========================================="

# 等待 InfluxDB 启动
echo "等待 InfluxDB 启动..."
sleep 5

# 创建数据库（如果环境变量未自动创建）
influx -execute "CREATE DATABASE qytdb" 2>/dev/null || echo "数据库已存在"

# 创建管理员用户
influx -execute "CREATE USER admin WITH PASSWORD 'CiSc0123' WITH ALL PRIVILEGES" 2>/dev/null || echo "管理员用户已存在"

# 创建普通用户
influx -execute "CREATE USER qytdbuser WITH PASSWORD 'Cisc0123'" 2>/dev/null || echo "普通用户已存在"

# 授予用户权限
influx -execute "GRANT ALL ON qytdb TO qytdbuser" 2>/dev/null || echo "权限已授予"

echo "=========================================="
echo "InfluxDB 初始化完成"
echo "=========================================="
echo ""
echo "数据库: qytdb"
echo "管理员: admin / CiSc0123"
echo "普通用户: qytdbuser / Cisc0123"
echo ""
