# 代码分享平台

一个现代化的代码分享与知识管理平台，支持 Markdown 编辑、代码高亮、图片粘贴等功能。

## ✨ 功能特性

- 📝 **Markdown 编辑器** - 支持实时预览、语法高亮
- 🖼️ **图片粘贴** - 直接粘贴图片到编辑器
- 🔍 **全文搜索** - 快速检索代码和文档
- 👥 **用户系统** - 注册、登录、个人主页
- 📱 **响应式设计** - 完美适配移动端
- 🏷️ **分类管理** - 支持多级分类

## 🛠️ 技术栈

| 前端 | 后端 | 数据库 |
|------|------|--------|
| Vue 3 + Vite | Flask + SQLAlchemy | SQLite / MySQL |
| TailwindCSS | Flask-JWT-Extended | Redis (缓存) |
| Markdown-it | Flask-CORS | |

---

# 🚀 部署教程

## 📋 前置要求

- **服务器**: 2核4GB 及以上配置
- **系统**: CentOS 8.x / Ubuntu 20.04+ / macOS
- **软件**: Python 3.9+、Node.js 18+、Git

---

# 方式一：Docker 部署（推荐）

> 最简单的部署方式，一键启动所有服务
> 
> ⚠️ **无需手动执行 `npm run build`**，Docker 构建时会自动完成前端编译

## 1. 安装 Docker

```bash
# CentOS
yum install -y docker docker-compose
systemctl enable docker && systemctl start docker

# Ubuntu
apt install -y docker.io docker-compose
systemctl enable docker && systemctl start docker

# macOS
brew install docker docker-compose
```

## 2. 克隆项目

```bash
git clone https://github.com/your-username/代码分享平台.git
cd 代码分享平台
```

## 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 安全密钥（必须修改）
JWT_SECRET_KEY=your-super-secret-key-change-this
SECRET_KEY=your-app-secret-key

# 域名配置
ALLOWED_ORIGINS=https://your-domain.com

# 数据库配置（默认 SQLite，生产环境推荐 MySQL）
DATABASE_URI=sqlite:///instance/bio_code_share.db
# DATABASE_URI=mysql+pymysql://app_user:password@mysql:3306/bio_code_share
```

## 4. 一键部署

```bash
# 开发环境（SQLite）
./deploy.sh dev sqlite

# 生产环境（MySQL）
./deploy.sh prod mysql
```

## 5. 访问应用

打开浏览器访问：**http://localhost:8080**

## Docker 常用命令

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

## 数据备份

```bash
# SQLite 备份
docker cp $(docker-compose ps -q app):/app/backend/instance/bio_code_share.db ./backup.db

# MySQL 备份
docker-compose exec mysql mysqldump -u app_user -p bio_code_share > backup.sql
```

---

# 方式二：阿里云 ECS 直接部署

> 适合需要更多控制权的生产环境

## 1. 购买 ECS 服务器

> 地址：https://cn.aliyun.com/

**推荐配置：**
- 实例规格：ecs.s6-c1m2.small（2核4GB）
- 镜像：CentOS 8.2 64位
- 系统盘：40GB SSD
- 带宽：按流量计费，峰值 10Mbps

**安全组开放端口：**
| 端口 | 用途 |
|------|------|
| 22 | SSH 连接 |
| 80 | HTTP 服务 |
| 443 | HTTPS 服务 |
| 5000 | 后端 API（可选） |

## 2. 连接服务器并安装环境

```bash
# SSH 连接
ssh root@your-ecs-ip

# 更新系统
yum update -y

# 安装 Python 3.9
yum install -y python39 python39-pip python39-devel

# 安装 Node.js 18
curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
yum install -y nodejs

# 安装其他依赖
yum install -y git nginx redis mysql-server

# 启动服务
systemctl enable nginx redis mysqld
systemctl start nginx redis mysqld
```

## 3. 部署代码

```bash
# 创建目录并克隆项目
mkdir -p /var/www && cd /var/www
git clone https://github.com/your-username/代码分享平台.git
cd 代码分享平台
```

### 部署后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -base64 32)
ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_URL=mysql://app_user:password@localhost:3306/bio_code_share
EOF
```

### 部署前端

```bash
cd ../frontend

# 安装依赖并构建
npm install
npm run build

# 复制到 Nginx 目录
cp -r dist/* /var/www/html/
```

## 4. 配置 Nginx

```bash
cat > /etc/nginx/conf.d/code-share.conf << 'EOF'
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/html;
    index index.html;

    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态资源缓存
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1M;
        add_header Cache-Control "public, immutable";
    }

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/javascript application/json;
}
EOF

# 测试并重启 Nginx
nginx -t && systemctl restart nginx
```

## 5. 配置数据库

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库和用户
CREATE DATABASE bio_code_share CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON bio_code_share.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 6. 启动后端服务

使用 Supervisor 管理后端进程：

```bash
# 安装 Supervisor
pip3 install supervisor

# 创建配置
cat > /etc/supervisord.d/flask-app.ini << 'EOF'
[program:flask-app]
command=/var/www/代码分享平台/backend/venv/bin/python /var/www/代码分享平台/backend/app.py
directory=/var/www/代码分享平台/backend
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/flask-app.log
environment=FLASK_ENV=production
EOF

# 启动服务
systemctl enable supervisord
systemctl start supervisord
supervisorctl reread && supervisorctl update
supervisorctl start flask-app
```

## 7. 配置 SSL 证书（可选但推荐）

```bash
# 安装 Certbot
yum install -y certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 设置自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

## 8. 配置防火墙

```bash
systemctl enable firewalld && systemctl start firewalld
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-service=ssh
firewall-cmd --reload
```

---

# ✅ 部署检查清单

部署完成后，请验证以下功能：

- [ ] 🌐 网站首页正常访问
- [ ] 🔐 用户注册/登录功能
- [ ] 📝 代码发布和编辑
- [ ] 🖼️ 图片粘贴功能
- [ ] 🔍 搜索功能
- [ ] 📱 移动端适配

---

# 🛠️ 常见问题

## 502 Bad Gateway

```bash
# 检查后端服务状态
supervisorctl status flask-app
tail -f /var/log/flask-app.log

# 检查端口
netstat -tlnp | grep 5000
```

## 数据库连接失败

```bash
# 检查 MySQL 服务
systemctl status mysqld

# 测试连接
mysql -u app_user -p bio_code_share
```

## 静态文件 404

```bash
# 检查文件权限
ls -la /var/www/html/

# 检查 Nginx 配置
nginx -t
tail -f /var/log/nginx/error.log
```

---

# 📚 更多文档

- [Docker 部署详细指南](./DOCKER_DEPLOYMENT_GUIDE.md)
- [阿里云部署完整指南](./ALIYUN_DEPLOYMENT_GUIDE.md)
- [功能优化指南](./HIGH_PRIORITY_OPTIMIZATION_GUIDE.md)
- [未来路线图](./FUTURE_ROADMAP.md)

---

# 📞 技术支持

如遇问题，可以：

1. 查看日志：`docker-compose logs -f` 或 `tail -f /var/log/flask-app.log`
2. 健康检查：`curl http://localhost:8080/health`
3. 提交 Issue：在 GitHub 仓库提交问题

---

**祝你部署顺利！** 🎉
