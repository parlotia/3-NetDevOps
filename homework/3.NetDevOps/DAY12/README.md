# NetDevOps DAY12 — AWS CloudFormation 基础设施即代码实战

## 作业背景

使用 AWS CloudFormation 模板（Infrastructure as Code）自动化创建云基础设施：依次部署 VPC 网络环境、EC2 计算实例、S3 存储桶三个 Stack，通过 Stack 间的 `Outputs/ImportValue` 实现资源引用。完成后 SSH 登录 EC2，使用 AWS CLI 操作 S3，最终清理所有资源。

## 实验环境

| 组件 | 版本/地址 |
|------|-----------|
| AWS 区域 | eu-north-1 (Europe Stockholm) |
| CloudFormation | YAML 模板格式 |
| EC2 实例 | Amazon Linux 2 (t3.micro) |
| VPC CIDR | 10.1.0.0/16 |
| EC2 KeyPair | us-east-1-zfs |
| S3 桶名 | netdevops-s3-basic-2026-zfs |
| EC2 密码 | root/Cisc0123 |

## 项目结构

```
DAY12/
├── cft_1_vpc.yaml                  # Stack 1：VPC + 子网 + 路由表 + IGW + 安全组
├── cft_2_ec2.yaml                  # Stack 2：EC2 + IAM Role + 公网IP输出
├── cft_3_s3.yaml                   # Stack 3：S3 桶（全局唯一名称）
├── CloudFormation实战总结.md        # 详细实验文档（802行，含完整操作截图指导）
└── README.md                       # 本文档
```

## 任务说明

### 任务一：创建 VPC 网络环境（cft_1_vpc.yaml）

**创建资源：**
- VPC（10.1.0.0/16）
- Internet Gateway + VPC 附加
- 子网 EC2Net1
- 路由表 + 默认路由 0.0.0.0/0 → IGW
- 安全组 EC2SecurityGroup（允许 SSH/ICMP/全出站）

**Outputs 导出：**
```yaml
Outputs:
  VPCID:
    Export: { Name: VPCID }
  EC2SubnetID:
    Export: { Name: EC2SubnetID }
  SecurityGroupID:
    Export: { Name: SecurityGroupID }
```

### 任务二：创建 EC2 实例（cft_2_ec2.yaml）

**创建资源：**
- IAM Role + Instance Profile（EC2 服务角色）
- EC2 实例（引用 Stack1 导出的子网和安全组）
- UserData 脚本：开启 root SSH + 设置密码 Cisc0123

**跨 Stack 引用：**
```yaml
SubnetId: !ImportValue EC2SubnetID
SecurityGroupIds:
  - !ImportValue SecurityGroupID
```

**Outputs 输出：**
- EC2 Instance ID
- 可用区
- 公网 IP（用于 SSH 登录）

### 任务三：创建 S3 存储桶（cft_3_s3.yaml）

**创建资源：**
- S3 Bucket（全局唯一名称：netdevops-s3-basic-2026-zfs）
- 开启 Public Access Block
- DeletionPolicy: Retain

### 任务四：SSH 登录 EC2 + AWS CLI 操作 S3

```bash
# SSH登录EC2（使用Outputs中的公网IP）
ssh root@<EC2_PUBLIC_IP>

# AWS CLI操作S3
aws s3 ls                                           # 查看桶列表
aws s3 cp /tmp/test.txt s3://netdevops-s3-basic-2026-zfs/  # 上传文件
aws s3 ls s3://netdevops-s3-basic-2026-zfs/         # 查看桶内容
aws s3 rm s3://netdevops-s3-basic-2026-zfs/test.txt # 删除文件
```

### 任务五：清理所有 Stack

```bash
# 注意：必须按逆序删除（先EC2→再VPC，S3独立）
# 1. 删除EC2 Stack
# 2. 删除VPC Stack
# 3. 手动删除S3桶（DeletionPolicy: Retain）
```

## 运行步骤

```bash
# 1. 登录AWS Console → CloudFormation

# 2. 创建Stack 1: VPC
#    Upload: cft_1_vpc.yaml
#    Stack Name: EC2VPC
#    等待状态: CREATE_COMPLETE

# 3. 创建Stack 2: EC2
#    Upload: cft_2_ec2.yaml
#    Stack Name: EC2Full
#    参数 KeyName: 填入你的真实密钥名
#    等待状态: CREATE_COMPLETE
#    记录 Outputs 中的 PublicIP

# 4. 创建Stack 3: S3
#    Upload: cft_3_s3.yaml
#    Stack Name: S3Basic
#    等待状态: CREATE_COMPLETE

# 5. SSH登录EC2并操作S3
ssh root@<PublicIP>  # 密码: Cisc0123

# 6. 实验结束后逆序删除Stack
```

## 三个模板的依赖关系

```
cft_1_vpc.yaml (Stack: EC2VPC)
    │
    │ Exports: VPCID / EC2SubnetID / SecurityGroupID
    ▼
cft_2_ec2.yaml (Stack: EC2Full)
    │
    │ ImportValue 引用网络资源
    ▼
EC2 实例运行（可SSH登录）

cft_3_s3.yaml (Stack: S3Basic) ← 独立，无依赖
```

## 知识点

- AWS CloudFormation 模板语法（YAML 格式）
- Stack 间资源引用（Outputs + Export + ImportValue）
- VPC 网络架构（子网 / 路由表 / IGW / 安全组）
- EC2 UserData 启动脚本
- IAM Role + Instance Profile 权限分配
- S3 桶全局唯一命名与访问策略
- DeletionPolicy（Delete / Retain）资源保护
- Stack 创建/删除顺序（依赖关系）
- AWS CLI S3 操作命令

## 截图清单

1. CloudFormation Stack 列表（三个 Stack 均 CREATE_COMPLETE）
2. EC2VPC Stack 的 Outputs 页面
3. EC2Full Stack 的 Outputs 页面（含公网 IP）
4. SSH 登录 EC2 成功
5. AWS CLI S3 上传/查看/删除操作
6. Stack 删除完成

## 提交文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `cft_1_vpc.yaml` | CloudFormation | VPC + 子网 + 路由表 + IGW + 安全组 |
| `cft_2_ec2.yaml` | CloudFormation | EC2 + IAM Role + 公网 IP 输出 |
| `cft_3_s3.yaml` | CloudFormation | S3 桶（全局唯一名称） |
| `CloudFormation实战总结.md` | 文档 | 详细操作指南（含完整截图指导） |
| `README.md` | 文档 | 本文档 |
