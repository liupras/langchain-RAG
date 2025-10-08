#!/bin/bash

# 停止应用
if [ -f app.pid ]; then
    PID=$(cat app.pid)
    kill $PID 2>/dev/null
    rm -f app.pid
    echo "应用已停止"
else
    echo "未找到运行中的进程"
fi