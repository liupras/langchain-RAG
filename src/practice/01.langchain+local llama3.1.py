#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-09-25
# @function: 在langchain中使用本地部署的llama3.1 8b模型
# @version : V0.5
# @Reference : https://python.langchain.com/docs/integrations/llms/ollama/

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# 在调用时替换{question}为实际的提问内容。
template = """Question: {question}

Answer: Let's think step by step.

请用简体中文回复。
"""

# ChatPromptTemplate是LangChain中的一个模板类，用于定义一个对话提示模板。
prompt = ChatPromptTemplate.from_template(template)

# 使用本地部署的lama3.1
model = OllamaLLM(model="llama3.1")

# 创建一个简单的链：prompt的输出会传递给model，然后model会根据prompt的输出进行处理
chain = prompt | model

# 调用链，传递输入数据并执行链中的所有步骤。
# 该输入中的question键值对被传递到prompt模板中，从而生成完整的对话提示："Question: Langchain是什么?"。
result = chain.invoke({"question": "Langchain是什么?"})

print(result)