#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-12-30
# @function: 生成知识库
# @version : V0.5
# @Description ：在问答的过程中，系统自动存储以往的问题和答案，产生“记忆”功能，提升会话体验。

# 参考：https://python.langchain.com/v0.2/docs/tutorials/qa_chat_history/

import bs4

from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import WebBaseLoader

persist_directory = 'chroma_langchain_db_test_2'

# 返回本地模型的嵌入。在存储嵌入和查询时都需要用到此嵌入函数。
def  get_embedding():
    # nomic-embed-text: 一个高性能开放嵌入模型，具有较大的标记上下文窗口。
    # 安装：ollama pull nomic-embed-text:latest
    # 这个模型只有274M，但实际做嵌入和检索时，感觉比llama3这样的大模型还要好。
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings

# 对文本矢量化并存储在本地
def create():

    # 加载、分块并索引博客内容来创建检索器。
    loader = WebBaseLoader(
        web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
        bs_kwargs=dict(
            parse_only=bs4.SoupStrainer(
                class_=("post-content", "post-title", "post-header")
            )
        ),
    )
    docs = loader.load()

    # 用于将长文本拆分成较小的段，便于嵌入和大模型处理。
    # 每个文本块的最大长度是1000个字符，拆分的文本块之间重叠部分为200。
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(docs)
   
    # 从文本块生成嵌入，并将嵌入存储在Chroma向量数据库中，同时设置数据库持久化路径。
    vectordb = Chroma.from_documents(documents=texts, embedding=get_embedding(),persist_directory=persist_directory)

    # 将数据库的当前状态写入磁盘，以便在后续重启时加载和使用。
    vectordb.persist()


if __name__ == '__main__':
    create()
 