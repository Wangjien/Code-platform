# Docker 容器化部署指南

## 🎯 概述

本文档提供完整的Docker容器化部署方案，让你能够**一键部署**代码分享平台。

## 📦 部署架构

```
┌─────────────────────────────────────────┐
│                Docker容器                 │
├─────────────────────────────────────────┤
│  Nginx (80端口)                         │
│    ↓ 反向代理                           │
│  Frontend (静态文件)                     │
│  Backend (Flask API :5000)             │
│    ↓ 数据存储                           │
│  SQLite/MySQL + Redis                  │
└─────────────────────────────────────────┘
```

## 🚀 快速开始

### 方式一：一键部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/your-username/代码分享平台.git
cd 代码分享平台

# 2. 一键部署（开发环境 + SQLite）
./deploy.sh dev sqlite

# 3. 一键部署（生产环境 + MySQL）
./deploy.sh prod mysql
```

**就这么简单！** 🎉

### 方式二：手动部署

```bash
# 1. 配置环境变量
cp .env.docker .env
vim .env  # 修改配置

# 2. 启动服务
docker-compose up -d

# 3. 检查状态
docker-compose ps
```

## ⚙️ 配置说明

### 环境变量配置

编辑 `.env` 文件：

```env
# 基础配置
JWT_SECRET_KEY=your-super-secure-jwt-key
SECRET_KEY=your-super-secure-app-key

# 数据库选择（三选一）
# 1. SQLite（简单）
DATABASE_URI=sqlite:///instance/bio_code_share.db

# 2. MySQL容器（推荐）
DATABASE_URI=mysql+pymysql://app_user:password@mysql:3306/bio_code_share

# 3. 外部MySQL
DATABASE_URI=mysql+pymysql://user:password@external-host:3306/database

# 跨域配置
ALLOWED_ORIGINS=http://localhost:8080,https://yourdomain.com
```

### 部署模式选择

#### 🔧 开发模式
```bash
./deploy.sh dev sqlite
```
- **特点**: 快速启动、适合开发调试
- **数据库**: SQLite（无需额外配置）
- **访问地址**: http://localhost:8080

#### 🏭 生产模式
```bash
./deploy.sh prod mysql
```
- **特点**: 高性能、适合生产环境
- **数据库**: MySQL + Redis
- **访问地址**: http://localhost:8080

## 📋 服务管理

### 基础命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 完全清理（包括数据）
docker-compose down -v
```

### 高级操作

```bash
# 仅重启应用服务
docker-compose restart app

# 查看应用日志
docker-compose logs -f app

# 进入容器调试
docker-compose exec app bash

# 数据库备份（MySQL）
docker-compose exec mysql mysqldump -u app_user -p bio_code_share > backup.sql

# 数据库恢复
docker-compose exec mysql mysql -u app_user -p bio_code_share < backup.sql
```

## 🔍 健康检查

### 自动健康检查
容器内置健康检查，自动监控服务状态：

```bash
# 手动检查应用状态
curl http://localhost:8080/health
```

返回示例：
```json
{
  "status": "healthy",
  "timestamp": "2026-01-15T11:30:00",
  "version": "1.0.0",
  "environment": "production",
  "database": {
    "status": "connected",
    "type": "MySQL"
  },
  "system": {
    "cpu_usage_percent": 15.2,
    "memory": {
      "used_percent": 45.8
    }
  }
}
```

### 监控指标

- **应用状态**: 检查Flask应用是否正常运行
- **数据库连接**: 验证数据库连接状态
- **系统资源**: CPU、内存、磁盘使用情况
- **响应时间**: API响应性能监控

## 🛠️ 故障排查

### 常见问题

#### 1. 端口占用
```bash
# 错误: Port 8080 is already in use
lsof -i :8080
kill -9 <PID>

# 或修改端口
sed -i 's/8080:80/8081:80/' docker-compose.yml
```

#### 2. 数据库连接失败
```bash
# 检查MySQL容器状态
docker-compose logs mysql

# 等待MySQL完全启动
docker-compose exec mysql mysqladmin ping -h localhost
```

#### 3. 前端页面空白
```bash
# 检查构建是否成功
docker-compose logs app | grep "frontend"

# 重新构建
docker-compose build --no-cache app
```

#### 4. API请求失败
```bash
# 检查后端日志
docker-compose logs app | grep "flask"

# 测试API连接
curl http://localhost:8080/api/health
```

### 日志分析

```bash
# 查看完整日志
docker-compose logs

# 只看错误日志
docker-compose logs | grep -i error

# 实时监控日志
docker-compose logs -f --tail=100
```

## 📊 性能优化

### 生产环境优化

#### 1. 资源限制
```yaml
# docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

#### 2. 缓存配置
```yaml
# 启用Redis缓存
environment:
  - REDIS_URL=redis://redis:6379/0
```

#### 3. 数据库连接池
```python
# backend/.env.production
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### 扩展部署

#### 多实例负载均衡
```bash
# 启动多个应用实例
docker-compose up -d --scale app=3

# 使用Nginx负载均衡
docker-compose --profile production up -d
```

## 🔐 安全配置

### 生产环境安全

1. **修改默认密钥**
```env
JWT_SECRET_KEY=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 32)
DB_PASSWORD=$(openssl rand -base64 16)
```

2. **限制访问来源**
```env
ALLOWED_ORIGINS=https://yourdomain.com
```

3. **启用HTTPS**
```bash
# 添加SSL证书
mkdir -p docker/nginx/ssl
# 将证书文件放入该目录
# 修改nginx配置启用HTTPS
```

## 📈 监控与日志

### 日志管理

```bash
# 配置日志轮转
echo '
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}' > /etc/docker/daemon.json
```

### 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看详细信息
docker-compose top
```

## 🔄 数据备份与恢复

### SQLite备份
```bash
# 备份
docker-compose exec app cp /app/backend/instance/bio_code_share.db /tmp/backup.db
docker cp $(docker-compose ps -q app):/tmp/backup.db ./backup-$(date +%Y%m%d).db

# 恢复
docker cp ./backup.db $(docker-compose ps -q app):/app/backend/instance/bio_code_share.db
docker-compose restart app
```

### MySQL备份
```bash
# 备份
docker-compose exec mysql mysqldump -u app_user -p${DB_PASSWORD} bio_code_share > backup-$(date +%Y%m%d).sql

# 恢复
docker-compose exec mysql mysql -u app_user -p${DB_PASSWORD} bio_code_share < backup.sql
```

## 🌐 域名与SSL

### 域名配置

1. **修改Nginx配置**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    # ... 其他配置
}
```

2. **SSL证书**
```bash
# 使用Let's Encrypt
docker run --rm -it \
  -v $(pwd)/docker/nginx/ssl:/etc/letsencrypt \
  certbot/certbot certonly \
  --webroot -w /var/www/certbot \
  -d yourdomain.com
```

## 📱 移动端适配

项目已完全支持移动端响应式设计，在移动设备上访问体验完整。

## ✅ 部署检查清单

部署完成后，请检查以下项目：

- [ ] 🌐 **网站访问**: http://localhost:8080 正常打开
- [ ] 🔐 **用户功能**: 注册、登录、发布代码正常
- [ ] 📝 **Markdown功能**: 编辑器、预览、图片粘贴正常
- [ ] 📱 **移动端适配**: 手机访问界面正常
- [ ] 🔍 **搜索功能**: 代码搜索返回结果正确
- [ ] 💾 **数据持久化**: 重启服务后数据不丢失
- [ ] ⚡ **性能指标**: 页面加载时间 < 3秒
- [ ] 🛡️ **安全检查**: 密钥已修改，跨域配置正确

## 📞 技术支持

### 获取帮助

- **查看日志**: `docker-compose logs -f`
- **健康检查**: `curl http://localhost:8080/health`
- **重置环境**: `docker-compose down -v && docker-compose up -d`

### 社区支持

- GitHub Issues: 提交问题和建议
- 文档更新: 持续完善部署指南

---

## 🎉 恭喜！

按照本指南，你已经成功将代码分享平台部署到Docker容器中！

现在可以：
- ✨ 享受现代化的Markdown编辑体验
- 🖼️ 直接粘贴图片到文档中
- 📱 在任何设备上访问和使用
- 🚀 一键部署到任何支持Docker的环境

**祝你使用愉快！** 🌟
