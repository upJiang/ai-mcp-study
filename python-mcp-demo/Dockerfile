FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制代码
COPY server.py .
COPY utils ./utils

# 创建config目录（用于挂载）
RUN mkdir -p /app/config

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=http
ENV MCP_PORT=8000
ENV KEYS_CONFIG_PATH=/app/config/keys.json

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 启动命令
CMD ["python", "server.py"]

