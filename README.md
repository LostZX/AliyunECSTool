# 阿里云ECS管理工具

一个阿里云ECS实例管理命令行工具，提供交互式界面，支持查询账户余额、创建和删除ECS实例等多种操作。

## 功能特点

- **账户余额查询**：随时了解您的阿里云账户余额
- **ECS实例管理**：
  - 创建ECS实例：交互式向导、模板创建ECS实例
  - 删除ECS实例：安全地删除不再需要的实例
  - 查询ECS状态：实时监控实例运行状态
  - 查询ECS详细信息：获取实例的详细配置信息
  - 查询所有ECS实例：列出账户指定区域下所有实例
- **资源查询**：
  - 查询实例规格列表：了解可用的实例类型和配置
  - 查询模板信息：使用模板快速创建实例
  - 查询ECS价格：获取实例的价格信息

## 系统要求

- Python 3.6 或更高版本

## 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装以下依赖：

```bash
pip install alibabacloud_tea_openapi>=0.3.7
pip install alibabacloud_ecs20140526>=7.0.4
pip install alibabacloud_tea_util>=0.3.8
pip install alibabacloud_bssopenapi20171214>=1.0.5
pip install alibabacloud_vpc20160428>=2.0.20
pip install pyyaml>=5.4.1
pip install prettytable>=2.1.0
```

## 配置文件

在项目根目录下创建`config.yml`文件，内容如下：

```yaml
# 阿里云ECS管理工具配置文件

# 注意 !! region_id 最好改为你常用的区域，因为下面申请机器v_switch_id 和 sercurity_group_id 没有写创建逻辑（有空再写），只能从设置的region中查询已存在的，如果一定要用指定区域，建议手动创建虚拟交换机和安全组

# 注意accesskey权限

# 阿里云访问密钥配置
aliyun:
  # 您的AccessKey ID
  access_key_id: 您的AccessKeyID
  # 您的AccessKey Secret
  access_key_secret: 您的AccessKeySecret
  # 默认区域ID
  region_id: cn-hangzhou
```

请将`您的AccessKeyID`和`您的AccessKeySecret`替换为您的阿里云账号的AccessKey信息。

```yaml
# 配置默认实例

# 注意 抢占实例默认需要阿里云账户余额 > 100才能使用，测试抢占实例以下面的配置1小时4毛钱,同配置同带宽比按量付费便宜一半

# 建议使用模板来创建实例，更方便快捷

instance:
  # 计费类型 PayByBandwidth 固定带宽 PayByTraffic 按量付费
  internet_charge_type: "PayByBandwidth"
  resource_type: "instance"
  # 镜像类型
  image_id: "ubuntu_20_04_x64_20G_alibase_20250625.vhd"
  # 规格，该规格为4vCPU 8.0GiB
  # 更多参考 https://ecs-buy.aliyun.com/ecs?spm=5176.ecscore_overview.home-res.buy.450e4df5lRugrm#/custom/prepay/cn-hangzhou?orderSource=buyWizard-console-overview
  # 或 执行 instance_type命令，当然不如参考阿里云创建实例页面更直观
  instance_type: "ecs.e-c1m2.xlarge"
  instance_name: "balala"
  # 最大带宽
  internet_max_bandwidth_out: 5
  # 这个要修改为自己的虚拟交换机id
  v_switch_id: "vsw-"
  # 这个要修改为自己的安全组id
  security_group_id: "sg-"
  # 磁盘大小
  system_disk_size: 40
  # 磁盘类型
  # 更多参考 https://ecs-buy.aliyun.com/ecs?spm=5176.ecscore_overview.home-res.buy.450e4df5lRugrm#/custom/prepay/cn-hangzhou?orderSource=buyWizard-console-overview
  system_disk_category: "cloud_essd_entry"
  # 实例的付费方式 按量付费
  instance_charge_type: "PostPaid"
  # 竞价策略 自动出价
  # 更多参考 https://ecs-buy.aliyun.com/ecs?spm=5176.ecscore_overview.home-res.buy.450e4df5lRugrm#/custom/prepay/cn-hangzhou?orderSource=buyWizard-console-overview
  spot_strategy: "SpotAsPriceGo"
  # 抢占式实例的保留时长 0为不确定时常，会一直存在，需要手动注销， 1为保留一小时，实例在所设定时间内不会释放，超过所设定时间后每5分钟监测库存、出价的变化，进而判断是否能够继续使用资源
  spot_duration: 0
  # ssh密码，修改为自己的
  password: "123456@qax"
  # 实例数量
  amount: 1
  host_name: "vps"
```

## 使用方法

运行以下命令启动工具：

```bash
python main.py
```

### 可用命令

- **create**：创建新的ECS实例
- **delete**：删除指定的ECS实例，用法：`delete instance_id`
- **balance**：查询账户余额
- **status**：查询ECS状态，用法：`status instance_id`
- **query**：查询ECS信息，用法：`query instance_id`
- **instances**：查询所有ECS实例
- **instance_type**：查询实例规格列表
- **templates**：查询模板信息
- **price**：查询ECS价格
- **help**：显示帮助信息
- **exit/quit**：退出程序

## 注意事项

1. 作者只测试了创建单个主机，如果需要创建多个，照理来说应该可以创建起来，只是没处理返回值
2. 请妥善保管您的AccessKey信息，不要将其泄露给他人
3. 创建实例前，请确保账户有足够的余额
4. 删除实例操作不可恢复，请谨慎操作
5. 如遇到API调用错误，请检查网络连接和AccessKey是否有效