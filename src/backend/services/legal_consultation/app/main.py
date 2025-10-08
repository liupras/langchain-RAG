#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @date    : 2025-06-29
# @function: 用websocket显示LLM的输出流

import logging
import os,sys
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from config import settings
from util import check_dir

# 读取日志级别（可通过环境变量控制）
log_level = os.getenv(settings.log_level, "INFO").upper()
log_dir = os.path.join(os.path.dirname(__file__), "logs")
check_dir(log_dir)

# 配置日志
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),              # 输出到 stdout
        logging.FileHandler(os.path.join(log_dir, "app.log"), mode="a")        # 输出到文件（可选）
    ]
)

logger = logging.getLogger("zf-legal-ai-api")
       
from fastapi import FastAPI, WebSocket,HTTPException,Request,Query
from fastapi.responses import HTMLResponse,FileResponse
from fastapi.responses import JSONResponse

app = FastAPI(title="多元纠纷化解AI接口",description="中国政法大学多元纠纷化解智能法制技术创新实验平台AI接口。",version="0.5.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境建议限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 如果是 HTTPException，就直接返回它的 status_code 和 detail
    if isinstance(exc, HTTPException):
        logger.warning(f"⚠️ HTTP异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    # 其它异常统一为 500
    logger.exception("❌ 未处理异常:")
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"}
    )

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    file_path = os.path.join(os.path.dirname(__file__), "./static/favicon-48x48.png")
    return FileResponse(file_path)

@app.get("/chat",tags=["测试客户端"],summary="返回聊天的前端界面")
async def get_chat():
    """返回聊天页面
    """

    file_path = os.path.join(os.path.dirname(__file__), "./static/chat_pro.html")
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/translate",tags=["测试客户端"],summary="返回翻译的前端界面")
async def get_translate():
    """返回翻译页面
    """

    file_path = os.path.join(os.path.dirname(__file__), "./static/translate.html")
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

from common import MessageRequest
from chat_professional import ask as ask_pro

@app.post("/chat",tags=["AI接口"],summary="咨询AI调解员接口",description="调用此接口咨询AI调解员，支持多轮会话。")
def chat(req: MessageRequest):
    """AI调解员对话接口
    """
    logger.info(f"收到用户消息: {req.message}")
    reply = ask_pro(question=req.message,thread_id=req.thread_id)
    return {"reply": reply}

from translate import stream_generator
from common import TranslateRequest
@app.post("/translate_stream",tags=["AI接口"],summary="翻译接口，流式返回内容",description="可以不用指定源语言，用中文指定目标语言，即可完成翻译。")
async def stream_translation(req: TranslateRequest):
    return EventSourceResponse(stream_generator(language_src=req.language_src,language_dst=req.language_dst,text=req.text))

from translate import trans
@app.post("/translate",tags=["AI接口"],summary="翻译接口",description="可以不用指定源语言，用中文指定目标语言，即可完成翻译。")
async def translation(req: TranslateRequest):
    return trans(language_src=req.language_src,language_dst=req.language_dst,text=req.text)

'''
from chat_general import ask_stream_async
from starlette.websockets import WebSocketDisconnect
import asyncio

async def ask(question,websocket=None):
    """与大模型聊天，流式输出"""

    async for r in ask_stream_async(query=question):
        print(r,end="|",flush=True)
        if websocket is not None:
            await websocket.send_json({"reply": r})
            await asyncio.sleep(0.1)    # sleep一下后，前端就可以一点一点显示内容。

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            user_message = data.get("message", "")
            logger.info(f"收到用户消息: {user_message}")
            await ask(user_message,websocket=websocket)
            """
            reply_message = ask(user_message)
            await websocket.send_json({"reply": reply_message})
       
            """
    except WebSocketDisconnect as e:
        logger.exception(f"客户端断开连接: code={e.code}")
    except Exception as e:
        logger.exception(f"❌ 发生异常: {e}")
'''

import uvicorn

if __name__ == '__main__':

    # 交互式API文档地址：
    # http://127.0.0.1:11014/docs/ 
    # http://127.0.0.1:11014/redoc/
    
    uvicorn.run(app, host="0.0.0.0", port=11014)