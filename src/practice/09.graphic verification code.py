#coding=utf-8
#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2025-01-03
# @Description: 生成和验证图形验证码。
# @version : V0.5

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO

from captcha import generate_captcha
from ttlcache import Cache,Error
_cache = Cache(max_size=30, ttl=300)    # 30个缓存，每个缓存5分钟

app = FastAPI()

@app.get("/captcha")
def get_captcha():

    captcha_id,captcha_text,captcha_image =  generate_captcha()
    print(f"生成的验证码: {captcha_id} {captcha_text}")
    _cache.add(captcha_id,(captcha_text,captcha_image))

    # 返回图片流
    buffer = BytesIO()
    captcha_image.save(buffer, format="PNG")
    buffer.seek(0)
    headers = {"X-Captcha-ID": captcha_id}
    return StreamingResponse(buffer, media_type="image/png", headers=headers)


@app.post("/verify-captcha")
async def verify_captcha(captcha_id: str, captcha_input: str):
    error,value = _cache.get(captcha_id)
    if error != Error.OK:
        raise HTTPException(status_code=400, detail="Invalid or expired captcha ID")
    
    captcha_text = value[0]

    if not captcha_text:
        raise HTTPException(status_code=400, detail="Invalid or expired captcha ID")

    if captcha_input.upper() != captcha_input.upper():
        raise HTTPException(status_code=400, detail="Incorrect captcha")

    return {"message": "Captcha verified successfully"}


# 交互式API文档地址：
# http://127.0.0.1:7000/docs/ 
# http://127.0.0.1:7000/redoc/
if __name__ == "__main__":    

    import uvicorn    
    uvicorn.run(app, host="0.0.0.0", port=7000)

    