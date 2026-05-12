# NetDevOps 第12天作业总结：CloudFormation 实战

## 一、作业目标

本次作业需要重新整理课堂上的 CloudFormation 代码，生成 3 个模板文件：

- [`cft_1_vpc.yaml`](homework/3.NetDevOps/DAY12/cft_1_vpc.yaml)：创建 VPC、子网、路由表、互联网网关、安全组
- [`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml)：创建 EC2，并输出公网 IP
- [`cft_3_s3.yaml`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml)：创建 S3 桶

此外，作业还要求：

1. 找到 EC2 公网 IP
2. SSH 登录 EC2
3. 使用 AWS CLI 对 S3 桶进行上传、查看、删除操作
4. 实验结束后删除所有 CloudFormation Stack
5. 保留相关截图作为作业提交材料

---

## 二、当前已完成内容

目前已经按课堂代码风格整理好以下 3 个模板文件：

- [`cft_1_vpc.yaml`](homework/3.NetDevOps/DAY12/cft_1_vpc.yaml)
- [`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml)
- [`cft_3_s3.yaml`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml)

其中已根据本次作业要求做了如下调整：

### 1. S3 桶名已修改为唯一风格

在 [`cft_3_s3.yaml`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml:7) 中，桶名设置为：

- `netdevops-s3-basic-2026-zfs`

这样做是因为 S3 桶名要求全局唯一，不能直接照抄老师原始名称。

### 2. EC2 KeyPair 按老师思路保留为参数

在 [`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:4) 中，使用了参数 `KeyName`，并给了默认值：

- `us-east-1-zfs`

这符合老师代码风格：

- KeyPair 作为参数输入
- 但保留一个默认值，方便直接部署

### 3. EC2 实例名称做了个性化调整

在 [`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:58) 中，实例标签名为：

- `EC2Full-zfs`

---

## 三、各模板作用说明

## 1. [`cft_1_vpc.yaml`](homework/3.NetDevOps/DAY12/cft_1_vpc.yaml)

该模板主要用于创建网络环境，包含以下资源：

- VPC
- Internet Gateway
- 子网 `EC2Net1`
- 路由表
- 默认路由 `0.0.0.0/0`
- 安全组 `EC2SecurityGroup`

这个模板还通过 `Outputs` 导出了：

- VPC ID
- 子网 ID
- 安全组 ID

这些导出值会被 [`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml) 引用。

## 2. [`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml)

该模板主要用于创建 EC2，包含以下功能：

- 使用已有 VPC Stack 导出的子网和安全组
- 创建 IAM Role 和 Instance Profile
- 创建 EC2 实例
- 通过 `UserData` 开启 root SSH 登录
- 设置 root 密码为 `Cisc0123`
- 输出 EC2 实例 ID、可用区和公网 IP

公网 IP 输出项在 [`PublicIP`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:90) 附近，可以在 Stack 创建完成后看到。

## 3. [`cft_3_s3.yaml`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml)

该模板主要用于创建一个基础 S3 桶，包含：

- 指定唯一桶名
- 开启公共访问阻止
- 设置标签
- 使用 `Retain` 保留策略

注意：[`DeletionPolicy: Retain`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml:15) 表示删除 Stack 时，桶可能不会自动删除，需要手动清理。

---

## 四、完成本实验必须具备的前提

本实验不是纯本地实验，必须有 AWS 账号才能真正完成。

至少需要：

- 一个 AWS 账号
- 可登录 AWS Console
- 有权限使用 CloudFormation、EC2、VPC、IAM、S3
- 在目标区域中存在可用的 EC2 KeyPair

如果没有 AWS 账号，那么目前只能完成代码整理，无法完成实际部署和截图。

---

## 五、还需要确认的关键信息

当前最需要确认的是 [`KeyName`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:4) 默认值是否真实存在。

现在模板里默认写的是：

- `us-east-1-zfs`

如果你的 AWS 账号里没有这个 KeyPair，那么创建 EC2 Stack 时会失败。

解决办法有两种：

1. 直接修改 [`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:9) 的默认值为你真实存在的密钥名
2. 在创建 Stack 时手动输入正确的 KeyPair 名

---

## 六、云上操作详细步骤

这一部分按照你真正操作 AWS 控制台时的顺序来写，尽量做到照着点就能完成。

## 第 1 步：登录 AWS 控制台

打开以下任意地址：

- https://aws.amazon.com/console/
- https://console.aws.amazon.com/

登录后进入 AWS Console 首页。

### 登录后先做 2 件事

#### 1. 看右上角当前区域
你截图里当前区域是：

- `Europe (Stockholm)`

也就是：

- `eu-north-1`

后面你创建的：
- KeyPair
- CloudFormation Stack
- EC2
- S3

最好都在同一个区域内操作。

#### 2. 先不要管首页卡片报错
首页 `Security` 卡片里的报错，不一定影响你做作业。
真正重要的是下面 3 个服务能不能打开：

- CloudFormation
- EC2
- S3

如果这 3 个服务能正常打开，说明作业仍然可以继续。

---

## 第 2 步：确认账号权限是否可用

在顶部搜索框依次搜索：

- `CloudFormation`
- `EC2`
- `S3`

### 判断标准

#### 情况 A：能正常进入服务页面
说明账号基本可用，可以继续做作业。

#### 情况 B：进入服务时出现权限不足、订阅缺失、访问拒绝
说明这个账号可能不支持完成实验。
你需要向老师反馈当前账号不可用。

建议反馈内容：

> 当前 AWS 账号登录后，服务页面出现权限不足或 SubscriptionRequiredException，暂时无法完成 CloudFormation / EC2 / S3 实验，请提供可用实验账号或补充权限。

---

## 第 3 步：检查或创建 EC2 KeyPair

进入 `EC2` 控制台。

左侧菜单找到：

- `Network & Security`
- `Key Pairs`

点击进入后，检查当前区域是否已经存在可用密钥对。

### 如果已经有 KeyPair
记下密钥名，后面创建 EC2 Stack 时使用。

### 如果没有 KeyPair
点击右上角 `Create key pair`，然后：

1. `Name`：输入你自己的密钥名，例如：`zfs-key`
2. `Key pair type`：保持默认 `RSA`
3. `Private key file format`：
   - Windows 常用 `ppk`（适合 PuTTY）
   - 通用建议 `pem`
4. 点击 `Create key pair`
5. 浏览器会自动下载私钥文件，请保存好

### KeyPair 与模板的关系
创建完后，你需要把真实密钥名填入：

- [`KeyName`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:4)

如果你不想改文件，也可以在创建 CloudFormation Stack 时手动输入这个值。

---

## 第 4 步：创建第一个 Stack（VPC）

进入 `CloudFormation` 控制台。

### 具体操作

1. 点击 `Create stack`
2. 选择 `With new resources (standard)`
3. 在 `Specify template` 页面选择 `Upload a template file`
4. 上传文件：[`cft_1_vpc.yaml`](homework/3.NetDevOps/DAY12/cft_1_vpc.yaml)
5. 点击 `Next`

### 填写 Stack 信息

- `Stack name` 建议填写：`EC2VPC`

然后继续下一步。

### 后续页面怎么选
一般保持默认即可：

- `Configure stack options`：默认
- `Advanced options`：默认
- 最后到 `Review` 页面确认

点击：

- `Submit`
- 或 `Create stack`

### 创建成功判断
返回 Stack 列表后，状态会从：

- `CREATE_IN_PROGRESS`

变成：

- `CREATE_COMPLETE`

### 这个 Stack 创建了什么
它会创建：

- VPC
- Internet Gateway
- 子网
- 路由表
- 安全组

并通过 `Outputs` 输出网络资源给 [`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml) 使用。

### 这里建议截图
截图内容：

- Stack 列表中 `EC2VPC` 显示 `CREATE_COMPLETE`
- `Outputs` 页面

---

## 第 5 步：创建第二个 Stack（EC2）

继续在 `CloudFormation` 控制台创建新 Stack。

### 具体操作

1. 点击 `Create stack`
2. 选择 `With new resources (standard)`
3. 上传文件：[`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml)
4. 点击 `Next`

### 填写 Stack name
建议填写：

- `EC2Host`

### 填写参数
在参数页面重点看两个：

#### 1. `KeyName`
这里一定要填你当前区域真实存在的 KeyPair 名。

例如：
- `zfs-key`
- 或你在 EC2 控制台实际看到的名字

#### 2. `NetworkStackName`
这里填写：

- `EC2VPC`

因为 [`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml) 要引用第一个 Stack 导出的子网和安全组。

### 后续页面
保持默认，继续下一步到 Review 页面。

### 很重要：Capabilities 勾选
因为 [`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:22) 会创建 IAM Role，所以在 Review 页面底部通常需要勾选：

- `I acknowledge that AWS CloudFormation might create IAM resources`

如果不勾选，这个 Stack 往往会创建失败。

### 创建成功判断
状态从：

- `CREATE_IN_PROGRESS`

变成：

- `CREATE_COMPLETE`

### 如果失败要看哪里
点击 Stack 进入：

- `Events`

查看哪一个资源失败。
常见失败点：

- KeyPair 不存在
- IAM 权限不足
- 角色名重名
- 导入的网络 StackName 不正确

### 创建成功后要做什么
点击 Stack 的：

- `Outputs`

找到：

- [`PublicIP`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:90)

记下公网 IP，后面 SSH 登录要用。

### 这里建议截图
截图内容：

- Stack 列表中 `EC2Host` 为 `CREATE_COMPLETE`
- `Outputs` 页面中的公网 IP

---

## 第 6 步：创建第三个 Stack（S3）

继续在 `CloudFormation` 控制台创建第三个 Stack。

### 具体操作

1. 点击 `Create stack`
2. 上传文件：[`cft_3_s3.yaml`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml)
3. 点击 `Next`

### 填写 Stack name
建议填写：

- `S3Basic`

### 后续页面
保持默认，直接到 Review 页面，点击创建。

### 创建成功判断
状态变为：

- `CREATE_COMPLETE`

### 如果失败常见原因
最常见的是桶名冲突，也就是：

- [`BucketName`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml:7)

已经被别人占用。

### 桶名冲突怎么改
把：

- `netdevops-s3-basic-2026-zfs`

改成更特殊的名字，例如：

- `netdevops-s3-basic-2026-zfs-001`
- `netdevops-s3-basic-2026-zfs-homework`
- `netdevops-s3-basic-2026-zfs-cloud`

改完重新上传创建即可。

### 这里建议截图
截图内容：

- Stack 列表中 `S3Basic` 为 `CREATE_COMPLETE`

---

## 第 7 步：找到 EC2 公网 IP

方法 1：在 CloudFormation 中看

进入第二个 Stack，点击：

- `Outputs`

查看：

- [`PublicIP`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:90)

方法 2：在 EC2 控制台看

进入 `EC2` 控制台，点击 `Instances`，找到你的实例，在详情页中看：

- `Public IPv4 address`

### 这里建议截图
截图内容：

- EC2 的公网 IP 页面

---

## 第 8 步：SSH 登录 EC2

模板里的 [`UserData`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:61) 已经配置了 root 登录：

- 用户：`root`
- 密码：`Cisc0123`

### 登录方式 1：Linux / macOS / WSL / Git Bash

打开终端执行：

```bash
ssh root@你的公网IP
```

例如：

```bash
ssh root@54.123.45.67
```

第一次连接会提示是否信任主机，输入：

```bash
yes
```

然后输入密码：

```bash
Cisc0123
```

### 登录方式 2：Windows PuTTY

1. 打开 PuTTY
2. 在 `Host Name` 填：公网 IP
3. 端口保持 `22`
4. 点击 `Open`
5. 登录用户名输入：`root`
6. 密码输入：`Cisc0123`

### 如果 SSH 连不上，先检查

1. EC2 是否已经完全启动完成
2. 公网 IP 是否正确
3. 安全组是否开放 22 端口
4. 本地网络是否限制 SSH

安全组放行在 [`cft_1_vpc.yaml`](homework/3.NetDevOps/DAY12/cft_1_vpc.yaml:58) 到 [`cft_1_vpc.yaml`](homework/3.NetDevOps/DAY12/cft_1_vpc.yaml:77) 已经配置了 TCP 22 允许 `0.0.0.0/0`。

### 这里建议截图
截图内容：

- SSH 登录成功后的终端界面

---

## 第 9 步：在 EC2 上执行 S3 桶操作

成功登录后，按老师要求执行以下命令。

### 1. 创建文件

```bash
cat >> upload-test.txt
```

输入：

```bash
test
```

然后按：

- `Ctrl + C`

结束输入。

### 2. 查看文件内容

```bash
cat upload-test.txt
```

正常应看到：

```bash
test
```

### 3. 上传文件到 S3

```bash
aws s3 cp upload-test.txt s3://netdevops-s3-basic-2026-zfs
```

如果你后面改过桶名，这里要同步改成你的真实桶名。

成功时通常会看到类似输出：

```bash
upload: ./upload-test.txt to s3://netdevops-s3-basic-2026-zfs/upload-test.txt
```

### 4. 列出桶内文件

```bash
aws s3 ls s3://netdevops-s3-basic-2026-zfs
```

成功时会显示类似：

```bash
2026-05-12 00:00:00         5 upload-test.txt
```

### 5. 删除文件

```bash
aws s3 rm s3://netdevops-s3-basic-2026-zfs/upload-test.txt
```

成功时会显示类似：

```bash
delete: s3://netdevops-s3-basic-2026-zfs/upload-test.txt
```

### 6. 再次查看桶内容

```bash
aws s3 ls s3://netdevops-s3-basic-2026-zfs
```

如果删除成功，这里应当不再显示 `upload-test.txt`。

### 如果执行 `aws s3` 命令报错怎么办
常见原因：

1. IAM Role 没绑定成功
2. 当前账号没权限访问 S3
3. EC2 没有正确获取 IAM 临时凭证
4. 桶名写错

重点检查：

- [`IamInstanceProfile`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:74)
- [`ManagedPolicyArns`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:34) 中是否包含 S3 权限
- 桶名是否和 [`cft_3_s3.yaml`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml:7) 一致

### 这里建议截图
截图内容：

- 创建文件成功截图
- `cat upload-test.txt` 截图
- `aws s3 cp` 成功截图
- `aws s3 ls` 显示文件截图
- `aws s3 rm` 删除成功截图
- 删除后再次 `aws s3 ls` 截图

---

## 第 10 步：实验结束后删除所有 Stack

老师要求实验结束后删除所有 CloudFormation Stack。

### 推荐删除顺序

1. 先删除 EC2 Stack，例如：`EC2Host`
2. 再删除 S3 Stack，例如：`S3Basic`
3. 最后删除 VPC Stack，例如：`EC2VPC`

### 删除方法

进入 CloudFormation 控制台：

1. 选中对应 Stack
2. 点击 `Delete`
3. 等待状态变成删除完成

### 删除时要注意的点

#### 1. S3 可能删不掉
因为 [`cft_3_s3.yaml`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml:15) 配置了：

- `DeletionPolicy: Retain`

所以删掉 Stack 后，S3 桶可能还保留着。

#### 2. 桶内对象必须为空才能删桶
如果桶中还有文件，需要先进入 S3 控制台：

1. 打开桶
2. 删除桶内全部对象
3. 再删除桶本身

### 这里建议截图
截图内容：

- 删除 Stack 的页面
- 删除成功后的 Stack 列表
- 如有需要，S3 桶手动删除截图

---

## 七、云上操作简版清单

如果你做实验时不想看大段文字，就按下面清单走：

1. 登录 AWS Console
2. 确认区域
3. 打开 EC2 → Key Pairs
4. 检查或创建 KeyPair
5. 打开 CloudFormation
6. 创建 [`cft_1_vpc.yaml`](homework/3.NetDevOps/DAY12/cft_1_vpc.yaml) → StackName 填 `EC2VPC`
7. 创建 [`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml) → `KeyName` 填真实密钥名，`NetworkStackName` 填 `EC2VPC`
8. 勾选 IAM capabilities
9. 创建 [`cft_3_s3.yaml`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml)
10. 查看 EC2 Stack 输出中的 [`PublicIP`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:90)
11. SSH 登录 EC2
12. 执行文件创建、上传、查看、删除 S3 的命令
13. 截图保存
14. 删除 3 个 Stack
15. 手动清理残留 S3 桶

---

## 八、作业需要截图的内容

建议至少保留以下截图：

### 1. CloudFormation 相关截图

- VPC Stack 创建成功截图
- EC2 Stack 创建成功截图
- S3 Stack 创建成功截图

### 2. EC2 输出截图

- EC2 Stack 的 Outputs 页面
- 公网 IP 显示截图

### 3. SSH 登录与 S3 操作截图

- SSH 登录成功截图
- 创建 `upload-test.txt` 截图
- 执行上传命令截图
- 执行 `aws s3 ls` 截图
- 执行删除命令截图
- 删除后再次 `aws s3 ls` 截图

### 4. 删除资源截图

- 删除所有 CloudFormation Stack 的截图
- 如有需要，补充 S3 桶手动清理截图

---

## 九、可能遇到的问题

## 1. KeyPair 不存在

现象：EC2 Stack 创建失败。

原因：[`KeyName`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:4) 填写的密钥对名称在 AWS 账号对应区域不存在。

处理：

- 改成真实的 KeyPair 名
- 或先去 EC2 控制台创建一个新的 KeyPair

## 2. IAM Role 重名

现象：EC2 Stack 创建失败，提示角色名已存在。

可能冲突的位置：

- [`AWS2022WebServiceRole`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:24)
- [`AWS2022WebServiceInstanceProfileName`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:44)

处理：

- 修改为你账号中未使用的新名字

## 3. S3 桶名重复

现象：S3 Stack 创建失败。

原因：[`BucketName`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml:7) 必须全球唯一。

处理：

- 换成更特殊的名字，例如在后面增加日期、姓名缩写、学号等

## 4. SSH 登录失败

可能原因：

- 安全组未放行 22 端口
- EC2 还没完全初始化完成
- 公网 IP 获取错误
- 本地网络限制 SSH 访问

处理：

- 检查 [`cft_1_vpc.yaml`](homework/3.NetDevOps/DAY12/cft_1_vpc.yaml:58) 到 [`cft_1_vpc.yaml`](homework/3.NetDevOps/DAY12/cft_1_vpc.yaml:77) 中的安全组放行配置
- 等待 EC2 启动完成后再登录
- 重新确认 Stack 输出中的公网 IP

## 5. EC2 中执行 `aws s3` 命令失败

可能原因：

- IAM Role 未正确绑定到实例
- 实例权限不足
- 桶名写错
- AWS CLI 环境未就绪

处理：

- 检查 [`IamInstanceProfile`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml:74)
- 检查 IAM 策略中是否包含 S3 权限
- 检查桶名是否与 [`cft_3_s3.yaml`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml:7) 一致

## 6. 删除 Stack 时 S3 删除不掉

原因：[`DeletionPolicy: Retain`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml:15) 会保留桶。

处理：

- 先手动删除桶内对象
- 再手动删除桶

---

## 十、当前结论

目前本次作业的代码部分已经完成，生成了 3 个可用的 CloudFormation 模板：

- [`cft_1_vpc.yaml`](homework/3.NetDevOps/DAY12/cft_1_vpc.yaml)
- [`cft_2_ec2.yaml`](homework/3.NetDevOps/DAY12/cft_2_ec2.yaml)
- [`cft_3_s3.yaml`](homework/3.NetDevOps/DAY12/cft_3_s3.yaml)

同时，文档中也已经补充了更详细的云上操作步骤。

如果你后续拿到可用 AWS 账号，只需要按本文档逐步执行，即可完成本次 CloudFormation 实战作业。