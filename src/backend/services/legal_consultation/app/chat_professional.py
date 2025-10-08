#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @date    : 2025-07-02
# @description: 带有专家库支持的聊天

from langchain_ollama import OllamaEmbeddings,ChatOllama
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState, StateGraph,END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from config import settings
from common import get_trimmer,clean_response

embedding = OllamaEmbeddings(model=settings.embed_model_name,base_url=settings.base_url)
vector_store = Chroma(persist_directory=settings.db_path,embedding_function=embedding)

llm = ChatOllama(model=settings.llm_model_name_local,temperature=0, verbose=True,base_url=settings.base_url)
trimmer = get_trimmer(max_tokens=settings.llm_max_size)

# 查询矢量知识库：retrieve
from langchain_core.tools import tool
@tool(response_format="content_and_artifact",parse_docstring=True)      # docstring的内容对agent自动推理影响比较大
def retrieve(query: str):
    """检索与 query参数内容 相关的知识产权领域法律法规的信息

    Args:
        query: 要搜索的字符串。 
    """

    print(f"start retrieve:{query}")

    # 定义相似度阈值。因为这种相似性检索并不考虑相似性大小，如果不限制可能会返回相似性不大的文档， 可能会影响问答效果。
    similarity_threshold = 0.6
    retrieved_docs = vector_store.similarity_search_with_score(query, k=6)

    # 根据相似度分数过滤结果
    filtered_docs = [
        doc for doc, score in retrieved_docs if score <= similarity_threshold
    ]

    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in filtered_docs
    )

    if not serialized:
        return "抱歉，我找不到任何相关信息。", None
    else:
        return serialized, filtered_docs

# 生成可能包含要发送的工具调用的 AIMessage。
def query_or_respond(state: MessagesState):
    """生成用于检索或响应的工具调用。"""
    trimmed_messages = trimmer.invoke(state["messages"])
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(trimmed_messages)
    """
    这里会自动进行指代消解：根据上下文自动修改问题，把问题中的代词替换成上下文中的内容
    """
    response.content = clean_response(response.content)
    # MessagesState 将消息附加到 state 而不是覆盖
    return {"messages": [response]}

# 执行检索
tools = ToolNode([retrieve])

# 使用检索到的内容生成响应。
def generate(state: MessagesState):
    """生成回答"""
    # 获取生成的 ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]
    # 获取 ToolMessages 的内容，并格式化为提示词
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "你是一个精通法律法规，擅长做纠纷调解的专业人员。"
        "使用以下检索到的上下文来回答问题。 "
        "如果你不知道答案，就说你不知道。 "
        "保持答案简洁。"
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    trimmed_messages = trimmer.invoke(prompt)

    # 执行
    response = llm.invoke(trimmed_messages)
    # 去掉think部分内容
    response.content = clean_response(response.content)
    # MessagesState 将消息附加到 state 而不是覆盖
    return {"messages": [response]}

def build_graph():
    graph_builder = StateGraph(MessagesState)

    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)    

    graph = graph_builder.compile()

    # 增加记忆功能
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)

    return graph

graph = build_graph()

def ask_stream(question,thread_id="test123"):
    """提问，记录聊天历史"""

    print('---ask_stream---')
    conf = {"configurable": {"thread_id": thread_id}}
    for step in graph.stream(
        {"messages": [{"role": "user", "content": question}]},
            stream_mode="values",
            config = conf,
        ):
            step["messages"][-1].pretty_print()

def ask(question,thread_id="test123"):
    conf = {"configurable": {"thread_id": thread_id}}
    state = graph.invoke({"messages": [{"role": "user", "content": question}]},config=conf)
    return state["messages"][-1].content

if __name__ == '__main__':
    #result = retrieve("任何单位和个人不得有为他人侵犯专利权")
    questions =[
        "我开了一家小店，碰巧用的名称和对面的一样，会涉嫌侵权么？",
        "如果可能涉嫌侵权，那是违反了哪条法律呢？"
    ]
    for q in questions:
        print(ask(q))
