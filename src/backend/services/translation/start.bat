@echo off
chcp 65001
echo start translation service

REM 切换到当前批处理文件所在的目录
cd /d %~dp0

echo 激活虚拟环境...
call .venv\Scripts\activate

echo 启动翻译服务...
python api.py