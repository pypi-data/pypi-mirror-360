FROM python:3.11-slim

WORKDIR /app

# 安装 curl
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 安装 asktable-mcp-server
RUN pip install --no-cache-dir asktable-mcp-server

# 暴露默认端口（SSE 模式）
EXPOSE 8095

# 设置容器启动时执行的命令
CMD ["python", "-m", "asktable_mcp_server.server", "--transport", "sse", "--port", "8095"]