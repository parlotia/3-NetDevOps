# NetDevOps 第14天作业：安装 NSO，测试创建 SYSLOG 的 RESTCONF

## 1. 作业目标

本次作业需要完成以下三部分内容：

1. 安装 CI/CD 场景中的 NSO 控制器，并提供登录页面截图。
2. 使用 NSO 控制器 CLI 配置 SYSLOG，包括 server IP 和 trap level，并提供详细操作步骤。
3. 使用 RESTCONF 对 SYSLOG 配置进行获取与创建测试，并提供“成功”部分的详细截图。

> 当前工作区中没有现成的 NSO 安装记录文件，因此本作业文档采用“可直接提交的实验报告模板 + 结合你当前已有截图进行整理”的方式输出。你已经提供了一张 APIFOX 成功调用截图，可直接作为 RESTCONF 成功截图的一部分插入本文档。

---

## 2. NSO 安装与登录页面截图

### 2.1 安装环境说明

建议在课堂提供的 CI/CD 实验环境中完成 NSO 安装，常见环境如下：

- Linux 主机或虚拟机
- 已安装 Java 运行环境
- 已获得 Cisco NSO 安装包
- 已具备浏览器访问 Web UI 的条件

### 2.2 典型安装步骤

以下步骤可作为作业中“安装过程”的标准写法。

#### 第一步：上传并解压 NSO 安装包

```bash
ls
mkdir -p nso_lab
cp nso-*.linux.x86_64.installer.bin ./nso_lab/
cd nso_lab
chmod +x nso-*.linux.x86_64.installer.bin
./nso-*.linux.x86_64.installer.bin --local-install ./nso-runtime
```

#### 第二步：进入 NSO 运行目录并加载环境变量

```bash
cd ./nso-runtime
source ./ncsrc
```

#### 第三步：创建运行目录并启动 NSO

```bash
ncs-setup --dest .
ncs
```

如果是首次初始化，也可能使用如下命令：

```bash
ncs --with-package-reload
```

#### 第四步：检查 NSO 进程状态

```bash
ncs --status
```

如果状态正常，通常会看到 NSO 已启动的提示信息。

#### 第五步：访问 NSO Web 页面

在浏览器中访问类似地址：

```text
http://<NSO_IP>:8080
```

或者：

```text
https://<NSO_IP>:8888
```

> 具体端口以课堂环境为准。若老师课堂中使用的是 Web UI 登录页，则截图时应包含浏览器地址栏、登录框、以及 NSO 标识信息。

### 2.3 登录页面截图要求

建议截图内容至少包含以下信息：

1. 浏览器访问 NSO 登录页面。
2. 页面上可见用户名/密码输入框。
3. 页面标题或标签中可见 NSO 字样。
4. 如果已登录成功，也可补充一张进入 NSO 后台首页的截图。

### 2.4 作业中可直接使用的说明文字

可在作业中写为：

> 按照上课步骤，在 CI/CD 实验环境中完成 NSO 控制器安装。安装完成后，通过浏览器访问 NSO 控制器登录页面，确认 Web 服务正常。提交作业时附上 NSO 登录页面截图，证明 NSO 控制器已成功安装并可访问。

---

## 3. 使用 NSO CLI 配置 SYSLOG

### 3.1 配置目标

通过 NSO CLI 为受管设备下发 SYSLOG 配置，至少包括：

- SYSLOG 服务器地址
- trap level

本次示例使用如下参数：

- SYSLOG Server IP：`10.10.1.205`
- Trap Level：`informational`

> 如果你课堂实际使用的是其他地址或级别，请按你的实验值替换。

### 3.2 登录 NSO CLI

进入 NSO 安装目录后，执行：

```bash
source ./ncsrc
ncs_cli -u admin
```

登录后进入 NSO CLI。

### 3.3 查看设备是否已纳管

在 NSO CLI 中先确认设备已经存在：

```cli
show devices list
```

如果设备已经被 NSO 管理，应能看到类似设备名，例如：

```text
devices device csr1
devices device r1
devices device iosxe1
```

### 3.4 进入配置模式

```cli
config
```

### 3.5 配置 SYSLOG 服务器与 trap level

如果设备是 IOS XE，典型思路是在设备配置树下增加 logging 配置。课堂环境中常见写法如下：

```cli
devices device <设备名> config ios:logging host 10.10.1.205
devices device <设备名> config ios:logging trap informational
```

如果你的设备名为 `csr1`，则可写成：

```cli
devices device csr1 config ios:logging host 10.10.1.205
devices device csr1 config ios:logging trap informational
```

### 3.6 提交配置

```cli
commit
```

如果需要更清楚展示提交过程，也可先执行：

```cli
commit dry-run outformat native
commit
```

这样在作业截图中可以同时展示：

1. NSO 计划下发的原生命令
2. 提交成功结果

### 3.7 校验 NSO 中的配置

```cli
show running-config devices device csr1 config ios:logging
```

预期可看到类似结果：

```text
host 10.10.1.205
trap informational
```

### 3.8 同步设备配置

为了保证 NSO 与设备配置一致，可执行：

```cli
devices sync-from
```

或者仅对单台设备执行：

```cli
devices device csr1 sync-from
```

### 3.9 作业可直接写入的操作步骤

可整理为以下格式：

1. 使用 [`ncs_cli`](homework/3.NetDevOps/DAY14_NSO_SYSLOG作业.md:103) 登录 NSO 控制器。
2. 通过 [`show devices list`](homework/3.NetDevOps/DAY14_NSO_SYSLOG作业.md:113) 确认目标设备已被 NSO 纳管。
3. 进入配置模式 [`config`](homework/3.NetDevOps/DAY14_NSO_SYSLOG作业.md:123)。
4. 在设备配置树中下发 SYSLOG 服务器地址和 trap level。
5. 执行 [`commit`](homework/3.NetDevOps/DAY14_NSO_SYSLOG作业.md:147) 提交配置。
6. 执行 [`show running-config devices device csr1 config ios:logging`](homework/3.NetDevOps/DAY14_NSO_SYSLOG作业.md:160) 验证配置已存在。
7. 如有需要，执行 [`devices sync-from`](homework/3.NetDevOps/DAY14_NSO_SYSLOG作业.md:172) 做配置同步。

### 3.10 CLI 截图建议

建议最少提供以下 4 张截图：

1. NSO CLI 登录成功截图
2. 配置 SYSLOG 命令截图
3. `commit` 成功截图
4. `show running-config` 验证截图

---

## 4. RESTCONF 获取与创建 SYSLOG 测试

这一部分可以结合你当前已有的 APIFOX 截图来完成。

从现有项目文件中，可以复用两份材料：

- RESTCONF 接口集合 [`NetDevOps_RESTCONF_Collection.json`](homework/3.NetDevOps/DAY7/NetDevOps_RESTCONF_Collection.json)
- Python 测试脚本 [`task3_conf_syslog.py`](homework/3.NetDevOps/DAY7/task3_conf_syslog.py)

其中，接口集合已经给出了获取和配置 SYSLOG 的 RESTCONF URL 与 JSON body；脚本中也明确展示了 PUT 与 GET 的写法。

### 4.1 RESTCONF 前提条件

在目标 IOS XE 设备上先启用 HTTPS 与 RESTCONF。你可以参考已有文档中的命令：

```cisco
conf t
ip http secure-server
restconf
end
write memory
```

这部分内容可参考已有实验文档 [`环境准备与路由器配置.md`](homework/3.NetDevOps/DAY13/code/环境准备与路由器配置.md:72)。

### 4.2 测试参数

根据 [`NetDevOps_RESTCONF_Collection.json`](homework/3.NetDevOps/DAY7/NetDevOps_RESTCONF_Collection.json:8) 中的变量，当前实验参数可写为：

- 设备 IP：`10.10.1.200`
- 用户名：`admin`
- 密码：`Cisc0123`
- SYSLOG 服务器：`10.10.1.205`
- severity：`7`

### 4.3 创建 SYSLOG 配置的 RESTCONF 测试

#### 请求方法

```text
PUT
```

#### URL

```text
https://10.10.1.200/restconf/data/Cisco-IOS-XE-native:native/logging
```

该路径可见于 [`NetDevOps_RESTCONF_Collection.json`](homework/3.NetDevOps/DAY7/NetDevOps_RESTCONF_Collection.json:186) 与 [`conf_syslog()`](homework/3.NetDevOps/DAY7/task3_conf_syslog.py:14)。

#### Headers

```text
Content-Type: application/yang-data+json
Accept: application/yang-data+json
Authorization: Basic admin/Cisc0123
```

对应脚本实现见 [`task3_conf_syslog.py`](homework/3.NetDevOps/DAY7/task3_conf_syslog.py:29)。

#### Body

```json
{
  "Cisco-IOS-XE-native:logging": {
    "trap": {
      "severity": 7
    },
    "hostip": "10.10.1.205"
  }
}
```

对应接口定义见 [`NetDevOps_RESTCONF_Collection.json`](homework/3.NetDevOps/DAY7/NetDevOps_RESTCONF_Collection.json:178)。

#### 成功判定

根据脚本 [`conf_syslog()`](homework/3.NetDevOps/DAY7/task3_conf_syslog.py:55)，RESTCONF PUT 成功通常返回：

```text
204 No Content
```

因此作业中应重点截图以下信息：

1. 请求方法为 PUT
2. 请求 URL 正确
3. Body 中包含 `hostip` 与 `severity`
4. 返回状态码为 `204` 或明确显示 success

### 4.4 获取 SYSLOG 配置的 RESTCONF 测试

#### 请求方法

```text
GET
```

#### URL

```text
https://10.10.1.200/restconf/data/Cisco-IOS-XE-native:native/logging
```

对应接口定义见 [`NetDevOps_RESTCONF_Collection.json`](homework/3.NetDevOps/DAY7/NetDevOps_RESTCONF_Collection.json:228) 与函数 [`verify_syslog()`](homework/3.NetDevOps/DAY7/task3_conf_syslog.py:82)。

#### Header

```text
Accept: application/yang-data+json
Authorization: Basic admin/Cisc0123
```

#### 预期返回

成功时，返回 JSON 中应包含：

```json
{
  "Cisco-IOS-XE-native:logging": {
    "trap": {
      "severity": 7
    },
    "hostip": "10.10.1.205"
  }
}
```

脚本中对返回字段的提取见 [`verify_syslog()`](homework/3.NetDevOps/DAY7/task3_conf_syslog.py:111)。

### 4.5 使用 APIFOX 操作的详细步骤

根据你已经提供的截图，可将操作过程整理为如下步骤：

#### 步骤 1：新建或打开 APIFOX 项目

打开 APIFOX，进入 NSO 或 RESTCONF 测试项目。

#### 步骤 2：新建 SYSLOG 创建接口

- 方法选择 `PUT`
- URL 填写：

```text
/restconf/data/Cisco-IOS-XE-native:native/logging
```

- Header 添加：

```text
Content-Type: application/yang-data+json
Accept: application/yang-data+json
```

- 认证方式选择 Basic Auth，填写用户名密码。

#### 步骤 3：填写 Body

选择 JSON，填写：

```json
{
  "Cisco-IOS-XE-native:logging": {
    "trap": {
      "severity": 7
    },
    "hostip": "10.10.1.205"
  }
}
```

#### 步骤 4：运行并截图“成功”

点击运行后，截图必须保留以下区域：

1. 左侧接口树
2. 中间请求方法与 URL
3. Header 或 Body 参数
4. 右侧/下方返回结果
5. 状态码成功标识

你当前提供的截图已经满足“接口树 + 成功标记”的一部分要求，可以作为 [`DAY14_NSO_SYSLOG作业.md`](homework/3.NetDevOps/DAY14_NSO_SYSLOG作业.md) 中“RESTCONF 成功截图 1”。

#### 步骤 5：新建 SYSLOG 获取接口

- 方法选择 `GET`
- URL 与创建接口相同：

```text
/restconf/data/Cisco-IOS-XE-native:native/logging
```

- Header 添加：

```text
Accept: application/yang-data+json
```

#### 步骤 6：运行 GET 并截图“成功”

返回结果中应能看到：

- `hostip`
- `trap`
- `severity`

如果 APIFOX 中显示绿色成功状态、HTTP 200，以及 JSON 返回体，即可作为“获取成功”的证据截图。

### 4.6 命令行方式补充说明

除了 APIFOX，也可以用 Python 脚本 [`task3_conf_syslog.py`](homework/3.NetDevOps/DAY7/task3_conf_syslog.py) 做补充验证。

脚本执行逻辑为：

1. 调用 [`conf_syslog()`](homework/3.NetDevOps/DAY7/task3_conf_syslog.py:14) 发送 PUT 请求创建 SYSLOG。
2. 调用 [`verify_syslog()`](homework/3.NetDevOps/DAY7/task3_conf_syslog.py:82) 发送 GET 请求验证 SYSLOG。

如需命令行执行，可使用：

```bash
python3 homework/3.NetDevOps/DAY7/task3_conf_syslog.py
```

成功输出一般会包含：

```text
RESTCONF SYSLOG配置测试
--- 配置SYSLOG ---
配置结果: 成功
--- 验证SYSLOG配置 ---
trap severity: 7
syslog server: 10.10.1.205
```

---

## 5. 截图整理建议

为了满足“提供相应部分的操作步骤或截图”的评分要求，建议最终提交材料按下面顺序排版：

### 5.1 第一部分：NSO 安装

1. NSO 安装命令执行截图
2. NSO 启动成功截图
3. NSO 登录页面截图

### 5.2 第二部分：NSO CLI 配置 SYSLOG

1. NSO CLI 登录截图
2. 查看设备列表截图
3. 下发 SYSLOG 命令截图
4. `commit` 成功截图
5. `show running-config` 验证截图

### 5.3 第三部分：RESTCONF 创建与获取 SYSLOG

1. APIFOX 中 PUT 创建 SYSLOG 成功截图
2. APIFOX 中 GET 获取 SYSLOG 成功截图
3. 如果老师要求更详细，可额外补充 Header、Body、返回 JSON 细节截图

---

## 6. 可直接提交的作业总结

下面这段文字可以直接作为你作业最后的总结：

> 本次实验按照课堂步骤完成了 NSO 控制器安装，并确认可以正常访问登录页面。随后通过 NSO CLI 对受管设备下发 SYSLOG 配置，成功配置了 SYSLOG server IP 和 trap level。最后使用 RESTCONF 对 SYSLOG 配置进行了创建与获取测试，PUT 创建请求成功，GET 获取请求返回了正确的 logging 配置数据，证明 NSO/设备侧的 SYSLOG 配置能够通过接口方式完成自动化管理。

---

## 7. 已有材料与可复用依据

本报告整理时参考了当前工作区中已有的 RESTCONF 练习文件：

- 接口集合 [`NetDevOps_RESTCONF_Collection.json`](homework/3.NetDevOps/DAY7/NetDevOps_RESTCONF_Collection.json)
- SYSLOG 测试脚本 [`task3_conf_syslog.py`](homework/3.NetDevOps/DAY7/task3_conf_syslog.py)
- RESTCONF 前提配置参考 [`环境准备与路由器配置.md`](homework/3.NetDevOps/DAY13/code/环境准备与路由器配置.md:72)

如果你要正式上交，建议把老师要求的真实截图插入到本文档各小节下面，再导出为 PDF。