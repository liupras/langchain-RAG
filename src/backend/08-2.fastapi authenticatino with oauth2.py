#coding=utf-8
#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-11-08
# @Description: 使用fastapi实现oauth2.0用户认证-实现密码哈希与 Bearer JWT 令牌验证。
# @version : V0.5

'''
[FastAPI 安全性](https://fastapi.tiangolo.com/zh/tutorial/security/)
OAuth是一个关于授权（authorization）的开放网络标准，在全世界得到广泛应用。比如：微信登录、Facebook，Google，Twitter，GitHub等。
OAuth2 规范要求使用密码流时，客户端或用户必须以表单数据形式发送 username 和 password 字段。因此，不能使用 JSON 对象。
并且，这两个字段必须命名为 username 和 password。
[理解OAuth2.0](https://www.ruanyifeng.com/blog/2014/05/oauth_2_0.html)
JWT 即JSON 网络令牌（JSON Web Tokens）是目前最流行的跨域认证解决方案。它在服务端将用户信息进行签名（如果有保密信息也可以加密后再签名），这样可以防止它被篡改。
每次客户端提交请求时，都附带JWT内容，这样服务端可以直接读取用户信息，而不用必须从服务器端的会话中获取。
[JSON Web Token 入门教程](https://ruanyifeng.com/blog/2018/07/json_web_token-tutorial.html)
'''

from fastapi import Body, Depends, FastAPI, HTTPException,status,Request
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel

from typing import  Union
from typing import Annotated

from gateway.config.config import config
ACCESS_TOKEN_EXPIRE_MINUTES = config["token"]["expires_time"]

# 加载用户数据库
import json

with open('gateway/common/users.json', 'r', encoding='utf-8') as file:
    fake_users_db = json.load(file)

# Token实体
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# 用户实体
class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str
    
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
'''
UserInDB(**user_dict) 是指：

直接把 user_dict 的键与值当作关键字参数传递，等效于：

UserInDB(
    username = user_dict["username"],
    email = user_dict["email"],
    full_name = user_dict["full_name"],
    disabled = user_dict["disabled"],
    hashed_password = user_dict["hashed_password"],
)
'''

from gateway.util.password import verify_password 

# 认证用户
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# 使用 OAuth2 的 Password 流以及 Bearer 令牌（Token）。
# tokenUrl="token" 指向的是暂未创建的相对 URL token。这个相对 URL 相当于 ./token。
# 此设置将会要求客户端把 username 与password 发送至 API 中指定的 URL：http://127.0.0.1:8000/token 。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from gateway.util.token import decode_access_token

# 根据token获取当前登录的用户信息
# 该函数接收 str 类型的令牌，并返回 Pydantic 的 User 模型
async def get_current_user(token: str = Depends(oauth2_scheme)):
    '''
    安全和依赖注入的代码只需要写一次。各个端点可以使用同一个安全系统。
    '''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        # 在JWT 规范中，sub 键的值是令牌的主题。
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except Exception:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# 获取当前登录用户信息，并检查是否禁用
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    '''
    在端点中，只有当用户存在、通过身份验证、且状态为激活时，才能获得该用户信息。
    '''
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# 创建一个FastAPI实例
app = FastAPI()

# 允许跨域访问
from fastapi.middleware.cors import CORSMiddleware
origins = config["origins"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 打印请求日志，可用于和客户端调试
async def log_request_details(request: Request):
    client_host = request.client.host
    client_port = request.client.port
    method = request.method
    url = request.url
    headers = request.headers
    body = None
    if request.form:    
        body = await request.form()
    elif request.body:
        body = await request.body()

    print(f"Client: {client_host}:{client_port}")
    print(f"Method: {method} URL: {url}")
    print(f"Headers: {headers}")
    print(f"Body: {body if body else 'No Body'}")


from gateway.util.token import create_access_token

# 登录方法
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),remember: bool|None=Body(None),log_details: None = Depends(log_request_details))-> Token:
    '''
    OAuth2PasswordRequestForm 是用以下几项内容声明表单请求体的类依赖项：

    username
    password
    scope、grant_type、client_id等可选字段。
    '''
    
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或者密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    m = 0
    if remember:
        m = ACCESS_TOKEN_EXPIRE_MINUTES
    
    # 在JWT 规范中，sub 键的值是令牌的主题。
    access_token = create_access_token(data={"sub": user.username},encrypted_text=user.userid, expire_minutes=m)

    # 响应返回的内容应该包含 token_type。本例中用的是BearerToken，因此， Token 类型应为bearer。
    return Token(access_token=access_token, token_type="bearer")


# 获取用户信息
@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''
    此处把 current_user 的类型声明为 Pydantic 的 User 模型。
    这有助于在函数内部使用代码补全和类型检查。
    get_current_user 依赖项从子依赖项 oauth2_scheme 中接收 str 类型的 toke。
    '''
    return current_user

# 测试用户是否登录
@app.get("/users/me/items")
async def read_own_items(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''
    Depends 在依赖注入系统中处理安全机制。    
    FastAPI 校验请求中的 Authorization 请求头，核对请求头的值是不是由 Bearer ＋ 令牌组成， 并返回令牌字符串（str）。
    如果没有找到 Authorization 请求头，或请求头的值不是 Bearer ＋ 令牌。FastAPI 直接返回 401 错误状态码（UNAUTHORIZED）。
    '''

    return [{"item_id": "Foo", "owner": current_user.username}]


if __name__ == "__main__":
    import uvicorn

    # 交互式API文档地址：
    # http://127.0.0.1:5001/docs/ 
    # http://127.0.0.1:5001/redoc/
    uvicorn.run(app, host="0.0.0.0", port=8000)