# NetDevOps DAY10 - PYATS OSPF状态监控与告警系统

## 实验环境

| 设备 | IP | 角色 |
|------|-----|------|
| C8Kv1 (R1) | 10.10.1.200 | OSPF状态监控源设备 |
| C8Kv2 (R2) | 10.10.1.201 | OSPF配置变更目标设备 |
| Linux服务器 | 10.10.1.205 | 数据采集与告警服务器 |
| QQ邮箱SMTP | smtp.qq.com:465 | 邮件告警服务 |

**账号信息：** admin / Cisc0123

### 依赖安装

```bash
# 安装 PYATS 和 Genie（需要额外依赖）
pip install pyats[full] genie

# 或使用虚拟环境
source /netdevops/.venv/bin/activate
pip install pyats[full] genie
```

---

## 任务一：创建数据库表并定时采集OSPF状态

**题目**：创建SQLite数据库表存储OSPF状态和路由表信息，使用PYATS脚本定期采集并写入数据库。

### 数据库表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 唯一ID，主键 |
| device_name | String(64) | 设备名称 |
| device_ip | String(64) | 设备IP地址 |
| ospf_status | JSON | OSPF状态 |
| route_table_status | JSON | 路由表状态 |
| record_datetime | DateTime | 记录时间（Asia/Chongqing时区） |

### 操作步骤

**1. 创建数据库模型**

执行 `code/day10_1_create_db.py` 创建数据库表：

```bash
cd /netdevops/homework/3.NetDevOps/DAY10/code
python3 day10_1_create_db.py
```

**2. 配置Testbed文件**

编辑 `code/device_info.yaml`，配置设备连接信息。

**3. 执行OSPF状态采集**

执行 `code/day10_2_collect_ospf.py` 采集OSPF状态：

```bash
python3 day10_2_collect_ospf.py
```

**4. 配置crond定时采集**

```bash
# 每5分钟采集一次
*/5 * * * * cd /netdevops/homework/3.NetDevOps/DAY10/code && python3 day10_2_collect_ospf.py >> /var/log/day10_collect.log 2>&1
```

---

## 任务二：OSPF状态比较与邮件告警

**题目**：比较最近两次采集的OSPF状态，如果有差异则发送邮件告警。

### 操作步骤

**1. 执行状态比较脚本**

```bash
python3 day10_3_compare_and_alert.py
```

**2. 配置crond定时比较**

```bash
# 每10分钟比较一次
*/10 * * * * cd /netdevops/homework/3.NetDevOps/DAY10/code && python3 day10_3_compare_and_alert.py >> /var/log/day10_alert.log 2>&1
```

### 邮件告警格式

**主题**：`C8Kv1-OSPF 状态改变` 或 `C8Kv2-OSPF 状态改变`

**收件人**：3348326959@qq.com; collinsctk@qytang.com

**正文**：使用 `-` 和 `+` 标记差异（类似diff输出格式）

---

## 目录结构

```
DAY10/
├── README.md
└── code/
    ├── day10_1_create_db.py           # 数据库模型创建
    ├── day10_2_collect_ospf.py        # OSPF状态采集
    ├── day10_3_compare_and_alert.py   # 状态比较与邮件告警
    ├── device_info.yaml               # Testbed配置
    └── sqlalchemy_pyats.db            # SQLite数据库文件（自动生成）
```

---

## 踩坑记录

### 1. PYATS learn() 返回的是 Genie 对象而非字典

**现象**：直接调用 `.to_dict()` 转换失败。

**修复**：确保使用 `learn('ospf').to_dict()` 正确转换。

### 2. JSON字段存储需要序列化

**现象**：直接存储字典到SQLite报错。

**修复**：使用 `json.dumps()` 序列化后再存储。

### 3. crond环境变量问题

**现象**：crond执行时找不到Python或模块。

**修复**：在crontab中使用绝对路径，或在脚本开头设置PATH。

### 4. SSH连接超时

**现象**：PYATS连接设备时超时。

**修复**：增加 `connection_timeout` 参数，使用 `ssh_options='-o StrictHostKeyChecking=no'`。

---

## 完整数据流

```
crond触发采集脚本
  → PYATS连接C8Kv1/C8Kv2
  → learn('ospf') 获取OSPF状态
  → parse('show ip route') 获取路由表
  → 序列化JSON写入SQLite数据库
  → crond触发比较脚本
  → 查询最近两条记录
  → Diff比较OSPF状态
  → 如有差异，发送邮件告警
```

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `day10_1_create_db.py` | 数据库模型创建脚本 |
| `day10_2_collect_ospf.py` | OSPF状态采集脚本 |
| `day10_3_compare_and_alert.py` | 状态比较与邮件告警脚本 |
| `device_info.yaml` | PYATS Testbed配置文件 |
| `qyt_smtp_attachment.py` | SMTP邮件发送工具 |
