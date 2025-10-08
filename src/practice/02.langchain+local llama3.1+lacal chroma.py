#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-09-30
# @function: langchian+本地llama3.1+本地chroma做RAG(RAG，Retrieval Augmented Generation,即：增强生成)
# @version : V0.5

# 参考：
# https://python.langchain.com/docs/integrations/vectorstores/chroma/
# https://github.com/hwchase17/chroma-langchain/blob/master/persistent-qa.ipynb

from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain.chains import VectorDBQA
from langchain.document_loaders import TextLoader

persist_directory = 'chroma_langchain_db_test'
model_name = "llama3.1"

# 定义嵌入。在存储嵌入和查询时都需要用到此嵌入函数。
def  get_embedding():
    embeddings = OllamaEmbeddings(model=model_name)
    return embeddings

# 对文本矢量化并存储在本地
def create_db():

    # 用来加载文本文件。
    # 指定文件使用tf-8编码读取，以确保正确处理非ASCII字符。
    loader = TextLoader('data/state_of_the_union.txt',encoding='utf-8')
    documents = loader.load()

    # 用于将长文本拆分成较小的段，便于嵌入和大模型处理。
    # 每个文本块的最大长度是1000个字符，拆分的文本块之间没有重叠部分。
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
   
    # 从文本块生成嵌入，并将嵌入存储在Chroma向量数据库中，同时设置数据库持久化路径。
    vectordb = Chroma.from_documents(documents=texts, embedding=get_embedding(),persist_directory=persist_directory)

    # 将数据库的当前状态写入磁盘，以便在后续重启时加载和使用。
    vectordb.persist()

# create_db()

def ask(query):

    # 创建大模型实例
    model = OllamaLLM(model=model_name)

    # 使用本地矢量数据库创建矢量数据库实例
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=get_embedding())

    # 处理基于向量数据库的查询回答任务。
    # "stuff"：意味着模型将所有的上下文一次性处理。
    qa = VectorDBQA.from_chain_type(llm=model, chain_type="stuff", vectorstore=vectordb)
    
    result = qa.run(query)
    return result

query = "What did the president say about Ketanji Brown Jackson"
r = ask(query)
print (r)
