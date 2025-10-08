#coding=utf-8
#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-12-25
# @Description: 处理配置文件。
# @version : V0.5

'''
pip install pyyaml
'''
import yaml
import os

class Config:
    _config = None

    @classmethod
    def load(cls, config_file):
        if cls._config is None:
            with open(config_file, 'r',encoding="utf-8") as file:
                cls._config = yaml.safe_load(file)
        return cls._config

    @classmethod
    def get(cls, key):
        return cls._config.get(key)

# 加载配置文件
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
config = Config.load(config_path)

# 现在可以在程序的任何地方使用config对象来访问配置
# 例如：
# database_host = config.get('database')['host']
# logging_level = config.get('logging')['level']
