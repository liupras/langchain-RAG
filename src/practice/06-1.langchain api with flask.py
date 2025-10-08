#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2024-11-03
# @Description: 使用Flask做langchain的API
# @version : V0.5

'''
# 执行以下命令安装相关依赖：
pip install flask flask-restful
pip install flasgger
pip install jsonschema
'''

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.llms import OllamaLLM

from flask import Flask, jsonify, request
from flasgger import Swagger
from jsonschema import validate

# 翻译方法
def translate(language,text):
    # 1. 创建提示词模板
    system_template = "Translate the following into {language}:"
    prompt_template = ChatPromptTemplate.from_messages([
        ('system', system_template),
        ('user', '{text}')
    ])

    # 2. 创建本地大模型
    model = OllamaLLM(model="llama3.1")

    # 3. 创建解析器
    parser = StrOutputParser()

    # 4. 创建链
    chain = prompt_template | model | parser

    #5. 调用链
    result = chain.invoke({"language": language,"text":text})

    return result


# 定义请求数据json的格式
schema={
    "type": "object",
    'required': ['l','t'],
    'properties': {
        'l': {'type': 'string',"minLength": 2,"maxLength": 100},
        't': {'type': 'string',"minLength": 2,"maxLength": 1000}
    }
}

app = Flask(__name__)

#翻译API
@app.route("/trans", methods=['POST'])
def trans_api():
    # 以下注释将会被flasgger使用。
    """
    翻译文本。
    ---
    tags:
      - 翻译
    description:
        将文本翻译为目标语言。
    consumes:
        - application/json
    produces:
        - application/json
    parameters:
      - name: query
        in: body
        required: true
        description: json格式。例如：{"l":"简体中文","t":"good morning"}            
    responses:
        code==ok: 
            description: 成功。msg的值为返回的内容。
        code==err: 
            description: 失败。例如：{"code":"err","msg":"抱歉，我不知道。"} 。
    """

    try:
        j = request.get_json()
        validate(instance=j, schema=schema)
        r = translate(j["l"].strip(),j["t"].strip())
        return jsonify({"code":"ok","msg":r})
    except Exception as e:
        return jsonify({"code":"err","msg":str(e)})  

if __name__ == '__main__':
    #r = translate("简体中文","good morning")
    #print(r)

    # 设置API 文档。API文档访问地址：http://127.0.0.1:5001/apidocs/
    swagger = Swagger(app=app)

    app.run(port=5001)