#!/bin/bash

# 容器启动脚本
set -e

echo "🚀 启动代码分享平台..."

# 等待数据库连接（如果使用外部数据库）
if [[ "$DATABASE_URI" == mysql* ]]; then
    echo "⏳ 等待数据库连接..."
    while ! nc -z ${DB_HOST:-mysql} ${DB_PORT:-3306}; do
        sleep 1
    done
    echo "✅ 数据库连接成功"
fi

# 创建必要目录
mkdir -p /app/backend/instance /app/backend/logs

# 初始化数据库
cd /app/backend
echo "🔄 初始化数据库..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('数据库表已创建')
"

# 执行数据库索引优化（如果存在）
if [ -f "/app/backend/migrations/add_search_indexes.sql" ]; then
    echo "🔍 执行数据库索引优化..."
    python -c "
import sqlite3
import os
from app import app

with app.app_context():
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite'):
        db_path = db_uri.replace('sqlite:///', '')
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            with open('migrations/add_search_indexes.sql', 'r') as f:
                conn.executescript(f.read())
            conn.close()
            print('索引优化完成')
    else:
        print('跳过SQLite索引优化（使用外部数据库）')
"
fi

echo "✅ 应用初始化完成"

# 启动Supervisor
echo "🎯 启动服务..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
