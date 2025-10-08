#!/bin/bash

set -e  # 遇到错误立即退出

IMAGE_NAME="zf-legal-ai-api:0.5.1"
TAR_GZ_FILE="zf-legal-ai-api-0.5.1.tar.gz"

echo "生成镜像..."
sudo docker build -t "$IMAGE_NAME" .

echo "保存镜像..."
sudo docker save "$IMAGE_NAME" | gzip > "$TAR_GZ_FILE"