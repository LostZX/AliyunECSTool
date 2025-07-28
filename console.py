#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
命令行交互界面模块
"""

import cmd
import time
from prettytable import PrettyTable
from tabulate import tabulate
from instance import Instance

from config import Config
from api import AliyunAPI
from utils import (
    print_warning,
    print_error,
    print_success,
    print_info,
    get_user_input,
)


class AliyunECSConsole(cmd.Cmd):
    """
    阿里云ECS控制台
    """

    intro = """
    ╔═════════════════════════════════════════════════════════════════╗
    ║                                                                 ║
    ║                  阿里云ECS管理工具 v1.0                         ║
    ║                                                                 ║
    ║  可用命令:                                                      ║
    ║  \033[1;32mcreate\033[0m          - 创建新的ECS实例                              ║
    ║  \033[1;32mdelete\033[0m          - 删除指定的ECS实例                            ║
    ║  \033[1;32mbalance\033[0m         - 查询账户余额                                 ║
    ║  \033[1;32mstatus\033[0m          - 查询ECS状态                                  ║
    ║  \033[1;32mquery\033[0m           - 查询ECS信息                                  ║
    ║  \033[1;32minstances\033[0m       - 查询所有ECS信息                              ║
    ║  \033[1;32minstance_type\033[0m   - 查询规格信息列表                             ║
    ║  \033[1;32mtemplates\033[0m       - 查询模板信息                                  ║
    ║  \033[1;32mprice\033[0m           - 查询ECS价格                                  ║    
    ║  \033[1;32mexit\033[0m            - 退出程序                                     ║
    ║                                                                 ║
    ╚═════════════════════════════════════════════════════════════════╝
    """
    prompt = "\033[1;36m阿里云ECS >\033[0m "

    def __init__(self):
        super().__init__()
        try:
            self.config = Config()
            access_key_id, access_key_secret = self.config.get_access_key()
            self.api = AliyunAPI(access_key_id, access_key_secret)
            self.current_region = self.config.get_default_region()  # 从配置获取默认区域
            self.api.set_region(self.current_region)
            print_success(f"成功连接到阿里云API，当前区域: {self.current_region}")

        except Exception as e:
            print_error(f"初始化失败: {e}")
            raise

    def get_names(self):
        """
        获取可用命令列表，只返回我们想要保留的命令
        """
        return [
            "create",
            "delete",
            "balance",
            "status",
            "query",
            "instances",
            "instance_type",
            "templates",
            "price" "help",
            "exit",
            "quit",
        ]

    def get_all_commands(self):
        """
        获取所有命令列表，用于帮助信息
        """
        commands = {
            "create": "创建新的ECS实例",
            "delete": "删除指定的ECS实例 delete instance_id",
            "balance": "查询账户余额",
            "status": "查询ECS状态 status instance_id",
            "query": "查询ECS信息 query instance_id",
            "instances": "查询所有ECS",
            "instance_type": "查询规格信息列表",
            "templates": "查询模板信息",
            "price": "查询实例当前价格",
            "exit": "退出程序",
            "quit": "退出程序",
            "help": "显示帮助信息",
        }
        return commands

    def do_help(self, arg):
        """
        显示帮助信息
        """
        if arg:
            # 显示特定命令的帮助
            super().do_help(arg)
        else:
            # 显示自定义帮助信息
            print_info("可用命令:")
            commands = self.get_all_commands()
            for cmd, desc in commands.items():
                print(f"  \033[1;32m{cmd}\033[0m - {desc}")

    def default(self, line):
        """
        处理未知命令
        """
        print_error(f"未知命令: {line}")
        print("输入 \033[1;32mhelp\033[0m 查看可用命令")

    def emptyline(self):
        """
        空行处理
        """
        pass

    def do_exit(self, arg):
        """
        退出程序
        """
        print_success("感谢使用阿里云ECS管理工具，再见！")
        return True

    def do_quit(self, arg):
        """
        退出程序
        """
        return self.do_exit(arg)

    def do_EOF(self, arg):
        """
        Ctrl+D退出程序
        """
        print()
        return self.do_exit(arg)

    def do_balance(self, arg):
        """
        查询账户余额
        """
        print_warning("正在查询账户余额...")
        result = self.api.get_account_balance()
        if result:
            data = result.get("Data", {})
            available_amount = data.get("AvailableAmount", "0")
            print(
                f"\033[1;32m当前账户可用余额:\033[0m \033[1;36m{available_amount}\033[0m 元"
            )
            # 如果余额低于100元，显示警告
            try:
                balance_float = float(available_amount)
                if balance_float < 100:
                    print_error("警告: 账户余额较低，请及时充值以避免服务中断")
            except ValueError:
                pass  # 忽略转换错误
        else:
            print_error("查询账户余额失败")
            print_warning("可能原因:")
            print("1. \033[1;36mAccessKey无效或已过期\033[0m")
            print("2. \033[1;36m网络连接问题\033[0m")
            print("3. \033[1;36m阿里云API服务异常\033[0m")

    def do_setregion(self, arg):
        """
        设置当前区域
        用法: setregion <region_id>
        例如: setregion cn-beijing
        """
        if not arg:
            print_warning("请指定区域ID")
            return

        self.current_region = arg
        self.api.set_region(arg)
        print_success(f"当前区域已设置为: {arg}")

    def do_create(self, arg):
        """
        创建实例向导
        """
        print("\n\033[1;36m===== 创建ECS实例向导 =====\033[0m\n")

        # 显示当前账户余额
        self.do_balance(None)
        print()

        use_template = get_user_input("是否从模板创建? (y/n)", "n").lower()
        if use_template == "y":
            api = AliyunAPI.get_instance()
            self.do_templates(None)
            current_region = get_user_input(
                "是否更改地域id? (当前id为) > " + self.current_region,
                self.current_region,
            )
            launch_template_name = get_user_input("选择模板名称：")
            launch_template_version = get_user_input("选择模板版本：", 1)
            amount = get_user_input("创建数量（默认为1）：", 1)
            password = get_user_input("输入root密码: ")
            region_id = self.current_region
            result = api.create_instances_from_template(
                current_region,
                launch_template_name,
                launch_template_version,
                amount,
                password,
            )
            instance_id = result["instance_ids"][0]
            print("等待系统处理中...")
            for i in range(10, 0, -1):
                print(f"\033[1;33m倒计时: {i}秒\033[0m", end="\r")
                time.sleep(1)
            result = self.api.get_describe_instance_attribute(instance_id)
            instance_result = self.display_result_instances_table(result)
            print(instance_result)
        else:
            change = get_user_input(
                "是否更改区域? 当前区域为 > " + self.current_region + " (y/n)", "n"
            ).lower()
            if change == "y":
                if not self._show_regions():
                    return
                region_id = get_user_input(
                    f"请输入区域ID", self.config.get_default_region()
                )
                if region_id:
                    self.api.set_region(region_id)
                    self.current_region = region_id
            print()
            # 选择镜像
            print_info("===== 选择镜像 =====")
            image_id = get_user_input(f"请输入镜像ID", self.config.get_image_id())
            print()

            # 选择实例规格
            print_info("===== 选择实例规格 =====")
            instance_type = get_user_input(
                f"请输入实例规格", self.config.get_instance_type()
            )
            print()
            # 设置密码

            print("\n\033[1;36m===== 输入密码 =====\033[0m")

            password = get_user_input("请输入密码", self.config.get_password())

            print("\n\033[1;36m===== 设置带宽 =====\033[0m")

            # 设置带宽
            bandwidth = get_user_input(
                "请输入公网出带宽(Mbps)", self.config.get_internet_max_bandwidth_out()
            )

            # 选择安全组
            print("\n\033[1;36m===== 选择安全组 =====\033[0m")

            print()

            securityGroups = self.api.get_all_describe_security_group_attribute(
                self.current_region
            )
            print(self.display_security_groups_table(securityGroups))
            security_group_id = get_user_input("请输入安全组ID")
            if not security_group_id:
                print_error("安全组ID不能为空，创建实例失败")
                return

            print("\n\033[1;36m===== 选择交换机 =====\033[0m")

            vswitch = self.api.get_v_switch(self.current_region)
            print(self.display_vswitch_table(vswitch))
            VSwitchId = get_user_input("请输入VSwitchId: ")

            if not VSwitchId:
                print_error("虚拟交换机ID不能为空，创建实例失败")
                return

            print("\n\033[1;36m===== 选择磁盘 =====\033[0m")

            SystemDiskCategory = get_user_input(
                "请输入系统盘类型", self.config.get_system_disk_category()
            )

            SystemDiskSize = get_user_input(
                "请输入系统盘大小(GB)", self.config.get_system_disk_size()
            )

            print("\n\033[1;36m===== 选择实例付费模式 =====\033[0m")

            InstanceChargeType = get_user_input(
                "请输入实例的付费方式", self.config.get_instance_charge_type()
            )

            print("\n\033[1;36m===== 选择网络带宽付费模式 =====\033[0m")

            InternetChargeType = get_user_input(
                "请输入网络带宽计费方式", self.config.get_internet_charge_type()
            )

            print("\n\033[1;36m===== 选择竞价策略 =====\033[0m")

            SpotStrategy = get_user_input("请输入竞价策略: ", "SpotAsPriceGo")
            if SpotStrategy == "SpotAsPriceGo":
                # 如果是抢占实例，询问竞价时长
                print("\n\033[1;36m===== 竞价时长 =====\033[0m")
                # 询问用户输入竞价时长
                SpotDuration = get_user_input(
                    "请输入竞价时长(小时), 0表示不限制: ", "0"
                )
            else:
                SpotDuration = None

            print("\n\033[1;36m===== 输入主机名称 =====\033[0m")
            HostName = get_user_input("请输入实例名称", "vps")

            print("\n\033[1;36m===== 输入实例名称 =====\033[0m")

            InstanceName = get_user_input("请输入实例名称", "balala")

            print("\n\033[1;36m===== 选择创建数量 =====\033[0m")
            Amount = get_user_input("请输入创建数量", "1")

            ##############

            instance = Instance(
                RegionId=self.current_region,
                ImageId=image_id,
                InstanceType=instance_type,
                Password=password,
                InternetMaxBandwidthOut=bandwidth,
                SecurityGroupId=security_group_id,
                VSwitchId=VSwitchId,
                SystemDiskCategory=SystemDiskCategory,
                SystemDiskSize=SystemDiskSize,
                SpotStrategy=SpotStrategy,
                SpotDuration=SpotDuration,
                InternetChargeType=InternetChargeType,
                HostName=HostName,
                InstanceName=InstanceName,
                Amount=Amount,
                InstanceChargeType=InstanceChargeType,
            )

            # 确认创建
            print("\n\033[1;36m===== 实例配置信息 =====\033[0m")
            print(instance)

            confirm = get_user_input("确认创建实例?", "y").lower()
            if confirm != "y":
                print_error("取消创建实例")
                return

            print_warning("正在创建实例...")

            instance_id = self.api.run_instances(instance=instance)
            print_success(f"实例创建请求已发送，实例ID: {instance_id[0]}")
            print("等待系统处理中...")
            for i in range(10, 0, -1):
                print(f"\033[1;33m倒计时: {i}秒\033[0m", end="\r")
                time.sleep(1)
            status = self.api.get_instance_status(self.current_region, instance_id[0])
            if (
                status["Data"]["TotalCount"] == 1
                and status["Data"]["InstanceStatus"][0]["Status"] == "Running"
            ):
                print_success("实例创建成功，状态为 Running")
                result = self.api.get_describe_instance_attribute(instance_id[0])
                instance_result = self.display_result_instances_table(result)
                print(instance_result)
            else:
                print_error("实例创建尚未完成，可能需要更多时间")
                print_warning(
                    "建议稍后使用 'status '" + instance_id[0] + " 命令手动检查状态"
                )

    def do_delete(self, arg):
        """
        删除ECS实例
        用法: delete <instance_id>
        """
        if not arg:
            print_error("错误: 请指定实例ID")
            print("用法: \033[1;32mdelete <instance_id>\033[0m")
            return

        # 显示警告信息
        print_error("警告: 删除操作不可恢复，实例数据将永久丢失!")
        print_warning(f"您即将删除实例: {arg}")

        # 二次确认
        confirm = get_user_input(f"确认删除实例 {arg}?", "no").lower()
        if confirm != "yes":
            print_success("已取消删除操作")
            return

        # 最终确认
        final_confirm = get_user_input("最终确认: 输入实例ID以确认删除")
        if final_confirm != arg:
            print_success("实例ID不匹配，已取消删除操作")
            return

        print_warning(f"正在删除实例 {arg}...")
        result = self.api.delete_instance(arg)
        if result is None:
            print_error(f"删除实例 {arg} 失败")
            print_warning("可能的原因:")
            print("1. \033[1;36m实例ID不存在或输入错误\033[0m")
            print("2. \033[1;36m实例当前状态不允许删除\033[0m")
            print("3. \033[1;36m没有足够的权限执行此操作\033[0m")
            print("4. \033[1;36m阿里云API服务异常\033[0m")
            return

        print_success(f"删除实例 {arg} 的请求已发送")
        print_warning("实例删除需要一段时间完成，请耐心等待...")

        # 添加10秒倒计时
        print("等待系统处理中...")
        for i in range(10, 0, -1):
            print(f"\033[1;33m倒计时: {i}秒\033[0m", end="\r")
            time.sleep(1)

        print("\n\033[1;32m正在验证删除状态...\033[0m")

        # 查询实例状态
        status_result = self.api.get_instance_status(self.current_region, arg)
        # 判断删除结果
        if status_result["Data"]["TotalCount"] > 0:
            print_error("实例删除尚未完成，可能需要更多时间")
            print_warning("建议稍后使用 'status' 命令手动检查状态")
        else:
            print_success(f"实例 {arg} 已成功删除")
            print_warning("所有关联资源（如磁盘和弹性IP）也已释放")

    def do_status(self, arg):
        if not arg:
            print_error("错误: 请指定实例ID")
            print("用法: \033[1;32mstatus <instance_id>\033[0m")
            return
        result = self.api.get_instance_status(self.current_region, arg)
        if result["Data"]["TotalCount"] == 0:
            print_error("实例不存在")
        else:
            print_success(result["Data"]["InstanceStatus"][0]["Status"])

    def do_query(self, arg):
        if not arg:
            print_error("错误: 请指定实例ID")
            print("用法: \033[1;32mquery <instance_id>\033[0m")
            return
        result = self.api.get_describe_instance_attribute(arg)
        instance_result = self.display_result_instances_table(result)
        print(instance_result)

    def do_instance_type(self, arg):
        types = AliyunAPI.get_instance().get_describe_instance_types()
        self.display_instance_types_table(types)

    @staticmethod
    def display_instance_types_table(data):
        """
        以表格形式展示实例规格信息（修复了None值比较问题）

        :param data: get_describe_instance_types返回的数据
        """
        if not data or "instance_types" not in data or not data["instance_types"]:
            print("未获取到有效的实例规格数据")
            return

        # 准备表格数据
        table_data = []
        for it in data["instance_types"]:
            # 获取存储数据，处理可能的None值
            storage_size = it.get("LocalStorageSize")
            storage_amount = it.get("LocalStorageAmount")
            storage_cat = it.get("LocalStorageCategory", "N/A")

            # 修复存储显示逻辑：避免与None值比较
            storage_display = "-"

            # 确保storage_amount是整数才能安全比较
            if isinstance(storage_amount, int):
                # 确保storage_size存在
                if storage_size is None:
                    storage_display = f"{storage_amount}×?"
                # storage_size也可能是字符串类型(如"1024GiB")
                elif isinstance(storage_size, int):
                    storage_display = f"{storage_amount}×{storage_size}GB"
                elif isinstance(storage_size, str):
                    storage_display = f"{storage_amount}×{storage_size}"
                else:
                    storage_display = f"{storage_amount}×?"
            # 当storage_amount无效时显示默认值
            else:
                storage_display = "-" if storage_cat == "cloud" else "N/A"

            # 安全处理其他字段的None值
            def safe_value(val):
                return val if val is not None else "N/A"

            table_data.append(
                [
                    safe_value(it.get("InstanceTypeId")),
                    safe_value(it.get("CpuCoreCount")),
                    safe_value(it.get("MemorySize")),
                    safe_value(it.get("GPUAmount")),
                    safe_value(it.get("GPUSpec")),
                    storage_cat,
                    storage_display,
                    safe_value(it.get("NetworkCardQuantity")),
                    safe_value(it.get("EniPrivateIpAddressQuantity")),
                    safe_value(it.get("InstanceTypeFamily")),
                ]
            )

        # 表头定义
        headers = [
            "规格ID",
            "CPU(核)",
            "内存(GiB)",
            "GPU数量",
            "GPU规格",
            "本地存储",
            "存储容量",
            "网卡数",
            "IP数量",
            "规格族",
        ]

        # 打印标题
        print("\n" + "=" * 80)
        print("ECS实例规格列表")
        print("=" * 80)

        # 使用 tabulate 渲染表格
        print(
            tabulate(
                table_data,
                headers=headers,
                tablefmt="grid",  # 网格格式
                stralign="center",  # 居中对齐更美观
                numalign="center",
                missingval="N/A",  # 处理缺失值
            )
        )

    def do_templates(self, arg):
        data = self.api.get_describe_launch_templates()
        self.display_launch_templates_table(data)

    @staticmethod
    def display_launch_templates_table(data):
        """
        以表格形式展示启动模板信息

        :param data: get_describe_launch_templates返回的数据
        """
        if not data or "launch_templates" not in data or not data["launch_templates"]:
            print("未获取到有效的启动模板数据")
            return

        # 准备表格数据
        table_data = []
        for template in data["launch_templates"]:
            # 处理标签
            tags = ""
            if template.get("tags"):
                tags_list = [
                    f"{tag['tag_key']}:{tag['tag_value']}"
                    for tag in template["tags"]
                    if "tag_key" in tag and "tag_value" in tag
                ]
                tags = ", ".join(tags_list)

            table_data.append(
                [
                    template.get("launch_template_id", "N/A"),
                    template.get("launch_template_name", "N/A"),
                    template.get("default_version_number", "N/A"),
                    template.get("latest_version_number", "N/A"),
                    template.get("created_by", "N/A"),
                    template.get("create_time", "N/A"),
                    tags,
                ]
            )

        # 表头定义
        headers = [
            "模板ID",
            "模板名称",
            "默认版本",
            "最新版本",
            "创建者",
            "创建时间",
            "标签",
        ]

        # 使用 tabulate 渲染表格
        print(
            tabulate(
                table_data,
                headers=headers,
                tablefmt="grid",  # 网格格式
                stralign="left",  # 与 render_instances_table 一致
                numalign="center",
                missingval="N/A",  # 处理缺失值
            )
        )

        print(f"启动模板总数: {len(data['launch_templates'])}")

        # 分页信息
        if all(key in data for key in ["page_number", "page_size", "total_count"]):
            total_pages = (data["total_count"] + data["page_size"] - 1) // data[
                "page_size"
            ]
            print(
                f"页码: {data['page_number']}/{total_pages} (每页 {data['page_size']} 条)"
            )

    def do_instances(self, arg):
        instances = self.api.get_describe_instances(self.current_region)
        table = self.display_instances_table(instances)
        print(table)

    @staticmethod
    def display_instances_table(instances):
        """
        渲染实例信息表格
        :param instances: describe_instances()返回的结果
        :return: 格式化表格字符串
        """

        if not instances:
            return "暂无实例数据"

        # 准备表格数据
        table_data = []
        for inst in instances:
            table_data.append(
                [
                    inst["instance_id"],
                    inst["public_ip"] or "无",
                    inst["os_name"],
                    inst["status"],
                ]
            )

        # 创建表格
        headers = ["实例ID", "公网IP", "操作系统", "状态"]
        return tabulate(
            table_data,
            headers=headers,
            tablefmt="grid",  # 网格格式
            stralign="left",
            numalign="left",
        )

    @staticmethod
    def display_security_groups_table(security_groups):
        """
        渲染安全组属性信息表格
        :param security_groups: get_describe_security_group_attribute()返回的结果
        :return: 格式化表格字符串
        """
        if not security_groups:
            return "暂无安全组数据"

        # 准备表格数据（按安全组分组）
        all_tables = []

        for sg in security_groups:
            # 安全组标题信息
            header = f"安全组ID: {sg['SecurityGroupId']}"
            if sg["Description"]:
                header += f" | 描述: {sg['Description']}"

            # 创建规则表格
            rule_data = []
            for rule in sg["attribute"]:
                # 标准化协议名称
                protocol = rule["IpProtocol"]
                if protocol == "ALL":
                    protocol = "全部协议"

                rule_data.append([rule["PortRange"], protocol, rule["SourceCidrIp"]])

            if not rule_data:
                rule_table = "此安全组暂无规则"
            else:
                # 创建规则表格
                headers = ["端口范围", "协议", "源IP网段"]
                rule_table = tabulate(
                    rule_data,
                    headers=headers,
                    tablefmt="grid",
                    stralign="left",
                    numalign="left",
                )

            # 组合安全组信息
            all_tables.append(f"\n{header}\n{rule_table}")

        # 返回所有安全组的组合表格
        return "\n".join(all_tables)

    @staticmethod
    def display_vswitch_table(extracted_data):
        """
        渲染VSwitch信息表格
        :param extracted_data: extract_vswitch_info()返回的数据
        :return: 格式化表格字符串
        """
        if not extracted_data:
            return "未找到虚拟交换机信息"

        # 准备表格数据
        table_data = []
        for i, (vsw_id, zone_id, vpc_id) in enumerate(extracted_data, 1):
            table_data.append([f"#{i}", vsw_id, zone_id, vpc_id])

        # 创建表格
        headers = ["序号", "VSwitch ID", "可用区", "VPC ID"]
        return tabulate(table_data, headers=headers, tablefmt="grid", stralign="left")

    @staticmethod
    def display_result_instances_table(instances):
        """
        渲染创建实例信息表格 (兼容多种数据结构)
        """
        if not instances:
            return "暂无实例数据"

        # 将单字典转换为列表
        if isinstance(instances, dict):
            instances = [instances]

        # 统一处理为字典格式
        normalized_data = []
        for item in instances:
            if isinstance(item, dict):
                # 处理字典格式
                normalized_data.append(
                    {
                        "instance_id": item.get("instance_id", "未知ID"),
                        "public_ip": item.get("public_ip") or "无",
                    }
                )
            elif isinstance(item, str):
                # 处理字符串格式 (直接作为instance_id)
                normalized_data.append({"instance_id": item, "public_ip": "无"})
            else:
                # 处理意外格式
                normalized_data.append(
                    {"instance_id": "无效格式", "public_ip": "无效格式"}
                )

        # 准备表格数据
        table_data = []
        for inst in normalized_data:
            table_data.append([inst["instance_id"], inst["public_ip"]])

        # 创建表格
        headers = ["实例ID", "公网IP"]
        return tabulate(table_data, headers=headers, tablefmt="grid", stralign="left")

    def do_price(self, arg):
        print("\n\033[1;36m===== ECS查价向导 =====\033[0m\n")
        ResourceType = "instance"

        RegionId = get_user_input("请输入区域ID: ", self.current_region)
        ImageId = get_user_input(
            "请输入imageid: ", "ubuntu_20_04_x64_20G_alibase_20250625.vhd"
        )
        InstanceType = get_user_input("请输入实例的资源规格：", "ecs.e-c1m2.xlarge")
        SystemDiskCategory = get_user_input(
            "请输入系统盘云盘类型： ", "cloud_essd_entry"
        )
        SystemDiskSize = get_user_input("请输入系统盘大小: ", "40")
        SpotStrategy = get_user_input(
            "请输入按量付费实例的抢占策略： ", "SpotAsPriceGo"
        )
        if SpotStrategy == "SpotAsPriceGo":
            SpotDuration = get_user_input("请输入实例使用时长: ", "0")
        InternetChargeType = get_user_input(
            "请输入网络带宽计费方式: ", "PayByBandwidth"
        )

        InternetMaxBandwidthOut = get_user_input("请输入公网出带宽最大值：", "5")
        Amount = get_user_input("请输入实例数量", 1)

        result = self.api.get_describe_price(
            RegionId=RegionId,
            ResourceType=ResourceType,
            InstanceType=InstanceType,
            SystemDiskCategory=SystemDiskCategory,
            ImageId=ImageId,
            SystemDiskSize=SystemDiskSize,
            SpotStrategy=SpotStrategy,
            SpotDuration=SpotDuration,
            InternetChargeType=InternetChargeType,
            InternetMaxBandwidthOut=InternetMaxBandwidthOut,
            Amount=Amount,
        )

        print(result)
        flag = get_user_input("是否根据该价格创建实例: (y/n)", "n")
        if flag == "y":
            HostName = "vps"
            Password = get_user_input("输入root密码: ")
            InstanceChargeType = get_user_input("请输入实例的付费方式: ", "PostPaid")
            vswitch = self.api.get_v_switch(self.current_region)
            print(self.display_vswitch_table(vswitch))
            VSwitchId = get_user_input("请输入VSwitchId: ")
            securityGroups = self.api.get_all_describe_security_group_attribute(
                self.current_region
            )
            print(self.display_security_groups_table(securityGroups))
            SecurityGroupId = get_user_input("请输入SecurityGroupId： ")
            instance = Instance(
                RegionId=RegionId,
                InstanceType=InstanceType,
                SystemDiskCategory=SystemDiskCategory,
                ImageId=ImageId,
                SystemDiskSize=SystemDiskSize,
                SpotStrategy=SpotStrategy,
                SpotDuration=SpotDuration,
                InternetChargeType=InternetChargeType,
                InternetMaxBandwidthOut=InternetMaxBandwidthOut,
                Password=Password,
                SecurityGroupId=SecurityGroupId,
                VSwitchId=VSwitchId,
                InstanceChargeType=InstanceChargeType,
                Amount=Amount,
                HostName=HostName,
            )

            instance_id = self.api.run_instances(instance=instance)
            print_success(f"实例创建请求已发送，实例ID: {instance_id[0]}")
            print("等待系统处理中...")
            for i in range(10, 0, -1):
                print(f"\033[1;33m倒计时: {i}秒\033[0m", end="\r")
                time.sleep(1)
            status = self.api.get_instance_status(self.current_region, instance_id[0])
            if (
                status["Data"]["TotalCount"] == 1
                and status["Data"]["InstanceStatus"][0]["Status"] == "Running"
            ):
                print_success("实例创建成功，状态为 Running")
                result = self.api.get_describe_instance_attribute(instance_id[0])
                instance_result = self.display_result_instances_table(result)
                print(instance_result)
            else:
                print_error("实例创建尚未完成，可能需要更多时间")
                print_warning(
                    "建议稍后使用 'status '" + instance_id[0] + " 命令手动检查状态"
                )
