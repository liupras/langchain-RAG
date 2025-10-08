#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @date    : 2025-07-29
# @description: 万能翻译

from openai import OpenAI
from config import settings

client = OpenAI(
    api_key=settings.dashscope_api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def build_prompt(language_src:str,language_dst:str,text:str):
    prompt_sysytem = "你是一个专业的翻译助手。"
    if language_src:
        prompt_user = f"""你是一个专业的翻译助手。请将以下文本从 {language_src} 翻译成 {language_dst}。只输出翻译结果，不要包含任何其他解释、说明或额外文本。

        原文：
        {text}

        翻译："""
    else:
        prompt_user = f"""你是一个专业的翻译助手。请将以下文本翻译成 {language_dst}。只输出翻译结果，不要包含任何其他解释、说明或额外文本。

        原文：
        {text}

        翻译："""

    return [
            {"role": "system", "content": prompt_sysytem},
            {"role": "user", "content": prompt_user}
    ]

def stream_generator(language_src:str,language_dst:str,text:str):    
    full_content = ""

    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=build_prompt(language_src,language_dst,text),
            stream=True,
            # 如使用开源版模型，可启用以下参数
            # extra_body={"enable_thinking": False},
        )

        for chunk in completion:
            if chunk.choices:
                delta = chunk.choices[0].delta.content
                full_content += delta
                print(delta)
                yield {
                    "event": "message",
                    "data": delta
                }

        yield {
            "event": "end",
            "data": "[[END]]"
        }

    except Exception as e:
        yield {
            "event": "error",
            "data": f"翻译失败: {str(e)}"
        }


def trans_stream(language_src:str,language_dst:str,text:str):
    """翻译方法。流式返回结果"""
    if not language_dst or not text:
        return ""
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=build_prompt(language_src,language_dst,text),
        stream=True,
        # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
        # 使用Qwen3开源版模型时，请将下行取消注释，否则会报错
        # extra_body={"enable_thinking": False},
    )

    full_content = ""
    print("流式输出内容为：")
    for chunk in completion:
        # 如果stream_options.include_usage为True，则最后一个chunk的choices字段为空列表，需要跳过（可以通过chunk.usage获取 Token 使用量）
        if chunk.choices:
            full_content += chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content)
    print(f"完整内容为：{full_content}")

def trans(language_src:str,language_dst:str,text:str):
    """翻译方法"""
    if not language_dst or not text:
        return ""
    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=build_prompt(language_src,language_dst,text)
        )
        print(completion.choices[0].message.content)
        return completion.choices[0].message.content
    except Exception as e:
        print(e)
        return "翻译失败..."

if __name__ == '__main__':
    trans("","英文","他不是一个坏人。")