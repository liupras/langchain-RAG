#coding=utf-8

#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-11-04
# @Description: 使用FastAPI做langchain的API
# @version : V0.5

'''安装依赖
pip install fastapi pydantic typing
'''

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.llms import OllamaLLM

# 翻译方法
def translate(language,text):
    # 1. 创建提示词模板
    system_template = "Translate the following into {language}:"
    prompt_template = ChatPromptTemplate.from_messages([
        ('system', system_template),
        ('user', '{text}')
    ])

    # 2. 创建本地大模型
    model = OllamaLLM(model="llama3.1")

    # 3. 创建解析器
    parser = StrOutputParser()

    # 4. 创建链
    chain = prompt_template | model | parser

    #5. 调用链
    result = chain.invoke({"language": language,"text":text})

    return result


# 导入FastAPI和Pydantic
from fastapi import FastAPI
from pydantic import BaseModel, Field


# 定义一个Pydantic模型来校验输入的JSON数据
class query_model(BaseModel):
    lang: str = Field(min_length=2, max_length=20, description="语言名称" )
    text: str = Field(min_length=2, max_length=500, description="待翻译的文本" )

from enum import Enum
# 操作结果枚举
class code_enum(str,Enum):
    OK = 'ok'
    ERR = 'error'

# API返回的消息体
class response_model(BaseModel):
    code: code_enum = Field(description="操作结果" )
    desc: str = Field(description="具体内容" )


# 创建一个FastAPI实例
app = FastAPI()

# 创建一个处理POST请求的端点。
'''
!注意：设置端点时，建议养成都不加 / 的风格。
在使用API网关时，如果从API网关传过来的路径是以 / 结尾的话，因为和此端点路径不一致，此端点会自动返回301重定向，导致客户端发生400错误。
'''
@app.post("/trans/v1", response_model=response_model)
async def translate_api(query: query_model):
    """
    翻译文本。

    参数:
    - Query: 翻译请求内容。

    返回:
    - Query: 测试
    """
    
    try:
        r = translate(query.lang.strip(),query.text.strip())
        return response_model(code=code_enum.OK,desc=r)
    except Exception as e:
        return response_model(code=code_enum.ERR,desc=str(e))

import uvicorn

if __name__ == '__main__':
    # 交互式API文档地址：
    # http://127.0.0.1:5001/docs/ 
    # http://127.0.0.1:5001/redoc/
    
    uvicorn.run(app, host="0.0.0.0", port=5001)
   