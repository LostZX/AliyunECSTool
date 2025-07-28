#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具函数模块
"""

from prettytable import PrettyTable


def create_table(headers):
    """
    创建一个带有彩色标题的表格
    
    Args:
        headers: 表格标题列表
    
    Returns:
        PrettyTable对象
    """
    # 为标题添加颜色
    colored_headers = [f"\033[1;36m{header}\033[0m" for header in headers]
    table = PrettyTable(['序号'] + colored_headers)
    return table


def print_warning(message):
    """
    打印警告信息
    
    Args:
        message: 警告信息
    """
    print(f"\033[1;33m{message}\033[0m")


def print_error(message):
    """
    打印错误信息
    
    Args:
        message: 错误信息
    """
    print(f"\033[1;31m{message}\033[0m")


def print_success(message):
    """
    打印成功信息
    
    Args:
        message: 成功信息
    """
    print(f"\033[1;32m{message}\033[0m")


def print_info(message):
    """
    打印普通信息
    
    Args:
        message: 普通信息
    """
    print(f"\033[1;36m{message}\033[0m")


def confirm_action(message, confirm_word=None):
    """
    确认操作
    
    Args:
        message: 确认信息
        confirm_word: 确认词，如果提供，用户必须输入此词才能确认
    
    Returns:
        bool: 是否确认
    """
    if confirm_word:
        user_input = input(f"\033[1;33m{message}\033[0m ({confirm_word}): ").strip()
        return user_input == confirm_word
    else:
        user_input = input(f"\033[1;33m{message}\033[0m (y/n): ").strip().lower()
        return user_input == 'y'


def get_user_input(prompt, default=None):
    """
    获取用户输入
    
    Args:
        prompt: 提示信息
        default: 默认值
    
    Returns:
        str: 用户输入
    """
    if default:
        user_input = input(f"\033[1;33m{prompt}\033[0m [默认: {default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"\033[1;33m{prompt}\033[0m: ").strip()