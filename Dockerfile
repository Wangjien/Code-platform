# Dockerfile - 使用预构建的前端
# 注意：需要先在本地运行 cd frontend && npm run build
FROM python:3.9-slim

# 安装系统依赖（包括 gcc 用于编译 psutil）
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 创建应用目录
WORKDIR /app

# 复制后端代码和预构建的前端
COPY backend/ ./backend/
COPY frontend/dist ./frontend/dist/

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制配置文件
COPY docker/nginx.conf /etc/nginx/sites-available/default
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# 创建必要目录
RUN mkdir -p /app/backend/instance /app/backend/logs /var/log/supervisor

# 设置环境变量
ENV PYTHONPATH=/app/backend
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/api/health || exit 1

# 启动脚本
CMD ["/start.sh"]
