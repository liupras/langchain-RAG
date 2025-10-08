#coding=utf-8
#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-11-08
# @Description: 使用fastapi实现oauth2.0用户认证-实现简单的 Password 和 Bearer 验证。
# @version : V0.5

'''
[FastAPI 安全性](https://fastapi.tiangolo.com/zh/tutorial/security/)
[理解OAuth2.0](https://www.ruanyifeng.com/blog/2014/05/oauth_2_0.html)
'''
'''
OAuth2 规范要求使用密码流时，客户端或用户必须以表单数据形式发送 username 和 password 字段。因此，不能使用 JSON 对象。
并且，这两个字段必须命名为 username 和 password。
'''

'''依赖项
pip install python-multipart
'''
from fastapi import Depends, FastAPI,HTTPException,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Union

# 模仿用户数据库
fake_users_db = {
    "liu": {
        "username": "liu",
        "full_name": "Jack Liu",
        "email": "liupras@gmail.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "wang": {
        "username": "wang",
        "full_name": "Mike Wang",
        "email": "56008507@qq.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

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

# 加密密码
def fake_hash_password(password: str):
    '''
    使用hash加密后，即便是数据库被盗，窃贼无法获取用户的明文密码，得到的只是哈希值。
    '''
    return "fakehashed" + password

# 使用 OAuth2 的 Password 流以及 Bearer 令牌（Token）。
# tokenUrl="token" 指向的是暂未创建的相对 URL token。这个相对 URL 相当于 ./token。
# 此设置将会要求客户端把 username 与password 发送至 API 中指定的 URL：http://127.0.0.1:8000/token 。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 根据token（即：username）返回用户信息
def fake_decode_token(token):
    # 用username明文做token没有任何安全保障
    user = get_user(fake_users_db, token)
    return user

# 根据token获取当前登录的用户信息
# 该函数接收 str 类型的令牌，并返回 Pydantic 的 User 模型
async def get_current_user(token: str = Depends(oauth2_scheme)):
    '''
    安全和依赖注入的代码只需要写一次。各个端点可以使用同一个安全系统。
    '''
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
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

# 登录方法
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    '''
    OAuth2PasswordRequestForm 是用以下几项内容声明表单请求体的类依赖项：

    username
    password
    scope、grant_type、client_id等可选字段。
    '''
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # 响应返回的内容应该包含 token_type。本例中用的是BearerToken，因此， Token 类型应为bearer。
    return {"access_token": user.username, "token_type": "bearer"}

# 获取用户信息
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    '''
    此处把 current_user 的类型声明为 Pydantic 的 User 模型。
    这有助于在函数内部使用代码补全和类型检查。
    get_current_user 依赖项从子依赖项 oauth2_scheme 中接收 str 类型的 toke。
    '''
    return current_user

# 测试用户是否登录
@app.get("/items")
async def read_items(token: str = Depends(oauth2_scheme)):
    '''
    Depends 在依赖注入系统中处理安全机制。    
    FastAPI 校验请求中的 Authorization 请求头，核对请求头的值是不是由 Bearer ＋ 令牌组成， 并返回令牌字符串（str）。
    如果没有找到 Authorization 请求头，或请求头的值不是 Bearer ＋ 令牌。FastAPI 直接返回 401 错误状态码（UNAUTHORIZED）。
    '''

    return {"token": token}

if __name__ == "__main__":
    import uvicorn

    # 交互式API文档地址：
    # http://127.0.0.1:8000/docs/ 
    # http://127.0.0.1:8000/redoc/
    uvicorn.run(app, host="0.0.0.0", port=8000)