@echo off
chcp 65001
echo start legal_consultation service

REM 切换到当前批处理文件所在的目录
cd /d %~dp0

echo 激活虚拟环境...
call .venv\Scripts\activate

echo 启动服务
.venv\Scripts\python "app\main.py"
