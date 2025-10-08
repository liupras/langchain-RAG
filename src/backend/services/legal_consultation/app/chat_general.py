#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @date    : 2025-06-29
# @description: 一般的聊天

from langchain_ollama import ChatOllama
from config import settings
from common import get_trimmer,clean_response
model = ChatOllama(model=settings.llm_model_name_local,temperature=0.3,verbose=True,base_url=settings.base_url)

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个精通法律法规，擅长做纠纷调解的专业人员。",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

from typing_extensions import Annotated, TypedDict
from langgraph.graph.message import add_messages
from typing import Sequence
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph

def build_app(max_tokens=settings.llm_max_size): 

    def call_model(state: State):
        trimmer = get_trimmer(max_tokens=max_tokens)
        trimmed_messages = trimmer.invoke(state["messages"])
        prompt = prompt_template.invoke(
            {"messages": trimmed_messages}
        )
        response = model.invoke(prompt)
        if isinstance(response,AIMessage):
            response.content = clean_response(response.content)
        return {"messages": [response]}

    workflow = StateGraph(state_schema=State)
    workflow.add_edge(START, "model")
    workflow.add_node("model", call_model)

    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app

app = build_app(settings.llm_max_size)

from langchain_core.messages import HumanMessage

def ask(thread_id,query):
    """提问"""
    config = {"configurable": {"thread_id": thread_id}}
    print(f"开始提问: {query}")
    output = app.invoke(
        {"messages": [HumanMessage(query)]},
        config,
    )
    content = output["messages"][-1].content
    return content

def ask_stream(query,thread_id="test"):
    """以stream方式回复"""
    in_think = False
    is_first_line = False

    config = {"configurable": {"thread_id": thread_id}}      
    for chunk, _ in app.stream(
        {"messages":[HumanMessage(content=query)]}, 
        config = config,
        stream_mode="messages",
    ):
        if isinstance(chunk, AIMessage):
            content = chunk.content
            #print(content,end='')
            if content == "<think>":
                in_think = True
            elif content == "</think>":
                in_think = False
                is_first_line = True
            else:
                if not in_think:
                    if is_first_line and content == '\n\n':
                        is_first_line = False
                    else:
                        yield content

async def ask_stream_async(query,thread_id="test"):
    """异步方法

    该方法可以保障在服务器端可以正常运行，不会卡死却不报错！
    """    
    in_think = False
    is_first_line = False

    config = {"configurable": {"thread_id": thread_id}}      
    async for chunk, _ in app.astream(
        {"messages":[HumanMessage(content=query)]}, 
        config = config,
        stream_mode="messages",
    ):
        if isinstance(chunk, AIMessage):
            content = chunk.content
            #print(content,end='')
            if content == "<think>":
                in_think = True
            elif content == "</think>":
                in_think = False
                is_first_line = True
            else:
                if not in_think:
                    if is_first_line and content == '\n\n':
                        is_first_line = False
                    else:
                        yield content


if __name__ == '__main__':
    thread_id = "liu123"
    messages=[
        "你好，我是刘大钧",
        "我喜欢香草冰淇淋",
        "3 + 3等于几？",
        "和我聊天有意思么？",
        "我叫什么名字？",
        "我问过什么数学问题？"
    ]
    for message in messages:
        #ai_message = ask(thread_id=thread_id,query=message)
        #print(ai_message)
        for r in ask_stream(query=message):
            if r is not None:
                print (r,end='')         
                #print (r, end="|")
        print('\n\n')
    