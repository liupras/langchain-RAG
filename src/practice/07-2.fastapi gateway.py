#coding=utf-8
#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-11-07
# @Description: 使用fastapi-gateway实现简单的应用网关
# @version : V0.5

from fastapi import FastAPI, Request,HTTPException
import httpx

#  定义超时时间，单位：秒
time_out = 30

# 创建一个FastAPI实例
app = FastAPI()

# 定义服务
services = {
    "translation": "http://127.0.0.1:5001",
    # 可以在这里添加其它服务地址
}
'''
services的key是服务名称，客户端在请求时传入服务名称，本网关再根据服务名称找到对应的服务地址
'''

# 接收客户端请求并转发到后端服务
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, path: str, request: Request):
    '''
    !注意：网关并未将header转发给后端服务，这样比较简单。
    '''
    
    if service not in services:
        raise HTTPException(status_code=401, detail="未找到该服务")
    
    #headers = dict(request.headers)

    # 从客户端请求中获取数据
    client_request_data = await request.json()
        
    service_url = services[service]
    url = f"{service_url}/{path}"   

    # 使用 httpx 将请求转发到后端服务，非阻塞，不过在我的配置一般的开发机上没有发现和阻塞式调用在性能上有多少区别。
    async with httpx.AsyncClient() as client:
        '''
        !注意：httpx.AsyncClient默认的timeout为5秒，在调用基于大模型的后端服务时经常超时，所以这里设置超时时间为30秒
        '''
        response = await client.post(url=url, json=client_request_data,timeout=time_out)
        #print(response)
        return response.json()

 
# 启动网关
if __name__ == "__main__":
    import uvicorn

    # 交互式API文档地址：
    # http://127.0.0.1:8000/docs/ 
    # http://127.0.0.1:8000/redoc/
    uvicorn.run(app, host="0.0.0.0", port=8000)