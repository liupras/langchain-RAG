#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-10-10
# @Description: 使用langserve让langchain提供API，与本地大模型聊天（用langchian开发）
# @version : V0.5

# 参考：https://python.langchain.com/v0.2/docs/tutorials/llm_chain/

# pip install "langserve[all]"

#!/usr/bin/env python
from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.llms import OllamaLLM
from langserve import add_routes

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


# 5. App 定义
app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="使用 LangChain 的 Runnable 接口的简单 API 服务器。",
)

# 6. 添加链的路由
add_routes(
    app,
    chain,
    path="/translate",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8010)