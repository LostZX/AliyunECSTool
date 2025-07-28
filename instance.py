class Instance:

    ResourceType = None

    # 镜像ID
    ImageId = None

    # 镜像类型
    InstanceType = None

    # 镜像名称
    InstanceName = None

    # 出网带宽
    InternetMaxBandwidthOut = None

    # 密码
    Password = None

    # 网络计费类型
    InternetChargeType = None

    # 系统盘大小
    SystemDiskSize = None

    # 系统盘类型
    SystemDiskCategory = None

    # 竞价策略
    SpotStrategy = None

    InstanceChargeType = None

    # 销毁时间
    SpotDuration = None

    # 区域id
    RegionId = None

    # 虚拟交换机id
    VSwitchId = None

    # 安全组id
    SecurityGroupId = None

    # 数量
    Amount = None

    # 主机名
    HostName = None

    def __init__(self, **kwargs):
        # 定义类属性
        self.ImageId = None
        self.InstanceType = None
        self.InstanceName = None
        self.InternetMaxBandwidthOut = None
        self.Password = None
        self.InternetChargeType = None
        self.SystemDiskSize = None
        self.SystemDiskCategory = None
        self.SpotStrategy = None
        self.SpotDuration = None
        self.RegionId = None
        self.ResourceType = None
        self.SecurityGroupId = None
        self.VSwitchId = None
        self.Amount = None
        self.HostName = None
        self.InstanceChargeType = None

        # 动态匹配传入参数与类属性
        class_attrs = vars(self).keys()
        for key, value in kwargs.items():
            if key in class_attrs:
                setattr(self, key, value)

    def __repr__(self):
        attrs = "\n".join([f"{k}: {v}" for k, v in vars(self).items()])
        return f"Instance Object:\n{attrs}"
