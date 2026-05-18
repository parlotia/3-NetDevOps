#!/bin/bash

# SNMP数据采集交互式脚本
# 每次运行前询问用户是否执行

echo "====================================="
echo "SNMP数据采集工具"
echo "====================================="
echo ""
echo "此脚本将执行以下操作："
echo "  1. 通过SNMP采集路由器接口数据"
echo "  2. 将数据写入InfluxDB数据库"
echo "  3. 用于Grafana监控面板显示"
echo ""
echo "数据来源: /netdevops/homework/2.Protocol/DAY5/write_influxdb.py"
echo ""

# 询问用户是否继续
read -p "是否立即执行数据采集？(y/n): " choice

case "$choice" in 
  y|Y|yes|YES)
    echo ""
    echo "开始执行数据采集..."
    echo "====================================="
    echo ""
    
    # 执行Python脚本
    /usr/bin/python3 /netdevops/homework/2.Protocol/DAY5/write_influxdb.py
    
    # 检查执行结果
    if [ $? -eq 0 ]; then
        echo ""
        echo "====================================="
        echo "✅ 数据采集成功完成！"
        echo "====================================="
        echo ""
        echo "数据已写入InfluxDB，可以在Grafana中查看。"
    else
        echo ""
        echo "====================================="
        echo "❌ 数据采集失败！"
        echo "====================================="
        echo ""
        echo "请检查："
        echo "  1. InfluxDB容器是否运行: docker ps | grep influx"
        echo "  2. 路由器SNMP配置是否正确"
        echo "  3. 网络连接是否正常"
    fi
    ;;
  n|N|no|NO)
    echo ""
    echo "已取消数据采集。"
    echo ""
    echo "提示：如需稍后执行，可手动运行："
    echo "  python3 /netdevops/homework/2.Protocol/DAY5/write_influxdb.py"
    ;;
  *)
    echo ""
    echo "无效输入，已取消。"
    ;;
esac

echo ""
