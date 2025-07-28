#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模块，用于加载和管理配置文件
"""

import sys
import yaml


class Config:
    """
    配置类，用于加载配置文件
    """

    def __init__(self, config_file="config.yml"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """
        加载配置文件
        """
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if not config:
                    raise ValueError("配置文件为空")
                return config
        except FileNotFoundError:
            print(f"\033[1;33m配置文件 {self.config_file} 不存在\033[0m")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"\033[1;31m解析配置文件失败: {e}\033[0m")
            sys.exit(1)
        except Exception as e:
            print(f"\033[1;31m加载配置文件失败: {e}\033[0m")
            sys.exit(1)

    def get_access_key(self):
        """
        获取阿里云AccessKey
        """
        try:
            return (
                self.config["aliyun"]["access_key_id"],
                self.config["aliyun"]["access_key_secret"],
            )
        except KeyError:
            print("\033[1;31m配置文件中缺少阿里云AccessKey配置\033[0m")
            print("\033[1;33m请确保config.yml文件中包含以下结构:\033[0m")
            print(
                "aliyun:\n  access_key_id: 您的AccessKeyID\n  access_key_secret: 您的AccessKeySecret"
            )
            sys.exit(1)

    def get_default_region(self):
        """
        获取默认区域ID
        """
        return self.config["aliyun"]["region_id"]

    def get_instance_type(self):
        return self.config["instance"]["instance_type"]

    def get_password(self):
        return self.config["instance"]["password"]

    def get_internet_charge_type(self):
        return self.config["instance"]["internet_charge_type"]

    def get_internet_max_bandwidth_out(self):
        return self.config["instance"]["internet_max_bandwidth_out"]

    def get_image_id(self):
        return self.config["instance"]["image_id"]

    def get_resource_type(self):
        return self.config["instance"]["resource_type"]

    def get_instance_name(self):
        return self.config["instance"]["instance_name"]

    def get_system_disk_size(self):
        return self.config["instance"]["system_disk_size"]

    def get_system_disk_category(self):
        return self.config["instance"]["system_disk_category"]

    def get_spot_strategy(self):
        return self.config["instance"]["spot_strategy"]

    def get_spot_duration(self):
        return self.config["instance"]["spot_duration"]

    def get_region_id(self):
        return self.config["instance"]["region_id"]

    def get_v_switch_id(self):
        return self.config["instance"]["v_switch_id"]

    def get_security_group_id(self):
        return self.config["instance"]["security_group_id"]

    def get_amount(self):
        return self.config["instance"]["amount"]

    def get_host_name(self):
        return self.config["instance"]["host_name"]

    def get_instance_charge_type(self):
        return self.config["instance"]["instance_charge_type"]
