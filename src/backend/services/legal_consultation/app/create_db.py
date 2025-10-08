#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2025-05-22
# @function: 对案件事实/事实查明进行矢量化
# 10498个案子中，有10355个被矢量化，出现了一点 本院查明 为空的案子。目前原因不明。

import os
from langchain_chroma import Chroma
from tqdm import tqdm
import pandas as pd
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

from config import settings
from summary import summarize
from util import get_current_dir

current_dir = get_current_dir()
embedding = OllamaEmbeddings(model=settings.embed_model_name,base_url=settings.base_url)
vectordb = Chroma(persist_directory=settings.db_path,embedding_function=embedding)

def embed_documents_in_batches(documents,ids, batch_size=10):
    """
    按批次嵌入，显示进度。
    """
    print(f'\n=====开始对{len(ids)}个文档的列进行嵌入=====')

    if not documents or len(documents) == 0:
        print("没有可处理的文档！")
        return    
    
    for i in tqdm(range(0, len(documents), batch_size), desc="嵌入进度"):
        docs = documents[i:i + batch_size]
        doc_ids = ids[i:i + batch_size]
        # 从文本块生成嵌入，并将嵌入存储在本地磁盘。
        vectordb.add_documents(documents=docs,ids=doc_ids)    

    print("处理完毕，当前数据库文档数量:", len(vectordb.get()['documents']))

def create():
    """生成矢量数据库"""
    data_dir = os.path.join(current_dir,"data")
    meta_file = os.path.join(data_dir,"meta_data.csv")
    split_dir = os.path.join(data_dir,"split_data")

    documents = []
    ids = []

    df_meta = pd.read_csv(meta_file,encoding='utf-8')
    df_meta = df_meta.map(lambda x: '' if pd.isna(x) else str(x))   # 填充空值
    print(f'\n=====开始对{len(df_meta)}个法规进行摘要 1/2=====')

    for _, row in tqdm(df_meta.iterrows(), total=df_meta.shape[0]):
        id = row["id"]
        title = row["title"]
        office = row["office"]
        publish = row["publish"]
        stage = row["stage"]
        file_data = os.path.join(split_dir,f"{id}.csv")
        df_data = pd.read_csv(file_data,encoding='utf-8')
        for _,item in df_data.iterrows():
            number = item["number"] 
            content = item["content"]
            content_new = summarize(content)
            if len(content_new) == 0:
                print(f"{title}_{number} 摘要失败！")
                continue
            doc_id = f"{id}_{number}"
            metadata = {
                "title":title,
                "number":number,
                "office":office,
                "publish":publish,
                "stage":stage        
            }
            documents.append(Document(page_content=content_new,metadata=metadata))
            ids.append(doc_id)

    print(f'\n=====开始对{len(ids)}个法规进行嵌入 1/2=====')
    embed_documents_in_batches(documents=documents,ids=ids)

    print("=====处理完毕=====")

if __name__ == '__main__':

    create()
 