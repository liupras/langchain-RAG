#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @date    : 2025-06-28
# @description: 工具函数集。

import os
def check_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def get_current_dir():
    """获取当前文件所在的文件夹"""

    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    return current_dir