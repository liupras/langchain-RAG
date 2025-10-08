#coding=utf-8
#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-12-23
# @Description: 处理token。
# @version : V0.5

'''
# 安装 PyJWT，在 Python 中生成和校验 JWT 令牌
pip install pyjwt
'''
import math

# 下面代码可以防止引用同级目录模块时出现错误：找不到模块
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

from aes import encrypt,decrypt
from config.config import config

separator = "\u2016"

# 用于JWT签名。
SECRET_KEY = config['secret']["jwt_key"]
'''
注意，不要使用本例所示的密钥，因为它不安全。
'''

# 对JWT编码解码的算法。JWT不加密，任何人都能用它恢复原始信息。
ALGORITHM = "HS256"

DEFAULT_TOKEN_EXPIRE_MINUTES = config['token']["default_expires_time"]   #默认token过期时间

# 加密签名：userid + timestamp
def get_sign(encrypted_text,access_token_expires):
    t = str(math.floor(access_token_expires.timestamp()))
    #print(f"access_token_expires is {t}")
    src_text = encrypted_text + separator + t
    return encrypt(src_text) 

from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError,ExpiredSignatureError

# 生成JWT
def create_access_token(data: dict,encrypted_text: str=None, expire_minutes: int | None = None):
    to_encode = data.copy()
    if expire_minutes is not None and expire_minutes > 0:
        expires_delta = timedelta(minutes=expire_minutes) 
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=DEFAULT_TOKEN_EXPIRE_MINUTES)
    if encrypted_text is not None and encrypted_text != "": #加密签名
        sign = get_sign(encrypted_text,expire)
        to_encode.update({"sign": sign})
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 解析并校验JWT。
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 校验JWT完整性
        sub:str = payload.get("sub")
        if sub is None or sub == "":
            raise InvalidTokenError
        sign:str = payload.get("sign")
        if sign is None or sign == "":
            raise InvalidTokenError
        exp:int = payload.get("exp")
        if exp is None or exp == 0:
            raise InvalidTokenError
        
        # 判断JWT是否过期
        now = math.floor(datetime.now(timezone.utc).timestamp())
        if now > exp:
            raise ExpiredSignatureError
        
        # 校验加密的签名
        plain_sign = decrypt(sign)
        if plain_sign is None:
            raise InvalidTokenError
        arr = plain_sign.split(separator)
        if len(arr) != 2:
            raise InvalidTokenError
        userid = arr[0]
        timestamp = int(arr[1])
        if timestamp != exp:
            raise InvalidTokenError        
        return userid    
    except Exception:
        raise InvalidTokenError