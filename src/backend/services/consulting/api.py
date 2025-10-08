#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-12-27
# @Description: 使用FastAPI和langchain咨询服务API
# @version : V0.5

# 导入FastAPI和Pydantic
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

# 将上级目录加入path，方便引用response等上级目录的模块
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

# 将当前文件所在目录的上级目录添加到模块搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from response import response_model,code_enum
from consulting import chat

# 定义一个Pydantic模型来校验输入的JSON数据
class query_model(BaseModel):
    question: str = Field(min_length=2, max_length=1000, description="咨询的问题内容" )

# 创建一个FastAPI实例
app = FastAPI()

# 创建一个处理POST请求的端点。
'''
!注意：设置端点时，建议养成都不加 / 的风格。
在使用API网关时，如果从API网关传过来的路径是以 / 结尾的话，因为和此端点路径不一致，此端点会自动返回301重定向，导致客户端发生400错误。
'''
@app.post("/ask/v1", response_model=response_model)
async def translate_api(query: query_model,request: Request):
    userid = request.headers.get("userid")
    print(f"userid: {userid}")
    try:
        r = chat(query.question.strip(),userid)
        return response_model(code=code_enum.OK,desc=r)
    except Exception as e:
        return response_model(code=code_enum.ERR,desc=str(e))
    
import uvicorn

if __name__ == '__main__':
    # 交互式API文档地址：
    # http://127.0.0.1:5002/docs/ 
    # http://127.0.0.1:5002/redoc/
    
    uvicorn.run(app, host="0.0.0.0", port=5002)