@echo off
chcp 65001
echo start gateaway

REM 切换到当前批处理文件所在的目录
cd /d %~dp0

echo 激活虚拟环境...
call .venv\Scripts\activate

echo 启动API...
python "api gateway.py"
