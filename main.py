#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
阿里云ECS管理工具
类似MSF的交互式对话脚本，用于申请和管理阿里云ECS实例
"""

import traceback
from console import AliyunECSConsole
from utils import print_warning, print_error, print_success


def main():
    """
    主函数
    """
    try:
        print_warning("正在初始化阿里云ECS管理工具...")
        console = AliyunECSConsole()
        console.cmdloop()
    except KeyboardInterrupt:
        print("\n")
        print_error("程序被中断")
    except Exception as e:
        print_error(f"程序出错: {e}")
        # 打印更详细的错误信息，帮助调试
        print_warning("详细错误信息:")
        traceback.print_exc()
    finally:
        print_success("感谢使用阿里云ECS管理工具!")


if __name__ == '__main__':
    main()