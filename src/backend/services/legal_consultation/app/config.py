#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @date    : 2025-06-04
# @description: 处理配置信息

from pydantic_settings import BaseSettings, SettingsConfigDict

import os
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
fp_env = os.path.join(current_dir, "..", ".env")

class Settings(BaseSettings):
    base_url:str
    db_path:str
    log_level:str
    llm_model_name_local: str
    llm_max_size: int
    embed_model_name: str
    embed_max_size:int
    dashscope_api_key:str

    # ✅ 显式声明配置文件路径
    model_config = SettingsConfigDict(env_file=fp_env, env_file_encoding="utf-8")

settings = Settings()