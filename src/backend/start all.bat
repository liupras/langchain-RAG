@echo off
chcp 65001
echo start all...

REM 启动API网关和所有服务

REM 切换到当前批处理文件所在的目录
cd /d %~dp0

echo 启动翻译服务
start "翻译服务"  "services\translation\start.bat"

echo 启动咨询服务
start "咨询服务" "services\consulting\start.bat"

echo 启动法律咨询服务
start "法律咨询服务" "services\legal_consultation\start.bat"

echo 启动网关
start "网关" "gateway\start.bat"

pause