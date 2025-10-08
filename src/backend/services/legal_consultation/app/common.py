#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @date    : 2025-06-18
# @description: 通用逻辑
import re

from pydantic import BaseModel,Field

class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="消息内容，不能为空。")
    thread_id: str = Field("test123", description="会话ID。")

    class Config:
        title = "聊天消息体"
        description = "与智能体聊天的消息体。"

class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, description="要翻译的文本")
    language_dst: str = Field(..., min_length=1, description="目标语言")
    language_src: str = Field("", description="源语言，可选")

def clean_response(response):
    """去除推理部分内容"""
    start_tag = "<think>"
    end_tag = "</think>"
    start_pos = response.find(start_tag)
    end_pos = response.find(end_tag)
    
    if start_pos != -1 and end_pos != -1:
        text = response[:start_pos] + response[end_pos+len(end_tag):]
        # 去掉空行
        paragraphs = text.split('\n')
        lines = [line for line in paragraphs if line.strip()]
        cleaned_text = '\n'.join(lines)
        return cleaned_text
    return response

def remove_last_parentheses_part(s):
    # 仅当字符串以 ）结尾，且包含（ 时执行处理
    if s.endswith('）') and '（' in s:
        # 从最右侧开始匹配最后一对（...）及其内容
        s = re.sub(r'（[^（]*）$', '', s)
    return s

def clean(text):
    """从大模型的返回中提取正文信息"""

    # 1：去掉 <think> 和 </think> 之间的内容（包括标签本身）
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

    # 去掉首尾空白
    text = text.strip()

    paragraphs = text.split('\n')

    # 2：去掉第一段如果以“摘要：”结尾
    if paragraphs and "摘要：" in paragraphs[0].strip():
        paragraphs = paragraphs[1:]

    # 3：去掉最后一段如果为括号注释
    if paragraphs and re.match(r'^（.*）$', paragraphs[-1].strip()):
        paragraphs = paragraphs[:-1]

    # 4: 去掉尾部包含括号的注释
    paragraphs = [remove_last_parentheses_part(line) for line in paragraphs]

    # 5: 去除空行（即只包含空白字符的行）
    lines = [line for line in paragraphs if line.strip()]
        
    # 合并为最终结果
    cleaned_summary = '\n'.join(lines)

    cleaned_summary = cleaned_summary.strip()

    return cleaned_summary

def truncate_text_by_paragraphs(text: str, max_len: int=15000) -> str:
    """
    截取分段落的结构化文本。

    Args:
        text (str): 输入的文本内容，假设段落之间以换行符分隔。
        max_len (int): 最大允许的文本长度。qwen3的token限制是40k，但是它可以快速稳定的处理文本的长度在15000左右

    Returns:
        str: 处理后的文本。
    """
    paragraphs = text.split('\n')

    # 去掉每个元素的空字符串并去掉空元素。
    paragraphs = [item.strip() for item in paragraphs if item.strip()]
    trigger_phrases = ["本院认为", "本院查明"]
    trigger_index = None

    # 1. 检查是否包含触发短语
    for i, paragraph in enumerate(paragraphs):
        if any(phrase in paragraph for phrase in trigger_phrases):
            trigger_index = i
            break

    if trigger_index is not None:
        # 如果找到触发短语，截取到触发短语的上一个段落
        text = '\n'.join(paragraphs[:trigger_index])

    # 2. 如果文本长度超过 max_len
    if len(text) > max_len:
        current_len = 0
        selected_paragraphs = []
        for paragraph in paragraphs:
            if current_len + len(paragraph) + 1 <= max_len:  # +1 是换行符的长度
                selected_paragraphs.append(paragraph)
                current_len += len(paragraph) + 1  # 更新当前长度（包括换行符）
            else:
                break  # 超过 max_len，停止截取

        text = '\n'.join(selected_paragraphs)

    return text

from langchain_core.messages import BaseMessage
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage, trim_messages

def simple_token_counter(messages: list[BaseMessage]) -> int:
    # 一个简单的估算：由于主要内容都是中文，每1个字符算一个token
    full_text = ChatPromptValue(messages=messages).to_string()
    return len(full_text)

def get_trimmer(max_tokens):
    """
    重要：请务必在在加载之前的消息之后，并且在提示词模板之前使用它。
    这里不适用大模型的精确估计，可以提升速度。
    """
    trimmer = trim_messages(
        max_tokens=max_tokens,  #设置裁剪后消息列表中允许的最大 token 数量
        strategy="last",        #指定裁剪策略为保留最后的消息，即从消息列表的开头开始裁剪，直到满足最大 token 数量限制。
        token_counter=simple_token_counter,    #通过model来计算消息中的 token 数量。
        include_system=True,    #在裁剪过程中包含系统消息（SystemMessage）
        allow_partial=False,    #不允许裁剪出部分消息，即要么保留完整的消息，要么不保留，不会出现只保留消息的一部分的情况。
        start_on="human",   #从人类消息（HumanMessage）开始进行裁剪，即裁剪时会从第一个HumanMessage开始计算 token 数量，之前的系统消息等也会被包含在内进行整体裁剪考量。
    )
    return trimmer

messages = [
    SystemMessage(content="你是个好助手"),
    HumanMessage(content="你好，我是刘大钧"),
    AIMessage(content="你好"),
    HumanMessage(content="我喜欢香草冰淇淋"),
    AIMessage(content="很好啊"),
    HumanMessage(content="3 + 3等于几？"),
    AIMessage(content="6"),
    HumanMessage(content="谢谢"),
    AIMessage(content="不客气"),
    HumanMessage(content="和我聊天有意思么？"),
    AIMessage(content="是的，很有意思"),
]

def test_trimmer(max_tokens):
    t = get_trimmer(max_tokens)
    messages_trimed = t.invoke(messages)
    print(f'messages_trimed:\n{messages_trimed}')

if __name__ == '__main__':

    test_trimmer(80)

    text_example = """这是一个段落。
    另一个段落。
    这是一个较长的段落，用于测试截取逻辑。
    本院认为，这是重要的信息。
    后续段落。"""

    max_len_example = 20

    result = truncate_text_by_paragraphs(text_example, max_len_example)
    print(result)
