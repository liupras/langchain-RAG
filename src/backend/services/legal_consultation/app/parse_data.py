#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @date    : 2025-06-28
# @description: 将数据拆条，便于进行矢量化。将每一个法律法规的内容拆分后输出为一个csv文件。

import os
import re
import pandas as pd
from util import check_dir,get_current_dir

current_dir = get_current_dir()    # 当前文件所在的目录
data_dir = os.path.join(current_dir,'data')     # 数据文件的目录

split_data_dir = os.path.join(data_dir,'split_data')     # 拆分后的数据文件的目录    
check_dir(split_data_dir)

file_meta_data = os.path.join(data_dir,'meta_data.csv')    # 元数据
content_dir = os.path.join(data_dir,'txt_utf8')     # 文本文件的目录

def clean(src):
    """清洗字符串"""
    src = re.sub(r"\s+", "", src)  # 去除空格
    src = src.replace('\u3000','')      # 去除空格
    src = src.replace(',',"，")     # 替换半角逗号为全角，防止生成csv文件时格式错乱。
    return src

def parse_content(text):
    """将文本拆条"""
    # 预处理：移除多余的空行，并按行分割
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    current_article = None
    articles = []   # 保存已经解析出来的条目内容
    max_len = 0     # 条目内容的最大长度

    # 正则表达式模式
    chapter_pattern = re.compile(r'^第[零一二三四五六七八九十百千]+章\s+(.+)$') # 匹配 "第一章 总则"
    article_pattern = re.compile(r'(^第[零一二三四五六七八九十百千]+条)') # 匹配 "第一条" 

    for line in lines:
        line = clean(line)
        if not line:
            continue

        # 尝试匹配章节标题
        chapter_match = chapter_pattern.match(line)
        if chapter_match:   # 如果匹配到，说明这一行都是章的内容，跳过不做处理。
            continue

        # 尝试匹配法条标题
        article_match = article_pattern.match(line)
        if article_match:
            if current_article is not None:
                # 保存已经解析出来的条目内容
                content = "\n".join(current_article["content"])
                if len(content) > max_len:
                    max_len = len(content)
                articles.append({"number": current_article["number"], "content": content})

            # 开启新的条目，有可能一部分内容也在本行
            article_number = clean(article_match.group(0))            
            article_content = line.replace(article_number,"")
            article_content = clean(article_content)

            article_contents = []
            if len(article_content) > 0:
                article_contents = [article_content]
            current_article = {
                "number": article_number,
                "content": article_contents
            }
        else:
            # 如果当前行不是章节或法条标题，则认为是法条内容
            if current_article is not None:
                current_article["content"].append(line)        

    if current_article is not None:
        content = "\n".join(current_article["content"])
        if len(content) > max_len:
            max_len = len(content)
        articles.append({"number": current_article["number"], "content": content})

    return articles,max_len        

def parse():
    """解析法律法规的数据文件，将每一个法律法规的内容拆分后输出为一个csv文件。
    """
    max_len = 0
    df = pd.read_csv(file_meta_data)
    for _, row in df.iterrows():
        id = str(row['id'])
        file_src = os.path.join(content_dir,f"{id}.txt")
        with open(file_src, 'r', encoding='utf-8') as file:
            text = file.read()
        articles,tmp_max_len = parse_content(text)
        #print(tmp_max_len)
        if tmp_max_len > max_len:
            max_len = tmp_max_len
        if len(articles) > 0:            
            output_file = os.path.join(split_data_dir,f"{id}.csv")
            df = pd.DataFrame(articles)
            df.to_csv(output_file, index=False)
        else:
            print(f"⚠️ {id} 无法解析，跳过。")


    print(f"✅ 已完成,最大条目长度为:{max_len}")

if __name__ == '__main__':
    parse()