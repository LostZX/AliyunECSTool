from alibabacloud_tea_openapi.models import Config
from alibabacloud_ecs20140526.client import Client as EcsClient
from alibabacloud_bssopenapi20171214.client import Client as BssClient
from alibabacloud_vpc20160428.client import Client as VpcClient
from alibabacloud_ecs20140526 import models as ecs_models
from alibabacloud_tea_util import models as util_models
from Tea.exceptions import UnretryableException, TeaException
import json


class AliyunAPI:
    """
    阿里云API封装类 (使用阿里云SDK V2.0)
    """

    # 单例实例存储
    _instance = None

    def __new__(cls, access_key_id, access_key_secret):
        """创建单例实例"""
        if cls._instance is None:
            cls._instance = super(AliyunAPI, cls).__new__(cls)

            # 初始化实例变量
            cls._instance.access_key_id = access_key_id
            cls._instance.access_key_secret = access_key_secret
            cls._instance.region_id = "cn-hangzhou"  # 默认区域

            # 初始化各种客户端
            cls._instance._initialize_clients()

        return cls._instance

    @classmethod
    def get_instance(cls):
        """静态方法获取单例实例"""
        if cls._instance is None:
            raise RuntimeError("阿里云API实例尚未初始化，请先使用构造函数创建实例")
        return cls._instance

    def _initialize_clients(self):
        """初始化各种阿里云服务客户端"""
        try:
            # 初始化ECS客户端
            ecs_config = Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
                endpoint=f"ecs.{self.region_id}.aliyuncs.com",
            )
            self.ecs_client = EcsClient(ecs_config)

            # 初始化BSS客户端
            bss_config = Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
                endpoint="business.aliyuncs.com",
            )
            self.bss_client = BssClient(bss_config)

            # 初始化VPC客户端
            vpc_config = Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
                endpoint=f"vpc.{self.region_id}.aliyuncs.com",
            )
            self.vpc_client = VpcClient(vpc_config)

        except Exception as e:
            raise Exception(f"\033[1;31m初始化阿里云API客户端失败: {e}\033[0m")

    def set_region(self, region_id):
        """
        设置区域
        """
        if not region_id:
            print("\033[1;31m区域ID不能为空，使用默认区域: cn-hangzhou\033[0m")
            region_id = "cn-hangzhou"

        try:
            self.region_id = region_id

            # 更新ECS客户端
            ecs_config = Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
                endpoint=f"ecs.{region_id}.aliyuncs.com",
            )
            self.ecs_client = EcsClient(ecs_config)

            # 更新VPC客户端
            vpc_config = Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
                endpoint=f"vpc.{region_id}.aliyuncs.com",
            )
            self.vpc_client = VpcClient(vpc_config)

            return True
        except Exception as e:
            print(f"\033[1;31m设置区域失败: {e}\033[0m")
            return False

    def get_describe_regions(self):
        """
        查询地域列表
        """
        try:
            # 创建请求对象

            describe_regions_request = ecs_models.DescribeRegionsRequest(
                instance_charge_type="",
                resource_type="instance",
                accept_language="zh-CN",
            )

            # 设置运行时参数
            runtime = util_models.RuntimeOptions()

            # 发起调用
            response = self.ecs_client.describe_regions_with_options(
                describe_regions_request, runtime
            )

            if (
                response
                and response.body
                and response.body.regions
                and response.body.regions.region
            ):
                # 构造与旧版API相同格式的返回结果
                result = {
                    "Regions": {"Region": []},
                    "RequestId": response.body.request_id,
                }

                for region in response.body.regions.region:
                    result["Regions"]["Region"].append(
                        {
                            "RegionId": region.region_id,
                            "LocalName": region.local_name,
                            "RegionEndpoint": region.region_endpoint,
                        }
                    )
                return result
            else:
                print(f"\033[1;31m查询地域列表返回数据格式异常\033[0m")
                return None
        except TeaException as e:
            print(f"\033[1;31m服务器错误: {e.code} - {e.message}\033[0m")
            return None
        except UnretryableException as e:
            print(f"\033[1;31m客户端错误: {e}\033[0m")
            return None
        except Exception as e:
            print(f"\033[1;31m查询地域列表失败: {e}\033[0m")
            return None

    def get_describe_price(
        self,
        RegionId=None,
        ImageId=None,
        InstanceType=None,
        InternetMaxBandwidthOut=5,
        SystemDiskCategory="cloud_essd_entry",
        SystemDiskSize=40,
        SpotStrategy="SpotAsPriceGo",
        SpotDuration=0,
        InternetChargeType="PayByBandwidth",
        ResourceType="instance",
        Amount=1,
    ):

        system_disk = ecs_models.DescribePriceRequestSystemDisk(
            category=SystemDiskCategory, size=SystemDiskSize
        )
        describe_price_request = ecs_models.DescribePriceRequest(
            region_id=RegionId if RegionId else self.region_id,
            image_id=ImageId,
            instance_type=InstanceType,
            system_disk=system_disk,
            internet_max_bandwidth_out=InternetMaxBandwidthOut,
            spot_strategy=SpotStrategy,
            spot_duration=SpotDuration,
            internet_charge_type=InternetChargeType,
            resource_type=ResourceType,
            amount=Amount,
        )

        runtime = util_models.RuntimeOptions()
        response = self.ecs_client.describe_price_with_options(
            describe_price_request, runtime
        )

        # 安全提取总价
        total_price = (
            getattr(response.body.price_info.price, "trade_price", 0.0)
            if hasattr(response.body, "price_info")
            else 0.0
        )

        # 安全提取明细
        component_prices = []
        if (
            hasattr(response.body, "price_info")
            and hasattr(response.body.price_info.price, "detail_infos")
            and hasattr(response.body.price_info.price.detail_infos, "detail_info")
        ):

            for detail in response.body.price_info.price.detail_infos.detail_info:
                component_prices.append(
                    {
                        "resource": getattr(detail, "resource", "unknown"),
                        "trade_price": getattr(detail, "trade_price", 0.0),
                    }
                )

        # 安全提取描述
        descriptions = []
        if (
            hasattr(response.body, "price_info")
            and hasattr(response.body.price_info, "rules")
            and hasattr(response.body.price_info.rules, "rule")
        ):

            for rule in response.body.price_info.rules.rule:
                if hasattr(rule, "description"):
                    descriptions.append(rule.description)

        # 资源类型中英对照
        resource_map = {
            "instanceType": "实例规格",
            "bandwidth": "网络带宽",
            "image": "系统镜像",
            "systemDisk": "系统磁盘",
            "dataDisk": "数据磁盘",
            "snapshot": "磁盘快照",
        }

        # 构建组件价格明细字符串
        components_lines = []
        for comp in component_prices:
            resource_name = resource_map.get(comp["resource"], comp["resource"])
            # 格式化价格：保留有效小数位
            price_value = comp["trade_price"]
            price_str = f"{price_value:.5f}".rstrip("0").rstrip(".")
            if price_str.endswith("."):
                price_str = price_str[:-1]
            components_lines.append(f"    ├─ {resource_name}: {price_str} 元")

        # 构建优惠描述字符串
        discount_text = (
            "\n".join([f"    • {desc}" for desc in descriptions])
            if descriptions
            else "    • 无额外优惠"
        )

        # 格式化总价
        total_str = f"{total_price:.5f}".rstrip("0").rstrip(".")
        if total_str.endswith("."):
            total_str = total_str[:-1]

        # 构建最终输出
        return (
            "📊 服务器价格明细报告\n"
            "=======================\n"
            "💳 总费用: {} 元\n\n"
            "🧾 费用明细:\n"
            "{}\n"
            "    └─ 合计: {} 元\n\n"
            "🎁 优惠信息:\n"
            "{}"
        ).format(
            total_str,
            "\n".join(components_lines) if components_lines else "    (无明细信息)",
            total_str,
            discount_text,
        )

    def get_describe_security_groups(self, region_id=None):
        """
        查询安全组列表
        """
        try:
            # 创建请求对象
            request = ecs_models.DescribeSecurityGroupsRequest(
                region_id=region_id if region_id else self.region_id
            )

            # 设置运行时参数
            runtime = util_models.RuntimeOptions()

            # 发起调用
            response = self.ecs_client.describe_security_groups_with_options(
                request, runtime
            )

            if (
                response
                and response.body
                and response.body.security_groups
                and response.body.security_groups.security_group
            ):
                # 构造与旧版API相同格式的返回结果
                result = {
                    "SecurityGroups": {"SecurityGroup": []},
                    "RequestId": response.body.request_id,
                    "TotalCount": response.body.total_count,
                    "PageNumber": response.body.page_number,
                    "PageSize": response.body.page_size,
                }

                for sg in response.body.security_groups.security_group:
                    sg_info = {
                        "SecurityGroupId": sg.security_group_id,
                        "SecurityGroupName": sg.security_group_name,
                        "Description": sg.description,
                        "VpcId": sg.vpc_id,
                        "CreationTime": sg.creation_time,
                        "SecurityGroupType": (
                            sg.security_group_type
                            if hasattr(sg, "security_group_type")
                            else ""
                        ),
                    }
                    result["SecurityGroups"]["SecurityGroup"].append(sg_info)

                return result
            else:
                print(f"\033[1;31m查询安全组列表返回数据格式异常\033[0m")
                return None
        except TeaException as e:
            print(f"\033[1;31m服务器错误: {e.code} - {e.message}\033[0m")
            return None
        except UnretryableException as e:
            print(f"\033[1;31m客户端错误: {e}\033[0m")
            return None
        except Exception as e:
            print(f"\033[1;31m查询安全组列表失败: {e}\033[0m")
            return None

    def get_describe_instance_types(self):
        """
        查询ECS实例规格列表
        :param region_id: 地域ID (可选)
        :param next_token: 分页令牌 (可选)
        :param max_results: 每页最大条目数 (默认100)
        """
        try:
            # 创建请求对象
            request = ecs_models.DescribeInstanceTypesRequest()

            # 设置运行时参数
            runtime = util_models.RuntimeOptions()

            # 发起调用
            response = self.ecs_client.describe_instance_types_with_options(
                request, runtime
            )

            if response and response.body:
                # 构造返回结果
                result = {
                    "request_id": response.body.request_id,
                    "next_token": response.body.next_token,
                    "instance_types": [],
                }

                # 处理实例规格列表
                if (
                    response.body.instance_types
                    and response.body.instance_types.instance_type
                ):
                    for instance_type in response.body.instance_types.instance_type:
                        result["instance_types"].append(
                            {
                                "InstanceTypeId": instance_type.instance_type_id,
                                "CpuCoreCount": instance_type.cpu_core_count,
                                "MemorySize": f"{instance_type.memory_size} GiB",
                                "GPUAmount": getattr(instance_type, "gpu_amount", 0),
                                "GPUSpec": getattr(instance_type, "gpu_spec", "N/A"),
                                "LocalStorageCategory": getattr(
                                    instance_type, "local_storage_category", "cloud"
                                ),
                                "LocalStorageAmount": getattr(
                                    instance_type, "local_storage_amount", 0
                                ),
                                "LocalStorageSize": f"{getattr(instance_type, 'local_storage_size', 0)} GiB",
                                "NetworkCardQuantity": instance_type.eni_quantity,
                                "EniPrivateIpAddressQuantity": instance_type.eni_private_ip_address_quantity,
                                "InstanceTypeFamily": instance_type.instance_type_family,
                            }
                        )

                return result
            else:
                print(f"\033[1;31m查询实例规格返回数据格式异常\033[0m")
                return None
        except TeaException as e:
            print(f"\033[1;31m服务器错误: {e.code} - {e.message}\033[0m")
            return None
        except UnretryableException as e:
            print(f"\033[1;31m客户端错误: {e}\033[0m")
            return None
        except Exception as e:
            print(f"\033[1;31m查询实例规格失败: {e}\033[0m")
            return None

    def get_describe_launch_templates(self, region_id=None):
        """
        查询启动模板列表
        :param region_id: 地域ID (可选)
        """
        try:
            # 创建请求对象
            request = ecs_models.DescribeLaunchTemplatesRequest(
                region_id=region_id if region_id else self.region_id
            )

            # 设置运行时参数
            runtime = util_models.RuntimeOptions()

            # 发起调用
            response = self.ecs_client.describe_launch_templates_with_options(
                request, runtime
            )

            if response and response.body:
                # 构造返回结果
                result = {
                    "request_id": response.body.request_id,
                    "total_count": response.body.total_count,
                    "page_number": response.body.page_number,
                    "page_size": response.body.page_size,
                    "launch_templates": [],
                }

                # 处理启动模板列表
                if (
                    response.body.launch_template_sets
                    and response.body.launch_template_sets.launch_template_set
                ):
                    for (
                        template
                    ) in response.body.launch_template_sets.launch_template_set:
                        template_info = {
                            "launch_template_id": template.launch_template_id,
                            "launch_template_name": template.launch_template_name,
                            "default_version_number": template.default_version_number,
                            "latest_version_number": template.latest_version_number,
                            "created_by": template.created_by,
                            "create_time": template.create_time,
                            "modified_time": template.modified_time,
                            "resource_group_id": template.resource_group_id,
                            "tags": [],
                            "version_details": [],
                        }

                        # 处理标签
                        if template.tags and template.tags.tag:
                            for tag in template.tags.tag:
                                template_info["tags"].append(
                                    {"tag_key": tag.tag_key, "tag_value": tag.tag_value}
                                )

                        result["launch_templates"].append(template_info)

                return result
            else:
                print(f"\033[1;31m查询启动模板返回数据格式异常\033[0m")
                return None
        except TeaException as e:
            print(f"\033[1;31m服务器错误: {e.code} - {e.message}\033[0m")
            return None
        except UnretryableException as e:
            print(f"\033[1;31m客户端错误: {e}\033[0m")
            return None
        except Exception as e:
            print(f"\033[1;31m查询启动模板失败: {e}\033[0m")
            return None

    def create_instances_from_template(
        self,
        region_id,
        launch_template_name,
        launch_template_version=1,
        amount=1,
        password=None,
    ):
        """
        根据启动模板创建ECS实例
        """
        try:
            request = ecs_models.RunInstancesRequest(
                region_id=region_id,
                launch_template_name=launch_template_name,
                launch_template_version=launch_template_version,
                amount=amount,
                password=password,
            )

            runtime = util_models.RuntimeOptions()
            response = self.ecs_client.run_instances_with_options(request, runtime)

            if response and response.body:
                return {
                    "request_id": response.body.request_id,
                    "instance_ids": response.body.instance_id_sets.instance_id_set,
                }
            return None
        except Exception as e:
            print(f"创建实例失败: {e}")
            return None

    def get_account_balance(self):
        """
        查询账户余额
        """
        try:
            # 创建请求对象
            response = self.bss_client.query_account_balance()

            if (
                response
                and response.body
                and response.body.data
                and response.body.data.available_amount
            ):
                # 构造与旧版API相同格式的返回结果
                result = {
                    "Data": {
                        "AvailableAmount": response.body.data.available_amount,
                        "AvailableCashAmount": response.body.data.available_cash_amount,
                        "CreditAmount": response.body.data.credit_amount,
                        "MybankCreditAmount": response.body.data.mybank_credit_amount,
                        "Currency": response.body.data.currency,
                    },
                    "Code": response.body.code,
                    "Message": response.body.message,
                    "RequestId": response.body.request_id,
                    "Success": response.body.success,
                }
                return result
            else:
                print(f"\033[1;31m查询账户余额返回数据格式异常\033[0m")
                return None
        except TeaException as e:
            print(f"\033[1;31m服务器错误: {e.code} - {e.message}\033[0m")
            return None
        except UnretryableException as e:
            print(f"\033[1;31m客户端错误: {e}\033[0m")
            return None
        except Exception as e:
            print(f"\033[1;31m查询账户余额失败: {e}\033[0m")
            return None

    def delete_instance(self, instance_id):
        """
        删除实例
        """
        if not instance_id:
            print("\033[1;31m实例ID不能为空\033[0m")
            return None

        try:
            # 创建请求对象
            request = ecs_models.DeleteInstanceRequest(
                instance_id=instance_id, force=True  # 强制删除
            )

            # 设置运行时参数
            runtime = util_models.RuntimeOptions()

            # 发起调用
            response = self.ecs_client.delete_instance_with_options(request, runtime)

            if response and response.body and response.body.request_id:
                # 构造与旧版API相同格式的返回结果
                result = {"RequestId": response.body.request_id}
                return result
            else:
                print(f"\033[1;31m删除实例返回数据格式异常\033[0m")
                return None
        except TeaException as e:
            error_code = e.code
            error_msg = e.message
            print(f"\033[1;31m服务器错误: {error_code} - {error_msg}\033[0m")

            # 提供更友好的错误信息
            if error_code == "InvalidInstanceId.NotFound":
                print("\033[1;33m实例ID不存在，请检查ID是否正确\033[0m")
            elif error_code == "IncorrectInstanceStatus":
                print("\033[1;33m实例状态不正确，无法删除\033[0m")
            elif error_code == "OperationDenied":
                print("\033[1;33m操作被拒绝，可能是因为实例有关联资源或受保护\033[0m")

            return None
        except UnretryableException as e:
            print(f"\033[1;31m客户端错误: {e}\033[0m")
            return None
        except Exception as e:
            print(f"\033[1;31m删除实例失败: {e}\033[0m")
            return None

    def get_describe_instance_attribute(self, instance_id):
        """
        查询实例的公共IP地址
        :param region_id: 实例所在区域
        :param instance_id: 要查询的实例ID
        :return: 包含实例ID和公共IP的字典，如无公网IP则返回None
        """
        try:
            # 创建API请求
            request = ecs_models.DescribeInstanceAttributeRequest(
                instance_id=instance_id
            )

            runtime = util_models.RuntimeOptions()
            response = self.ecs_client.describe_instance_attribute_with_options(
                request, runtime
            )

            if response and response.body:
                instance = response.body
                # 优先获取弹性公网IP (EIP)
                eip = instance.eip_address.ip_address if instance.eip_address else None

                # 如果不存在EIP则获取公网IP
                public_ip = eip or (
                    instance.public_ip_address.ip_address[0]
                    if instance.public_ip_address
                    and instance.public_ip_address.ip_address
                    else None
                )

                return {"instance_id": instance.instance_id, "public_ip": public_ip}
            return None
        except Exception as e:
            print(f"查询实例公网IP失败: {e}")
            return None

    def get_instance_status(
        self,
        region_id,
        instance_id,
    ):
        """
        查询instance状态
        """

        if not instance_id:
            print("\033[1;31m实例ID不能为空\033[0m")
            return None

        # 发起调用
        try:
            # 创建请求对象
            request = ecs_models.DescribeInstanceStatusRequest(
                region_id=region_id if region_id else self.region_id,
                instance_id=[instance_id],
            )
            runtime = util_models.RuntimeOptions()
            response = self.ecs_client.describe_instance_status_with_options(
                request, runtime
            )
            result = {
                "Data": {
                    "TotalCount": response.body.total_count,
                    "PageSize": response.body.page_size,
                    "PageNumber": response.body.page_number,
                    "InstanceStatus": [
                        {
                            "Status": status.status,
                            "InstanceId": status.instance_id,
                        }
                        for status in response.body.instance_statuses.instance_status
                    ],
                },
                "Code": "200",
                "Message": "Success",
                "RequestId": response.body.request_id,
                "Success": True,
            }
            return result
        except TeaException as e:
            error_code = e.code
            error_msg = e.message
            print(f"\033[1;31m服务器错误: {error_code} - {error_msg}\033[0m")

            # 提供更友好的错误信息
            if error_code == "InvalidInstanceId.NotFound":
                print("\033[1;33m实例ID不存在，请检查ID是否正确\033[0m")
            elif error_code == "IncorrectInstanceStatus":
                print("\033[1;33m实例状态不正确，无法删除\033[0m")
            elif error_code == "OperationDenied":
                print("\033[1;33m操作被拒绝，可能是因为实例有关联资源或受保护\033[0m")

            return None
        except UnretryableException as e:
            print(f"\033[1;31m客户端错误: {e}\033[0m")
            return None
        except Exception as e:
            print(f"\033[1;31m查询实例失败: {e}\033[0m")
            return None

    def get_describe_instances(self, region_id=None):
        try:
            request = ecs_models.DescribeInstancesRequest(
                region_id=region_id if region_id else self.region_id
            )
            # 设置返回字段
            request.field = json.dumps(
                ["InstanceId", "PublicIpAddress", "EipAddress", "OSName", "Status"]
            )

            runtime = util_models.RuntimeOptions()
            response = self.ecs_client.describe_instances_with_options(request, runtime)

            instances = []
            if response.body and response.body.instances:
                for item in response.body.instances.instance:
                    public_ip = None
                    if item.eip_address and item.eip_address.ip_address:
                        public_ip = item.eip_address.ip_address
                    elif item.public_ip_address and item.public_ip_address.ip_address:
                        public_ip = item.public_ip_address.ip_address[0]
                    os_name = getattr(
                        item, "os_name", getattr(item, "OSName", "Unknown")
                    )
                    instances.append(
                        {
                            "instance_id": item.instance_id,
                            "public_ip": public_ip,
                            "os_name": os_name,
                            "status": item.status,
                        }
                    )

            return instances
        except Exception as e:
            print(f"查询实例失败: {e}")
            return []

    def run_instances(self, instance):
        system_disk = ecs_models.RunInstancesRequestSystemDisk(
            category=instance.SystemDiskCategory, size=instance.SystemDiskSize
        )

        instance_request = ecs_models.RunInstancesRequest(
            region_id=instance.RegionId,
            image_id=instance.ImageId,
            internet_max_bandwidth_out=instance.InternetMaxBandwidthOut,
            password=instance.Password,
            system_disk=system_disk,
            instance_type=instance.InstanceType,
            spot_strategy=instance.SpotStrategy,
            spot_duration=instance.SpotDuration,
            internet_charge_type=instance.InternetChargeType,
            instance_name=instance.InstanceName,
            v_switch_id=instance.VSwitchId,
            host_name=instance.HostName,
            instance_charge_type=instance.InstanceChargeType,
            security_group_id=instance.SecurityGroupId,
            amount=instance.Amount,
        )

        response = self.ecs_client.run_instances(instance_request)
        id = response.body.instance_id_sets.instance_id_set
        return id

    def get_describe_security_group_attribute(self, region_id, group_id):
        """
        查询指定安全组的属性信息，返回处理后的端口规则
        """
        try:
            # 创建安全组属性查询请求
            request = ecs_models.DescribeSecurityGroupAttributeRequest(
                region_id=region_id if region_id else self.region_id,
                security_group_id=group_id,
            )

            # 设置运行时选项
            runtime = util_models.RuntimeOptions()

            # 发起API调用
            response = self.ecs_client.describe_security_group_attribute_with_options(
                request, runtime
            )

            # 处理响应数据
            if response and response.body:
                processed_rules = []
                permissions = response.body.permissions.permission

                for rule in permissions:
                    # 转换端口范围
                    port_range = rule.port_range
                    if port_range == "-1/-1":
                        port_range = "all/all"

                    # 提取所需字段
                    processed_rules.append(
                        {
                            "PortRange": port_range,
                            "IpProtocol": rule.ip_protocol,
                            "SourceCidrIp": rule.source_cidr_ip,
                        }
                    )
                processed_rules = {group_id: processed_rules}
                return processed_rules
            else:
                print(f"\033[1;31m安全组 {group_id} 属性查询返回空数据\033[0m")
                return None

        except TeaException as e:
            print(f"\033[1;31m服务器错误[{group_id}]: {e.code} - {e.message}\033[0m")
            return None
        except UnretryableException as e:
            print(f"\033[1;31m客户端错误[{group_id}]: {e}\033[0m")
            return None
        except Exception as e:
            print(f"\033[1;31m安全组属性查询失败[{group_id}]: {e}\033[0m")
            return None

    def get_all_describe_security_group_attribute(self, region_id):
        group_attribute = []

        groups = self.get_describe_security_groups(region_id=region_id)
        for i in range(0, groups["TotalCount"]):
            group = groups["SecurityGroups"]["SecurityGroup"]
            securityGroupId = group[i]["SecurityGroupId"]
            attr = self.get_describe_security_group_attribute(
                region_id=region_id, group_id=securityGroupId
            )
            group_attribute.append(
                {
                    "SecurityGroupId": securityGroupId,
                    "Description": group[i]["Description"],
                    "attribute": attr[securityGroupId],
                }
            )
        return group_attribute

    def get_v_switch(self, region_id=None):
        request = ecs_models.DescribeVSwitchesRequest(
            region_id=region_id if region_id else self.region_id
        )
        vswitches_response = self.ecs_client.describe_vswitches(request)
        try:
            # 正确访问阿里云SDK响应结构
            vswitch_list = vswitches_response.body.v_switches.v_switch

            # 提取目标字段
            return [[vsw.v_switch_id, vsw.zone_id, vsw.vpc_id] for vsw in vswitch_list]

        except AttributeError as e:
            raise ValueError(f"无效的SDK响应结构: {str(e)}") from e
