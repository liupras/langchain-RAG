#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @date    : 2025-05-22
# @description: 对太长的基本案情内容进行摘要，缩短内容，以便大模型矢量化

from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd

from common import clean,truncate_text_by_paragraphs

from config import settings

# 初始化本地 Ollama 的 LLM
llm = ChatOllama(
    model=settings.llm_model_name_local,     
    temperature=0.0,
    verbose=True,
    base_url=settings.base_url
)

def summarize(src,embed_max_size = settings.embed_max_size):
    """对司法判例文本进行摘要，主要用于案件事实。

    max_size: 摘要后的字符长度，以限制它小于矢量化大模型的token size
    """
    
    if not src or pd.isna(src):
        return ""

    if len(src) <= embed_max_size:
        return src
    if len(src) > settings.llm_max_size:
        src = truncate_text_by_paragraphs(src,settings.llm_max_size)

    prompt = PromptTemplate.from_template("""
        你是一位专业的法律顾问助手，擅长理解和提炼法律条文的核心内容。
        请根据以下提供的法律法规条文内容，进行摘要整理，生成简洁的摘要文本。
        - 要求语言准确、表达简明、逻辑清晰，适合非法律专业人士快速了解该条文的关键信息，同时保留法律要点。
        - 摘要内容控制在{max_size}字符以内。

        请阅读以下法律条文，并生成摘要：
                                       
        {input}
        """)
    
    summarize_chain = prompt | llm | StrOutputParser()

    try:
        summary = summarize_chain.invoke({"input": src,"max_size":embed_max_size})
        if len(summary) == 0:
            print(f"{src}摘要失败，返回内容为空！")
        s = clean(summary)
        if len(s)> embed_max_size:
            print(f"{src}清洗失败，清洗完毕后内容为空！")
            return ""
        else:
            return s
    except Exception as e:
        print(e)
    return ""

if __name__ == '__main__':

    src="""
        以下知识产权创造和运用活动，可以申请知识产权促进专项资金支持：
        （一）符合产业发展方向的知识产权申请、注册、登记等活动；
        （二）具有市场应用前景的小微企业知识产权转化实施、小微企业与武汉地区高等学校合作的知识产权转化；
        （三）企业知识产权质押贷款贴息、保险费补贴和对担保机构的风险补偿；
        （四）知识产权优势企业、示范园区、行业联盟、产学研协同创新培育；
        （五）知识产权预警导航等信息利用、知识产权运营和商用化等活动；
        （六）其他重大知识产权创造和运用活动。
    """

    text = summarize(src,embed_max_size=100)
    print(text)