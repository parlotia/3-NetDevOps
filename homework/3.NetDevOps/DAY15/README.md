# DAY15 作业说明（按当前实验环境重写版）

## 1. 原始作业要求

老师这一部分的核心要求，本质上是两件事：

1. 把 NSO + GitLab CI/CD 的自动化流程跑起来
2. 提交能够证明流程成功的代码和截图

从老师上课演示和你前面给的信息来看，DAY15 不是只要“写一个脚本”，而是要把下面这条链路说明清楚：

- GitLab 仓库里有代码
- push 代码后自动触发 pipeline
- pipeline 按步骤去调用 NSO RESTCONF
- NSO 完成 authgroup、devices、sync、config 等动作
- 最终在日志里能看到设备配置步骤的输出

所以这次 README 的目标，不是再讲一遍理论，而是直接告诉你：**按你现在这套代码，应该怎么交作业、截什么图、每一步在当前实验环境里到底代表什么。**

---

## 2. 本次实现方式

这次不是完全照搬老师原版环境，而是按你当前实验环境做了适配，保持“老师五步思路不变”，但把脚本细节改成你现在能跑通的版本。

当前版本的特点是：

- 使用 [`DAY15/code`](homework/3.NetDevOps/DAY15/code) 作为最终提交目录
- pipeline 已经扩展成 **5 个 stage**
- 同时支持 `ci` 和 `cd` 两个分支
- 当前环境只有一台设备 `C8Kv1`
- [`device_config_info.yaml`](homework/3.NetDevOps/DAY15/code/device_config_info.yaml) 同时承载：
  - 设备纳管字段
  - logging 配置字段
- 第 2 步 [`restconf_2_devices.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_2_devices.py) 会真实执行 devices patch
- 但为了规避当前 NSO 返回全量 devices 时的 `ChunkedEncodingError`，第 2 步不再打印全量 devices 查询结果
- 第 4 步 [`restconf_4_config.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_4_config.py) 已回到你最终要求的“第一张图那种简化 logging 输出风格”

也就是说，现在这套代码不是最早那个最小 logging demo，而是：**既保留老师五步结构，又适配你当前单设备实验环境的版本。**

---

## 3. 这次你真正要交的东西

你真正要交的内容，建议分成两部分：

### 3.1 代码部分

提交 [`DAY15/code`](homework/3.NetDevOps/DAY15/code) 目录中的核心文件，至少包括：

- [`.gitlab-ci.yml`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml)
- [`device_config_info.yaml`](homework/3.NetDevOps/DAY15/code/device_config_info.yaml)
- [`restconf_1_authgroup.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_1_authgroup.py)
- [`restconf_2_devices.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_2_devices.py)
- [`restconf_3_sync.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_3_sync.py)
- [`restconf_4_config.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_4_config.py)
- [`module_2_device_2_patch.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_2_device_2_patch.py)
- [`module_2_device_3_sync.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_2_device_3_sync.py)
- [`module_logging.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_logging.py)
- [`module_sync.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_sync.py)
- [`restconf_0_basic_info.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_0_basic_info.py)

### 3.2 截图部分

老师真正容易看的，通常是下面几类图：

- 整个 pipeline 成功页
- [`ci_nso_config`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 的日志图
- 如果要体现五步完整性，再补 [`ci_nso_devices`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 的日志图
- 变量配置页
- 可选：NSO 侧验证结果图

---

## 4. 先准备哪些代码截图

如果老师要求“展示代码”，建议你优先截下面 4 组。

### 4.1 截 [`device_config_info.yaml`](homework/3.NetDevOps/DAY15/code/device_config_info.yaml)

这一张图要体现两件事：

1. 当前环境只有一台设备 `C8Kv1`
2. 这个 YAML 既写了 devices 纳管信息，也写了 logging 配置

建议截图时能看到类似这些字段：

```yaml
devices:
  - name: C8Kv1
    ip: 10.10.1.201
    host_key_verification: none
    authgroup: qytadmin
    protocol: ssh
    ned_id: cisco-ios-cli-3.8
    admin_state: unlocked
    logging:
      host:
        - host: 10.10.1.101
      trap: debugging
```

### 4.2 截 [`module_logging.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_logging.py)

这一张图重点给老师看两点：

- 你是通过 RESTCONF 调设备 logging 路径
- 当前实现不会再故意吞掉真实失败

建议截图重点包含：

- [`get_devices_logging()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_logging.py:30)
- [`push_logging_config()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_logging.py:38)
- [`config_devices_logging()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_logging.py:53)

### 4.3 截 [`module_2_device_2_patch.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_2_device_2_patch.py)

这一张图是这次后期修复的关键证据。

它说明第 2 步不是假输出，而是真的会把 [`device_config_info.yaml`](homework/3.NetDevOps/DAY15/code/device_config_info.yaml) 里的设备地址、authgroup、NED、协议等信息 patch 到 NSO。

建议截图重点包含：

- [`patch_devices()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_2_device_2_patch.py:8)
- PATCH 目标 URL
- `tailf-ncs:device` payload 结构

### 4.4 截 [`restconf_4_config.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_4_config.py)

这一张图是为了说明：你最后已经按要求改回简化 logging 风格。

建议截图时能看到它的执行顺序：

1. 调 [`get_devices_logging()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_logging.py:30)
2. 调 [`config_devices_logging()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_logging.py:53)
3. 调 [`sync_devices()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_2_device_3_sync.py:7)
4. 最后再次读取 logging 结果

---

## 5. 当前脚本的实际执行流程

当前 DAY15 这套脚本已经按现在实验环境调整成“**单设备 + 五步流程 + 简化 logging 展示**”的版本。

其中第 2 步 [`restconf_2_devices.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_2_devices.py) 的实际逻辑是：

1. 先打印设备状态说明，但**不再调用全量 devices 查询**
2. 调用 [`patch_devices()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_2_device_2_patch.py:8) 把 [`device_config_info.yaml`](homework/3.NetDevOps/DAY15/code/device_config_info.yaml) 里的当前实验设备地址真正写回 NSO
3. 这样做是为了修复之前 `nso_devices -> nso_config` 之间的 `connection refused`，同时规避全量查询时出现的 `ChunkedEncodingError`

第 4 步 [`restconf_4_config.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_4_config.py) 的实际逻辑是：

1. 先调用 [`get_devices_logging()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_logging.py:30) 查看设备当前 logging
2. 再调用 [`config_devices_logging()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_logging.py:53) 下发 logging
3. 然后调用 [`sync_devices()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_2_device_3_sync.py:7) 执行同步
4. 最后再次调用 [`get_devices_logging()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_logging.py:30) 查看结果

当前环境只有一台设备，所以 [`device_config_info.yaml`](homework/3.NetDevOps/DAY15/code/device_config_info.yaml) 里只保留了 `C8Kv1`，同时这个文件现在既包含设备纳管字段，也包含 logging 配置字段。

所以 pipeline 里的核心输出风格应该类似：

```text
查看devices状态:
跳过全量 devices 查询（避免 NSO chunked 响应问题）
设备 C8Kv1 准备更新为当前实验地址
配置devices
...
查看devices状态:
设备 C8Kv1 状态: 已按当前实验地址提交到 NSO

查看设备Logging配置:
...
配置Logging
None
同步devices:
...
查看设备Router配置:
...
```

你交作业时，至少要把第 2 步设备纳管成功信息和第 4 步 logging 配置输出这两段日志对应上。

## 6. GitLab 具体操作步骤

这一部分就是你问的重点：**GitLab 到底怎么操作。**

---

### 第 1 步：新建 GitLab 项目，或者进入你已有项目

#### 你要做什么

1. 打开 GitLab Web 页面
2. 如果你还没有项目，就点击 `New project`
3. 创建一个项目，比如可以叫：
   - `netdevops-day15`
4. 如果你已经有项目，就直接进入那个项目

#### 这一页建议截图吗

- 一般不用
- 重点截图在后面的 pipeline 页面

---

### 第 2 步：把 DAY15 代码放进 GitLab 仓库

你现在真正要上传的是 [`DAY15/code`](homework/3.NetDevOps/DAY15/code) 目录里的内容。

注意这套代码已经不是最早的“纯 logging 小样例”，而是当前实验环境可运行的版本，特点包括：

- [`.gitlab-ci.yml`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 已经扩展成 5 个 stage
- 同时支持 `ci` 和 `cd` 两个分支的 job
- [`device_config_info.yaml`](homework/3.NetDevOps/DAY15/code/device_config_info.yaml) 现在是**单设备 `C8Kv1`**
- [`restconf_2_devices.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_2_devices.py) 会真实执行设备 patch，但跳过全量 devices 查询

#### 你要做什么

假设你本地有 git 环境，在终端里进入你的项目目录后执行：

```bash
git init
git remote add origin 你的GitLab仓库地址
git checkout -b ci
git add .
git commit -m "finish day15 nso logging ci"
git push -u origin ci
```

如果你的仓库已经初始化过，只需要：

```bash
git checkout -b ci
git add .
git commit -m "finish day15 nso logging ci"
git push -u origin ci
```

#### 注意

- 你的 [`.gitlab-ci.yml`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 里现在同时有 `ci_*` 和 `cd_*` 两套 job
- 如果你推到 `ci` 分支，会触发 `ci` 这套流水线
- 如果你推到 `cd` 分支，会触发 `cd` 这套流水线
- 如果只是为了交老师要求的截图，**优先推送到 `ci` 分支**，因为 README 后面截图说明都是按 [`ci_nso_config`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 写的

#### 这一步要不要截图

- 通常不用
- 除非老师要求看提交记录

---

### 第 3 步：在 GitLab 里配置 CI/CD Variables

进入你的 GitLab 项目后，依次点击：

- `Settings`
- `CI/CD`
- `Variables`

#### 你要做什么

新增下面 3 个变量：

```text
ci_nso_restconf_base_url=http://10.10.1.205:8080/restconf/data/
ci_nso_username=admin
ci_nso_password=你的实际密码
```

#### 变量解释

- `ci_nso_restconf_base_url`
  - NSO RESTCONF 地址
- `ci_nso_username`
  - 登录 NSO 的用户名
- `ci_nso_password`
  - 登录 NSO 的密码

#### 注意事项

- 名字必须完全一致
- URL 必须是 `http://10.10.1.205:8080/restconf/data/`
- 这里不要写 `https`
- 要带上 `/restconf/data/`
- 如果密码不对，pipeline 很可能报 `access-denied`

#### 这一步建议截图

- 建议截一张 Variables 页面
- 密码可以打码

#### 这张图的作用

- 不是老师硬性要求
- 但它能证明你的 pipeline 为什么可以连到 NSO

---

### 第 4 步：检查 GitLab Runner 是否可用

进入 GitLab 项目的：

- `Build`
- `Runners`

或者在项目设置里看 runner 状态。

#### 你要做什么

- 确认项目有可用 runner
- 确认 runner 能执行 Python3
- 最好确认 runner 有 `netdevops` 这个 tag

因为你的 [`.gitlab-ci.yml`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 写的是：

```yaml
tags:
  - netdevops
```

#### 如果没有这个 tag 会怎么样

- pipeline 会卡住不跑
- job 会显示没有可用 runner

#### 这一步建议截图吗

- 一般不用
- 除非你的 pipeline 起不来，需要保留排障证据

---

### 第 5 步：推送代码后，查看 pipeline 是否自动触发

当你把代码 push 到 `ci` 分支后，GitLab 通常会自动触发 pipeline。

进入：

- `Build`
- `Pipelines`

#### 你要做什么

- 找到最新一次 pipeline
- 看状态是不是运行中/成功
- 点进去看里面有哪些 job

#### 这一步必须截图

- 当 pipeline 成功后，截整个 pipeline 总览页

#### 这一张图对应老师哪条要求

- 对应：**提供整个 pipeline 成功执行的截图**

---

### 第 6 步：点开 [`ci_nso_config`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 看日志

这是最关键的一步。

#### 你要做什么

1. 在 pipeline 页面里，点开 [`ci_nso_config`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml)
2. 查看 job 日志
3. 找到 logging 那一段输出
4. 如果老师也看五步完整链路，可以顺手把前面的 [`ci_nso_devices`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 日志一起保留

你现在脚本设计的目标输出风格是：

```text
查看设备Logging配置:
...
配置Logging
None
同步devices:
...
查看设备Router配置:
...
```

而在当前实验环境里，建议你同时确认前一阶段 [`ci_nso_devices`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 出现了类似下面这段内容：

```text
查看devices状态:
跳过全量 devices 查询（避免 NSO chunked 响应问题）
设备 C8Kv1 准备更新为当前实验地址
配置devices
...
查看devices状态:
设备 C8Kv1 状态: 已按当前实验地址提交到 NSO
```

#### 你必须截什么图

至少截 2 张：

- 图 1：[`ci_nso_config`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) job 成功页
- 图 2：job 日志中 logging 那一段输出

如果你想把“真实修过设备纳管链路”也体现出来，建议再补 1 张：

- 图 3：[`ci_nso_devices`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 日志里设备 patch 成功那一段

#### 这一张图对应老师哪条要求

- 对应：**[`ci_nso_config`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 设备配置步骤，配置 logging 部分的截图**

---

### 第 7 步：如果 pipeline 没触发，怎么处理

#### 你先检查 3 件事

1. 你 push 的是不是 `ci` 分支
2. GitLab 项目里有没有可用 runner
3. [`.gitlab-ci.yml`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 有没有成功提交

#### 典型原因

- 分支不对
- runner 没有 tag
- `.gitlab-ci.yml` 语法有问题
- 项目变量没配好

---

### 第 8 步：如果 job 报错，优先看哪几类问题

#### 常见报错 1：`access-denied`

说明通常是：

- 用户名错了
- 密码错了
- NSO RESTCONF 用户权限不够

优先检查：

- [`ci_nso_username`](homework/3.NetDevOps/DAY15/README.md:295)
- [`ci_nso_password`](homework/3.NetDevOps/DAY15/README.md:296)

#### 常见报错 2：`No connection adapters were found`

这通常说明你变量里的 URL 写错了。

正确格式必须是：

```text
http://10.10.1.205:8080/restconf/data/
```

不要漏掉：

- `http://`
- 端口 `8080`
- `/restconf/data/`

#### 常见报错 3：`unknown element: ipv4-host-list`

这是之前出现过的 NED 数据结构不兼容问题。

原因是当前环境的 IOS NED logging 结构，不接受老师原先那种：

```yaml
host:
  ipv4-host-list:
    - ipv4-host: 10.10.1.205
```

当前环境应该使用：

```yaml
host:
  - host: 10.10.1.101
```

所以如果以后再出现这类报错，优先去检查 [`device_config_info.yaml`](homework/3.NetDevOps/DAY15/code/device_config_info.yaml) 里的 logging 结构。

#### 常见报错 4：job 一直 pending

一般说明不是脚本逻辑问题，而是 runner 问题。

优先检查：

- GitLab Runner 是否在线
- runner 有没有 `netdevops` tag
- 项目有没有绑定到这个 runner

#### 常见报错 5：`ChunkedEncodingError`

这类报错是在查询全量 devices 时出现过的。

当前版本的处理思路不是继续硬读，而是：

- 保留第 2 步真实设备 patch
- 跳过全量 devices 查询输出
- 避开当前实验环境下不稳定的 chunked 响应

所以如果你在 [`restconf_2_devices.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_2_devices.py) 附近再看到类似报错，不要再改回全量查询。

---

### 第 9 步：如果 pipeline 成功，再补一个结果验证图

#### 方法一：NSO CLI 验证

你可以在 NSO 侧确认设备配置是否已经成功下发。

例如验证 logging 时，可以检查：

- 设备是否已经纳管
- `sync-from` 是否成功
- logging host / trap 是否存在

#### 预期结果

至少能证明：

- 设备 `C8Kv1` 已存在于 NSO
- logging 配置已经被下发
- pipeline 日志与 NSO 当前状态一致

#### 这一步要不要截图

- 不是硬性要求
- 但如果老师想看“不是假跑”，这张验证图会很有说服力

---

### 第 10 步：最后整理你真正要交的截图

建议按下面顺序整理：

1. GitLab pipeline 总览成功图
2. [`ci_nso_config`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 成功页
3. [`ci_nso_config`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 日志中 logging 输出图
4. [`ci_nso_devices`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 日志中设备 patch 输出图（建议补）
5. CI/CD Variables 图（建议补）
6. 可选：NSO 验证图

---

## 7. 为什么现在脚本比较适合交作业

相比最早的版本，现在这套脚本更适合交作业，原因很明确：

1. **结构上更接近老师五步要求**
   - 不再只是一个 logging demo
   - 已经补齐 authgroup、devices、sync、config 等阶段

2. **更贴合你现在的实验环境**
   - 当前只有一台设备 `C8Kv1`
   - 设备地址、authgroup、NED 都按当前环境修正过

3. **真正修过 devices → config 的链路问题**
   - 不是靠吞错让 job 继续跑
   - 而是通过 [`patch_devices()`](homework/3.NetDevOps/DAY15/code/nso_restconf/module_2_device_2_patch.py:8) 把设备地址重新写回 NSO

4. **规避了当前环境里的不稳定点**
   - 不再依赖全量 devices 查询
   - 规避了 `ChunkedEncodingError`

5. **日志风格又回到了你最终要的简单版本**
   - [`restconf_4_config.py`](homework/3.NetDevOps/DAY15/code/nso_restconf/restconf_4_config.py) 现在保留的是简化 logging 输出
   - 更适合直接截图交作业

---

## 8. 当前结论

到目前为止，这套 DAY15 内容已经可以按“老师五步流程 + 当前单设备实验环境”的思路来交。

你在最终提交时，重点抓住下面三件事就够了：

1. 代码目录提交 [`DAY15/code`](homework/3.NetDevOps/DAY15/code)
2. 截图重点放在 pipeline 总览、[`ci_nso_config`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 日志、[`ci_nso_devices`](homework/3.NetDevOps/DAY15/code/.gitlab-ci.yml) 日志
3. 说明当前版本已经真实修复过设备纳管链路，并针对 chunked 查询问题做了环境适配

按这份 README 去整理材料，逻辑会比之前更完整，也更符合你现在实际跑出来的结果。
