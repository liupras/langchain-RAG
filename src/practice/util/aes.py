#coding=utf-8
#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-12-22
# @Description: 加密解密算法。
# @version : V0.5

'''
pip install pycryptodome
'''

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

# 将上级目录加入path，方便引用response等上级目录的模块
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from config.config import config

# 密钥和初始化向量 (IV) 必须是固定长度
key = config['secret']["aes_key"].encode('utf-8')
iv = config['secret']["aes_iv"].encode('utf-8')
'''
注意，不要使用本例所示的key和iv，因为它不安全。
'''

# AES加密
def encrypt(text):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_text = pad(text.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded_text)
    return base64.b64encode(encrypted).decode('utf-8')

# AES解密
def decrypt(encrypted_text):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decoded_data = base64.b64decode(encrypted_text)
    decrypted = unpad(cipher.decrypt(decoded_data), AES.block_size)
    return decrypted.decode('utf-8')


if __name__ == "__main__":
    text = "hello_world"
    encrypted_text = encrypt(text)
    decrypted_text = decrypt(encrypted_text)

    print(f"原始字符串: {text}")
    print(f"加密后: {encrypted_text}")
    print(f"解密后: {decrypted_text}")
