# 阿里云部署完整指南

## 🏗️ 部署架构概览

```
用户 → CDN → SLB负载均衡 → ECS服务器集群
                           ↓
                    RDS数据库 + OSS对象存储
```

## 📋 前置准备

### 1. 阿里云资源清单
- ✅ **ECS实例** - 云服务器（推荐：2核4GB，CentOS 8.x）
- ✅ **RDS实例** - 云数据库MySQL 8.0（可选，也可用ECS自建）
- 🔄 **OSS存储** - 对象存储（用于图片/文件）
- 🔄 **CDN加速** - 内容分发网络
- 🔄 **SLB负载均衡** - 高可用（多实例时）
- ✅ **安全组** - 网络访问控制
- ✅ **域名备案** - ICP备案（必须）

### 2. 本地准备
```bash
# 确保项目已优化并测试通过
cd /Users/wangjien/Project/代码分享平台
git status  # 确保所有更改已提交
npm run build  # 构建前端
```

## 🛠️ 第一步：创建ECS实例

### 1.1 购买ECS服务器
```
地域：选择离用户近的区域（如华东1-杭州）
实例规格：ecs.s6-c1m2.small（2核4GB）或更高
镜像：CentOS 8.2 64位
系统盘：40GB SSD云盘
网络：专有网络VPC
带宽：按使用流量计费，峰值10Mbps
```

### 1.2 安全组配置
```bash
# 开放端口
22   - SSH连接
80   - HTTP服务
443  - HTTPS服务
5000 - 后端API（可选，建议用Nginx代理）
3306 - MySQL（仅内网，如果自建数据库）
```

## 🔧 第二步：服务器环境配置

### 2.1 连接服务器
```bash
# 使用SSH连接（替换为你的ECS公网IP）
ssh root@your-ecs-ip

# 更新系统
yum update -y
```

### 2.2 安装基础环境
```bash
# 安装Python 3.9
yum install -y python39 python39-pip python39-devel

# 安装Node.js 18
curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
yum install -y nodejs

# 安装Git
yum install -y git

# 安装Nginx
yum install -y nginx

# 安装MySQL（如果不使用RDS）
yum install -y mysql-server
systemctl enable mysqld
systemctl start mysqld

# 安装Redis
yum install -y redis
systemctl enable redis
systemctl start redis
```

### 2.3 安装进程管理工具
```bash
# 安装PM2用于管理Node.js进程
npm install -g pm2

# 安装Supervisor用于管理Python进程
pip3 install supervisor
```

## 📦 第三步：部署应用代码

### 3.1 创建部署目录
```bash
mkdir -p /var/www
cd /var/www

# 克隆项目（或上传代码包）
git clone https://github.com/your-username/代码分享平台.git
cd 代码分享平台
```

### 3.2 部署后端服务
```bash
cd backend

# 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt

# 如果没有requirements.txt，手动安装
pip install flask flask-restful flask-sqlalchemy flask-jwt-extended flask-cors flask-limiter marshmallow python-dotenv

# 创建生产环境配置
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_URL=mysql://username:password@rds-host:3306/database_name
REDIS_URL=redis://localhost:6379
EOF

# 初始化数据库
python app.py
# 在另一个终端执行数据库迁移
sqlite3 instance/bio_code_share.db < migrations/add_search_indexes.sql
```

### 3.3 部署前端
```bash
cd ../frontend

# 安装Node.js依赖
npm install

# 创建生产环境配置
cat > .env.production << EOF
VITE_API_BASE_URL=https://yourdomain.com/api
VITE_APP_TITLE=代码分享平台
EOF

# 构建前端
npm run build

# 将构建文件移动到Nginx目录
cp -r dist/* /var/www/html/
```

## 🌐 第四步：Nginx配置

### 4.1 创建Nginx配置
```bash
cat > /etc/nginx/conf.d/code-share.conf << 'EOF'
# 前端静态文件服务
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/html;
    index index.html;

    # 前端路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 跨域配置
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods 'GET, POST, PUT, DELETE, OPTIONS';
        add_header Access-Control-Allow-Headers 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization';
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # 静态资源缓存
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1M;
        add_header Cache-Control "public, immutable";
    }

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;
}

# HTTPS配置（SSL证书配置后取消注释）
# server {
#     listen 443 ssl http2;
#     server_name yourdomain.com www.yourdomain.com;
#     root /var/www/html;
#     index index.html;
#
#     ssl_certificate /path/to/your/cert.pem;
#     ssl_certificate_key /path/to/your/key.pem;
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
#     ssl_prefer_server_ciphers off;
#
#     # 其他配置同HTTP
#     location / {
#         try_files $uri $uri/ /index.html;
#     }
#
#     location /api/ {
#         proxy_pass http://127.0.0.1:5000/;
#         # ... 其他proxy配置
#     }
# }

# HTTP重定向到HTTPS
# server {
#     listen 80;
#     server_name yourdomain.com www.yourdomain.com;
#     return 301 https://$server_name$request_uri;
# }
EOF

# 测试Nginx配置
nginx -t

# 启动Nginx
systemctl enable nginx
systemctl start nginx
```

## 🗄️ 第五步：数据库配置

### 5.1 使用阿里云RDS（推荐）
```bash
# 1. 在阿里云控制台创建RDS MySQL实例
# 2. 配置白名单，允许ECS内网IP访问
# 3. 创建数据库和用户

# 连接RDS创建数据库
mysql -h your-rds-host.mysql.rds.aliyuncs.com -u username -p
CREATE DATABASE bio_code_share CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'app_user'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON bio_code_share.* TO 'app_user'@'%';
FLUSH PRIVILEGES;

# 更新后端.env配置
DATABASE_URL=mysql://app_user:secure_password@your-rds-host.mysql.rds.aliyuncs.com:3306/bio_code_share
```

### 5.2 或使用ECS自建MySQL
```bash
# 启动MySQL服务
systemctl start mysqld

# 获取临时密码
grep 'temporary password' /var/log/mysqld.log

# 安全配置
mysql_secure_installation

# 创建数据库
mysql -u root -p
CREATE DATABASE bio_code_share CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON bio_code_share.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
```

## 🚀 第六步：启动服务

### 6.1 创建Supervisor配置（后端）
```bash
cat > /etc/supervisord.d/flask-app.ini << 'EOF'
[program:flask-app]
command=/var/www/代码分享平台/backend/venv/bin/python /var/www/代码分享平台/backend/app.py
directory=/var/www/代码分享平台/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/flask-app.log
environment=FLASK_ENV=production
EOF

# 启动Supervisor
systemctl enable supervisord
systemctl start supervisord
supervisorctl reread
supervisorctl update
supervisorctl start flask-app
```

### 6.2 检查服务状态
```bash
# 检查后端服务
supervisorctl status flask-app
curl http://localhost:5000/api/codes

# 检查Nginx
systemctl status nginx
curl http://localhost

# 检查数据库连接
mysql -u app_user -p bio_code_share -e "SHOW TABLES;"
```

## 🔒 第七步：安全配置

### 7.1 配置防火墙
```bash
# 启用firewalld
systemctl enable firewalld
systemctl start firewalld

# 开放必要端口
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-service=ssh
firewall-cmd --reload
```

### 7.2 SSL证书配置（免费Let's Encrypt）
```bash
# 安装Certbot
yum install -y certbot python3-certbot-nginx

# 获取SSL证书
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

## 📊 第八步：监控和日志

### 8.1 设置日志轮转
```bash
cat > /etc/logrotate.d/flask-app << 'EOF'
/var/log/flask-app.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 644 www-data www-data
}
EOF
```

### 8.2 系统监控脚本
```bash
cat > /usr/local/bin/check-services.sh << 'EOF'
#!/bin/bash
# 检查关键服务状态

echo "=== $(date) ==="
echo "检查Nginx状态:"
systemctl is-active nginx

echo "检查Flask应用状态:"
supervisorctl status flask-app

echo "检查数据库连接:"
mysqladmin ping

echo "检查磁盘使用:"
df -h

echo "检查内存使用:"
free -h

echo "============================"
EOF

chmod +x /usr/local/bin/check-services.sh

# 设置定时检查
echo "*/5 * * * * /usr/local/bin/check-services.sh >> /var/log/system-check.log" | crontab -
```

## 🚀 第九步：域名配置

### 9.1 域名解析
```
# 在域名服务商处添加A记录
yourdomain.com     A    your-ecs-public-ip
www.yourdomain.com A    your-ecs-public-ip
```

### 9.2 备案要求
- 域名必须在阿里云备案
- 备案过程通常需要7-20天
- 备案期间可使用ECS公网IP测试

## 🔄 第十步：部署脚本

创建自动化部署脚本：

```bash
cat > /var/www/deploy.sh << 'EOF'
#!/bin/bash
# 自动化部署脚本

set -e

echo "开始部署..."

# 备份当前版本
cp -r /var/www/代码分享平台 /var/www/backup-$(date +%Y%m%d-%H%M%S)

# 更新代码
cd /var/www/代码分享平台
git pull origin main

# 更新后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 数据库迁移（如有需要）
# python migrate.py

# 重启后端服务
supervisorctl restart flask-app

# 构建前端
cd ../frontend
npm install
npm run build
cp -r dist/* /var/www/html/

# 重启Nginx
systemctl reload nginx

echo "部署完成！"
echo "访问地址: https://yourdomain.com"
EOF

chmod +x /var/www/deploy.sh
```

## 📝 部署后检查清单

### ✅ 功能验证
- [ ] 网站首页正常访问
- [ ] 用户注册/登录功能
- [ ] 代码发布功能
- [ ] Markdown编辑器
- [ ] 图片粘贴功能
- [ ] 搜索功能
- [ ] 响应式布局（移动端）

### ✅ 性能检查
- [ ] 页面加载速度 < 3秒
- [ ] API响应时间 < 1秒
- [ ] 图片加载正常
- [ ] 缓存机制生效

### ✅ 安全验证
- [ ] HTTPS证书有效
- [ ] 安全头部设置
- [ ] SQL注入防护
- [ ] XSS防护
- [ ] CSRF保护

## 🛠️ 常见问题排查

### 502 Bad Gateway
```bash
# 检查后端服务
supervisorctl status flask-app
tail -f /var/log/flask-app.log

# 检查端口监听
netstat -tlnp | grep 5000
```

### 数据库连接失败
```bash
# 检查数据库服务
systemctl status mysqld

# 测试连接
mysql -u app_user -p bio_code_share

# 检查配置
cat backend/.env
```

### 静态文件404
```bash
# 检查文件权限
ls -la /var/www/html/

# 检查Nginx配置
nginx -t
tail -f /var/log/nginx/error.log
```

## 🚀 高级优化（可选）

### 1. 使用Docker部署
```bash
# 创建Dockerfile
# 使用Docker Compose管理服务
# 简化部署和扩展
```

### 2. 配置CDN加速
```bash
# 阿里云CDN配置
# 静态资源加速
# 图片处理服务
```

### 3. 数据库优化
```bash
# 读写分离
# 连接池配置
# 缓存策略
```

---

## 📞 技术支持

如果在部署过程中遇到问题，可以：

1. 检查服务状态：`systemctl status nginx mysqld`
2. 查看错误日志：`tail -f /var/log/nginx/error.log`
3. 测试网络连接：`telnet your-domain 80`
4. 检查防火墙：`firewall-cmd --list-all`

部署完成后，你的代码分享平台就可以在阿里云上稳定运行了！
