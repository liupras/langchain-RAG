@echo off
setlocal

:: 设置变量
set IMAGE_NAME=zf-legal-ai-api:0.5.1
set TAR_FILE=zf-legal-ai-api-0.5.1.tar
set TAR_GZ_FILE=zf-legal-ai-api-0.5.1.tar.gz

echo 正在生成镜像...
docker build -t %IMAGE_NAME% .

echo 正在保存镜像为 tar 文件...
docker save %IMAGE_NAME% > %TAR_FILE%

echo 压缩镜像为 tar.gz 文件...
7z a -tgzip %TAR_GZ_FILE% %TAR_FILE%
del %TAR_FILE%

echo 完成！镜像已保存为 %TAR_GZ_FILE%