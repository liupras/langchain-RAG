#coding=utf-8
#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-12-23
# @Description: 处理password。
# @version : V0.5

'''
# Passlib 是处理密码哈希的 Python 包，支持很多安全哈希算法及配套工具。
# 本教程推荐的算法是 Bcrypt。
pip install passlib[bcrypt]
'''

from passlib.context import CryptContext

# 使用bcrypt加密密码：每次加密都会生成不同的哈希值。
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 校验密码：校验接收的密码是否匹配存储的哈希值。
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 加密密码
def get_password_hash(password):
    '''
    使用hash加密后，即便是数据库被盗，窃贼无法获取用户的明文密码，得到的只是哈希值。
    哈希是指把特定内容（本例中为密码）转换为乱码形式的字节序列（其实就是字符串），但这个乱码无法转换回传入的密码。
    '''
    return pwd_context.hash(password)