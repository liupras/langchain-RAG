#!/bin/bash

# 设置工作目录
cd /opt/my_project || exit

# 激活虚拟环境
source .venv/bin/activate

# 启动应用
nohup python3 ./app/main.py > app.log 2>&1 &

# 输出PID方便管理
echo $! > app.pid

echo "应用已启动，PID: $(cat app.pid)"