# <font color="blue"> TODO: Git action 打包成直接部署的镜像已经完成，还有些问题需要修改，暂时先不要部署</font>


# 代码分享平台

一个面向生物信息学领域的代码分享平台，支持代码片段发布、Markdown文档、代码语法高亮、评论互动等功能。适用于实验室内部代码共享、团队协作开发、教学演示等场景。
> **<font color="red">既然已经有gitee或github这种项目或代码管理平台为什么要开发这个项目？</font>**

| 特性 | GitHub 代码分享平台 | 定位 |
| :--- | :--- | :--- |
| **定位** | 代码版本控制 + 协作开发 | 知识分享 + 代码片段管理 |
| **内容形式** | 完整项目仓库 | 单篇文章/代码片段 |
| **学习曲线** | 需要学 Git | 像写博客一样简单 |
| **访问门槛** | 需要账号才能看私有仓库 | 可公开分享，无需登录即可浏览 |

# 服务启动后的效果

##  登录页面
!["登录页"](https://files.mdnice.com/user/112287/5a7f4642-33a7-44c4-b58d-96628211f8d1.png)

## 普通用户与管理员账户的区别
!["普通用户登录界面"](https://files.mdnice.com/user/112287/2c264e56-6dd4-4100-a5f0-e56dce0df654.png)

相比普通用户的登录界面，管理员界面可以进行后台管理。
!["管理员登录后的界面"](https://files.mdnice.com/user/112287/551aa94e-4b1c-4066-bbe7-1d137f7914ad.png)
后台管理界面可以对用户、内容和评论进行审核和管理。
!["管理后台页面"](https://files.mdnice.com/user/112287/348c923c-158e-4ea3-9921-833f9845f008.png)

## 内容发布界面
提供纯代码和markdown模式发布代码。
![](https://files.mdnice.com/user/112287/ea25f6e0-343f-4fb2-920d-bbdad07693b5.jpg)

提供多种生物信息学语言支持。
![](https://files.mdnice.com/user/112287/d5a29eca-e1e2-45b3-8826-83651073c9ae.png)


## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + Vite + Element Plus + TypeScript | 现代化响应式界面 |
| 后端 | Flask + Flask-RESTful + SQLAlchemy | RESTful API 服务 |
| 数据库 | SQLite / MySQL | SQLite 适合小规模，MySQL 适合生产环境 |
| 缓存 | Redis | 提升查询性能，支持会话管理 |
| Web服务器 | Nginx + Gunicorn | 反向代理 + WSGI 服务器 |
| 容器化 | Docker + Docker Compose | 一键部署，环境隔离 |

---

## 部署方式概览

| 方式 | 难度 | 适用场景 | 说明 |
|------|------|----------|------|
| **Docker Hub 镜像** | ⭐ 最简单 | 快速体验、小团队 | 直接拉取预构建镜像，无需编译 |
| **Docker 本地构建** | ⭐⭐ 简单 | 需要自定义修改 | 克隆代码后本地构建镜像 |
| **直装部署** | ⭐⭐⭐ 中等 | 生产环境、完全控制 | 手动安装所有依赖 |

---

## 🚀 Docker Hub 镜像部署（推荐新手）

类似 Nextcloud，直接拉取预构建镜像即可运行，**无需克隆代码、无需本地构建**。

> 💡 镜像通过 GitHub Actions 自动构建，每次发布新版本时自动推送到 Docker Hub 和 GitHub Container Registry。

**镜像地址：**
- Docker Hub: `wangjien/code-platform`
- GitHub Container Registry: `ghcr.io/wangjien/code-platform`

### 一键部署（SQLite 版本）

```bash
# 1. 创建部署目录
mkdir -p ~/code-platform && cd ~/code-platform

# 2. 下载配置文件
curl -O https://raw.githubusercontent.com/Wangjien/Code-platform/master/docker-compose.hub.yml
curl -O https://raw.githubusercontent.com/Wangjien/Code-platform/master/.env.example

# 3. 配置环境变量
cp .env.example .env

# 4. 修改必要配置（至少修改 JWT_SECRET_KEY）
# 生成随机密钥: openssl rand -base64 32
nano .env

# 5. 启动服务
docker compose -f docker-compose.hub.yml up -d

# 6. 访问应用
echo "访问: http://$(hostname -I | awk '{print $1}'):8080"
```

### 一键部署（MySQL 版本）

```bash
# 1. 创建部署目录
mkdir -p ~/code-platform && cd ~/code-platform

# 2. 下载 MySQL 版本配置文件
curl -O https://raw.githubusercontent.com/Wangjien/Code-platform/master/docker-compose.hub.mysql.yml
curl -O https://raw.githubusercontent.com/Wangjien/Code-platform/master/.env.example

# 3. 配置环境变量
cp .env.example .env
nano .env  # 修改 JWT_SECRET_KEY 和 MySQL 密码

# 4. 启动服务
docker compose -f docker-compose.hub.mysql.yml up -d
```

### 配置说明

编辑 `.env` 文件，**必须修改**以下配置：

```bash
# 安全密钥（必须修改！）
JWT_SECRET_KEY=你的随机密钥  # 使用 openssl rand -base64 32 生成

# 允许访问的域名/IP
ALLOWED_ORIGINS=http://你的服务器IP:8080

# 管理员账户（建议修改默认密码）
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=你的强密码
```

### 常用命令

```bash
# 查看运行状态
docker compose -f docker-compose.hub.yml ps

# 查看日志
docker compose -f docker-compose.hub.yml logs -f

# 停止服务
docker compose -f docker-compose.hub.yml down

# 更新到最新版本
docker compose -f docker-compose.hub.yml pull
docker compose -f docker-compose.hub.yml up -d
```

### 数据备份

```bash
# SQLite 数据库备份
docker cp code-platform:/app/backend/instance/bio_code_share.db ./backup_$(date +%Y%m%d).db
```

---

## 快速部署 (Docker 本地构建)

本节介绍如何在服务器上使用 Docker 快速部署应用（需要克隆代码并本地构建镜像）。

### 环境要求

在开始之前，请确保服务器满足以下条件：

| 要求 | 最低配置 | 推荐配置 |
|------|----------|----------|
| 操作系统 | CentOS 7+ / Ubuntu 18.04+ / Debian 10+ | Ubuntu 22.04 LTS |
| 内存 | 2GB | 4GB+ |
| 磁盘 | 10GB | 20GB+ |
| Docker | 20.0+ | 最新稳定版 |
| Docker Compose | 2.0+ | 最新稳定版 |

### 第一步：安装 Docker 和 Docker Compose

如果服务器尚未安装 Docker，请按以下步骤安装：

**CentOS / RHEL:**

```bash
# 安装依赖
sudo yum install -y yum-utils

# 添加 Docker 仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

**Ubuntu / Debian:**

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# 添加 Docker GPG 密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加 Docker 仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 验证安装
docker --version
docker compose version
```

**将当前用户加入 docker 组 (可选，避免每次使用 sudo):**

```bash
sudo usermod -aG docker $USER
# 重新登录后生效
```

### 第二步：获取项目代码

```bash
# 克隆仓库
git clone https://github.com/Wangjien/Code-platform.git

# 进入项目目录
cd Code-platform

# 查看目录结构
ls -la
```

### 第三步：配置环境变量

复制环境变量模板文件：

```bash
cp .env.example .env
```

使用编辑器打开 `.env` 文件进行配置：

```bash
vim .env
# 或
nano .env
```

**必须修改的配置项：**

```bash
# ===== 安全配置 (必须修改) =====
# JWT 密钥：用于用户登录令牌加密，必须修改为随机字符串
# 生成方法: openssl rand -base64 32
JWT_SECRET_KEY=这里填写一个随机的长字符串

# ===== 域名配置 =====
# 允许访问的域名或IP，用于 CORS 跨域配置
# 格式: http://域名或IP:端口
# 示例: http://192.168.1.100:8080 或 https://code.example.com
ALLOWED_ORIGINS=http://你的服务器IP:8080
```

**生成随机密钥的方法：**

```bash
# 方法1: 使用 openssl
openssl rand -base64 32

# 方法2: 使用 Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# 方法3: 使用 /dev/urandom
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
```

### 第四步：执行部署

**方式一：使用一键部署脚本 (推荐)**

<font color="red">注意：在执行部署脚本之前, 查看下方的数据库配置详解</font>

```bash
# 添加执行权限
chmod +x deploy.sh

# 使用 SQLite 数据库部署 (适合小规模使用)
./deploy.sh prod sqlite

# 或使用 MySQL 数据库部署 (适合生产环境)
./deploy.sh prod mysql
```

部署脚本会自动完成以下操作：
1. 检查 Docker 环境
2. 检查端口占用情况
3. 生成环境配置
4. 构建 Docker 镜像
5. 启动所有服务
6. 执行健康检查

**方式二：手动部署**

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看构建日志
docker-compose logs -f
```

### 第五步：验证部署

```bash
# 查看容器运行状态
docker-compose ps

# 期望输出类似：
# NAME                COMMAND             STATUS              PORTS
# code-platform-app   "/start.sh"         Up (healthy)        0.0.0.0:8080->80/tcp
# code-platform-redis "redis-server..."   Up                  0.0.0.0:6379->6379/tcp

# 检查应用健康状态
curl http://localhost:8080/api/health

# 期望输出: {"status": "healthy"}

# 查看应用日志
docker-compose logs app
```

### 第六步：访问应用

部署成功后，打开浏览器访问：
L
```
http://你的服务器IP:8080
```

**默认管理员账户：**

首次启动时会自动创建默认管理员账户：

| 项目 | 默认值 |
|------|--------|
| 用户名 | admin |
| 邮箱 | admin@example.com |
| 密码 | admin123 |

**重要：请登录后立即修改默认密码！**

可以在 `.env` 文件中自定义管理员账户：

```bash
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=你的强密码
```

  **首次使用：**
 1. 使用默认管理员账户登录
 2. 进入"管理后台"进行系统配置
 3. 修改默认密码
 4. 普通用户可通过"注册"创建新账户
 
 ---

 ## 非 Docker 直装部署（Ubuntu 22.04 示例）
 
 本节适用于：你希望在服务器上直接安装依赖并运行服务（不使用 Docker）。
 
 ### 环境要求
 
 - Ubuntu 22.04（18.04+ 理论可行）
 - Python 3.10+（建议使用系统自带 Python3）
 - Nginx
 - Redis
 -（可选）MySQL
 -（前端可选）Node.js：如果你选择在服务器上构建前端
 
 ### 第一步：安装系统依赖
 
 ```bash
 sudo apt update
 sudo apt install -y git nginx redis-server python3 python3-venv python3-pip
 ```
 
 如果你打算使用 MySQL（可选）：
 
 ```bash
 sudo apt install -y mysql-server
 sudo systemctl enable --now mysql
 sudo systemctl status mysql --no-pager
 ```
 
 初始化（建议执行）：
 
 ```bash
 sudo mysql_secure_installation
 ```
 
 创建数据库与账号（示例）：
 
 ```bash
 sudo mysql -e "CREATE DATABASE IF NOT EXISTS bio_code_share DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
 sudo mysql -e "CREATE USER IF NOT EXISTS 'biocode'@'localhost' IDENTIFIED BY 'YourStrongPassword';"
 sudo mysql -e "GRANT ALL PRIVILEGES ON bio_code_share.* TO 'biocode'@'localhost';"
 sudo mysql -e "FLUSH PRIVILEGES;"
 ```
 
 （可选）如果你使用 Rocky/CentOS/RHEL 系：
 
 ```bash
 # 仅示例：不同系统源可能不同，请按你服务器实际情况选择合适的 MySQL 8 安装方式
 # dnf -y module disable mysql
 # dnf -y install mysql-server
 # systemctl enable --now mysqld
 ```
 
 ### 第二步：拉取代码
 
 建议安装到 `/opt`：
 
 ```bash
 sudo mkdir -p /opt/code-platform
 sudo chown -R $USER:$USER /opt/code-platform
 cd /opt/code-platform
 git clone https://github.com/Wangjien/Code-platform.git .
 ```
 
 ### 第三步：准备前端静态文件（2 选 1）
 
 #### 方式 A：在服务器上构建（需要 Node.js）
 
 安装 Node.js（Ubuntu 22.04 示例，使用 NodeSource）：
 
 ```bash
 curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
 sudo apt install -y nodejs
 node -v
 npm -v
 ```
 
 ```bash
 cd /opt/code-platform/frontend
 npm ci
 npm run build
 ```
 
 构建完成后产物在：`/opt/code-platform/frontend/dist`
 
 #### 方式 B：在本地构建后上传（服务器不需要 Node.js）
 
 在你的电脑上：
 
 ```bash
 cd frontend
 npm ci
 npm run build
 ```
 
 然后把 `frontend/dist` 整个目录上传到服务器的 `/opt/code-platform/frontend/dist`。
 
 ### 第四步：配置后端 Python 环境
 
 ```bash
 cd /opt/code-platform/backend
 python3 -m venv .venv
 source .venv/bin/activate
 pip install -U pip
 pip install -r requirements.txt
 ```
 
 ### 第五步：配置环境变量（建议使用 .env）
 
 ```bash
 cp /opt/code-platform/.env.example /opt/code-platform/.env
 ```
 
 重点配置项（SQLite 默认推荐）：
 
 - `JWT_SECRET_KEY`：必须改成随机长字符串
 - `ALLOWED_ORIGINS`：写你的访问地址（例如 `http://你的IP` 或 `https://你的域名`）
 - `DATABASE_URI`：SQLite 推荐使用绝对路径，例如：
 
 ```bash
 DATABASE_URI=sqlite:////opt/code-platform/backend/instance/bio_code_share.db
 ```
 
 并创建目录：
 
 ```bash
 mkdir -p /opt/code-platform/backend/instance /opt/code-platform/backend/logs
 ```
 
 如果你使用 MySQL：把 `DATABASE_URI` 改为本机连接（示例）：
 
 ```bash
 DATABASE_URI=mysql+pymysql://biocode:YourStrongPassword@127.0.0.1:3306/bio_code_share
 ```
 
 并确保已安装 MySQL 驱动依赖（通常已包含在 `requirements.txt`，如未包含请补充后重新安装依赖）。
 
 如果你使用远程 MySQL / 云数据库（RDS）（示例）：
 
 ```bash
 DATABASE_URI=mysql+pymysql://biocode:YourStrongPassword@your-mysql-host:3306/bio_code_share?charset=utf8mb4
 ```
 
 远程 MySQL 安全建议：
 
 - **只开放必要端口**：云安全组/防火墙只允许你的服务器 IP 访问 `3306`，不要全网开放。
 - **最小权限账号**：避免用 `root` 连接应用；使用单独业务账号，仅授权 `bio_code_share.*`。
 - **强密码与轮换**：使用强密码并定期轮换。
 - **TLS**：生产环境优先启用 MySQL TLS（按云数据库指引配置证书）。
 - **服务端 bind-address**：自建 MySQL 若需要远程连接，才配置 `bind-address`；否则保持仅本机监听更安全。
 
 自建 MySQL 远程账号示例（在 MySQL 内执行）：
 
 ```sql
 CREATE USER 'biocode'@'你的服务器公网IP' IDENTIFIED BY 'YourStrongPassword';
 GRANT ALL PRIVILEGES ON bio_code_share.* TO 'biocode'@'你的服务器公网IP';
 FLUSH PRIVILEGES;
 ```
 
 ### 第五点五步：初始化数据库（建表 / 初始化默认数据 / 创建管理员）
 
 在后端目录执行（SQLite/MySQL 都需要执行一次建表）：
 
 ```bash
 cd /opt/code-platform/backend
 source .venv/bin/activate
 python -c "from app import app, db;\nwith app.app_context():\n    db.create_all();\n    print('数据库表已创建')"
 ```
 
 初始化默认分类与标签（可选，但建议执行）：
 
 ```bash
 python /opt/code-platform/backend/init_data.py
 ```
 
 创建/提升管理员（可选；也可通过环境变量 `ADMIN_*` 配置后首次启动自动创建）：
 
 ```bash
 python /opt/code-platform/make_admin.py
 ```
 
 ### 第六步：使用 systemd 启动后端（Gunicorn）
 
 创建 systemd service 文件：
 
 ```bash
 sudo tee /etc/systemd/system/code-platform.service > /dev/null <<'EOF'
 [Unit]
 Description=Code Platform (Gunicorn)
 After=network.target redis-server.service mysql.service
 Wants=redis-server.service
 
 [Service]
 Type=simple
 User=www-data
 Group=www-data
 WorkingDirectory=/opt/code-platform/backend
 EnvironmentFile=/opt/code-platform/.env
 Environment=PYTHONPATH=/opt/code-platform/backend
 Environment=FLASK_DEBUG=0
 ExecStart=/opt/code-platform/backend/.venv/bin/gunicorn \
   -w 2 \
   -b 127.0.0.1:5000 \
   --access-logfile - \
   --error-logfile - \
   --timeout 120 \
   app:app
 Restart=always
 RestartSec=3
 TimeoutStartSec=30
 
 # 更严格的系统权限（如遇到写入权限问题，可先注释这几行排查）
 NoNewPrivileges=true
 PrivateTmp=true
 
 [Install]
 WantedBy=multi-user.target
 EOF
 ```
 
 赋予目录权限（避免 www-data 无法写入 SQLite 数据库文件）：
 
 ```bash
 sudo chown -R www-data:www-data /opt/code-platform/backend/instance /opt/code-platform/backend/logs
 ```
 
 启动服务：
 
 ```bash
 sudo systemctl daemon-reload
 sudo systemctl enable --now code-platform
 sudo systemctl status code-platform --no-pager
 ```
 
 生产环境建议（可选）：
 
 - **并发参数**：`-w`（worker 数）建议按 CPU 调整（通常 `CPU*2+1` 作为经验值），内存紧张可降低。
 - **运行端口**：后端只监听 `127.0.0.1:5000`，通过 Nginx 对外提供访问。
 - **日志**：当前配置将 Gunicorn 日志输出到 `journalctl`，便于统一运维。
 - **依赖服务**：如果你不用 MySQL，可从 `After=` 中移除 `mysql.service`。
 
 ### 第七步：配置 Nginx（静态前端 + /api 反代）
 
 创建站点配置：
 
 ```bash
 sudo tee /etc/nginx/sites-available/code-platform > /dev/null <<'EOF'
 server {
     listen 80;
     server_name _;
 
     root /opt/code-platform/frontend/dist;
     index index.html;
 
     location / {
         try_files $uri $uri/ /index.html;
     }
 
     location /api/ {
         proxy_pass http://127.0.0.1:5000/api/;
         proxy_set_header Host $host;
         proxy_set_header X-Real-IP $remote_addr;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_set_header X-Forwarded-Proto $scheme;
     }
 
     location /health {
         proxy_pass http://127.0.0.1:5000/health;
     }
 }
 EOF
 ```
 
 启用站点并重载：
 
 ```bash
 sudo ln -sf /etc/nginx/sites-available/code-platform /etc/nginx/sites-enabled/code-platform
 sudo nginx -t
 sudo systemctl reload nginx
 ```
 
 ### 第七点五步：配置 HTTPS（可选但推荐）
 
 前提：你已经有域名解析到服务器，并且 80/443 端口在安全组/防火墙放行。
 
 1) 安装 Certbot：
 
 ```bash
 sudo apt update
 sudo apt install -y certbot python3-certbot-nginx
 ```
 
 2) 申请证书并让 Certbot 自动修改 Nginx：
 
 ```bash
 sudo certbot --nginx -d your-domain.com
 ```
 
 3) 验证自动续期：
 
 ```bash
 sudo certbot renew --dry-run
 ```
 
 如果你不希望 Certbot 自动改配置，也可以让它只签发证书，然后手工把 Nginx `listen 443 ssl` 与证书路径配置进去。
 
 ### 第八步：验证
 
 ```bash
 curl -i http://localhost/health
 curl -i http://localhost/api/health
 ```
 
 浏览器访问：
 
 ```
 http://你的服务器IP
 ```
 
 ### 常见问题排查
 
 ```bash
 sudo systemctl status code-platform --no-pager
 sudo journalctl -u code-platform -n 200 --no-pager
 sudo tail -n 200 /var/log/nginx/error.log
 sudo nginx -t
 ```

 ## 常用运维命令

 ### 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart app

# 查看服务状态
docker-compose ps

# 查看资源使用情况
docker stats
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs

# 实时查看日志 (按 Ctrl+C 退出)
docker-compose logs -f

# 只看最近100行日志
docker-compose logs --tail=100

# 查看特定服务日志
docker-compose logs app
docker-compose logs redis
docker-compose logs mysql
```

### 进入容器

```bash
# 进入应用容器
docker-compose exec app bash

# 进入 Redis 容器
docker-compose exec redis sh

# 进入 MySQL 容器
docker-compose exec mysql bash
```

### 更新部署

```bash
# 拉取最新代码
git pull origin master

# 重新构建并部署
docker-compose down
docker-compose up -d --build

# 或使用部署脚本
./deploy.sh prod sqlite
```

---

## 数据库配置详解

### SQLite (默认)

SQLite 是默认的数据库选项，适合以下场景：
- 个人使用或小团队 (< 50人)
- 测试和开发环境
- 数据量较小 (< 10000条记录)

**优点：** 无需额外配置，开箱即用
**缺点：** 不支持高并发，不适合大规模生产环境

数据文件位置：Docker volume 中的 `/app/backend/instance/bio_code_share.db`

### MySQL (生产推荐)

MySQL 适合以下场景：
- 团队或企业使用 (> 50人)
- 生产环境
- 需要高并发和数据可靠性

**配置步骤：**

1. **修改 `.env` 文件：**

```bash
# 注释掉 SQLite 配置
# DATABASE_URI=sqlite:///instance/bio_code_share.db

# 启用 MySQL 配置
DATABASE_URI=mysql+pymysql://biocode:YourStrongPassword@mysql:3306/bio_code_share

# 数据库连接格式说明
mysql+pymysql://biocode:biocode123@mysql:3306/bio_code_share
              └──────┘ └─────────┘ └───┘ └──┘ └─────────────┘
              用户名     密码      主机  端口    数据库名

# MySQL 配置
MYSQL_ROOT_PASSWORD=YourRootPassword
MYSQL_USER=biocode
MYSQL_PASSWORD=YourStrongPassword
```

2. **修改 `docker-compose.yml`：**

找到 `app` 服务的 `depends_on` 部分，取消 `mysql` 的注释：

```yaml
services:
  app:
    # ... 其他配置 ...
    depends_on:
      - redis
      - mysql  # 取消这行的注释
```

找到 `environment` 部分，修改数据库配置：

```yaml
    environment:
      # 注释掉 SQLite
      # - DATABASE_URI=sqlite:///instance/bio_code_share.db
      
      # 启用 MySQL
      - DATABASE_URI=mysql+pymysql://biocode:${MYSQL_PASSWORD}@mysql:3306/bio_code_share
```

3. **重新部署：**

```bash
docker-compose down
docker-compose up -d --build
```

4. **验证 MySQL 连接：**

```bash
# 查看 MySQL 日志
docker-compose logs mysql

# 进入 MySQL 容器测试连接
docker-compose exec mysql mysql -u biocode -p bio_code_share
# 输入密码后，执行: SHOW TABLES;
```

### DATABASE_URI 格式说明

```
mysql+pymysql://biocode:password@mysql:3306/bio_code_share
               |______|  |______|  |___|  |__|  |__________|
               用户名     密码     主机   端口    数据库名

各部分说明：
- mysql+pymysql: 数据库驱动，使用 PyMySQL 连接 MySQL
- biocode: 数据库用户名
- password: 数据库密码
- mysql: 数据库主机名 (Docker 容器名)
- 3306: MySQL 默认端口
- bio_code_share: 数据库名称
```

---

## 本地开发环境

如果需要在本地进行开发和调试，请按以下步骤操作。

### 后端开发

```bash
# 进入后端目录
cd backend

# 创建 Python 虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r ../requirements.txt

# 启动开发服务器
python app.py
```

后端服务运行在: `http://localhost:5001`

API 文档: `http://localhost:5001/api/`

### 前端开发

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务运行在: `http://localhost:5173`

**注意：** 前端开发时会自动代理 API 请求到后端 `http://localhost:5001`

### 前端构建

```bash
cd frontend

# 构建生产版本
npm run build

# 构建产物位于 dist/ 目录
ls dist/
```

---

## 目录结构说明

```
Code-platform/
├── backend/                    # Flask 后端应用
│   ├── app.py                 # 应用入口，Flask 实例创建
│   ├── models/                # 数据模型定义
│   │   ├── user.py           # 用户模型
│   │   ├── code.py           # 代码模型
│   │   └── comment.py        # 评论模型
│   ├── resources/             # RESTful API 资源
│   │   ├── auth.py           # 认证相关 API
│   │   ├── code.py           # 代码相关 API
│   │   ├── comment.py        # 评论相关 API
│   │   └── admin.py          # 管理员 API
│   ├── utils/                 # 工具函数
│   │   ├── cache.py          # 缓存工具
│   │   └── decorators.py     # 装饰器
│   └── instance/              # 实例配置和数据库文件
│
├── frontend/                   # Vue 3 前端应用
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   │   ├── HomeView.vue      # 首页
│   │   │   ├── LoginView.vue     # 登录页
│   │   │   ├── CodeDetailView.vue # 代码详情页
│   │   │   └── AdminView.vue     # 管理后台
│   │   ├── components/       # 通用组件
│   │   │   ├── MainLayout.vue    # 主布局
│   │   │   └── CodeEditor.vue    # 代码编辑器
│   │   ├── utils/            # 工具函数
│   │   │   ├── http.ts          # HTTP 请求封装
│   │   │   ├── cache.ts         # 前端缓存
│   │   │   └── validation.ts    # 表单验证
│   │   ├── router/           # 路由配置
│   │   └── config/           # 配置文件
│   ├── dist/                 # 构建产物 (生产环境使用)
│   └── package.json          # 前端依赖配置
│
├── docker/                     # Docker 相关配置
│   ├── nginx.conf            # Nginx 配置文件
│   ├── supervisord.conf      # Supervisor 进程管理配置
│   └── start.sh              # 容器启动脚本
│
├── Dockerfile                  # Docker 镜像构建文件
├── docker-compose.yml          # Docker Compose 编排文件
├── deploy.sh                   # 一键部署脚本
├── requirements.txt            # Python 依赖列表
├── .env.example               # 环境变量模板
└── README.md                  # 项目说明文档
```

---

## 功能特性

### 用户功能

- **用户注册与登录**: 支持邮箱注册，JWT 令牌认证
- **个人中心**: 查看和管理自己发布的代码
- **代码发布**: 支持代码片段和 Markdown 文档两种模式
- **代码浏览**: 按语言、分类、标签筛选代码
- **代码搜索**: 全文搜索代码标题和描述
- **评论互动**: 对代码进行评论和讨论
- **代码导出**: 支持源码、Markdown、JSON、ZIP 格式导出

### 管理员功能

- **用户管理**: 查看用户列表，修改用户角色和状态
- **内容审核**: 审核待发布的代码，批准或拒绝
- **评论管理**: 查看和删除不当评论

### 支持的编程语言

| 语言 | 扩展名 | 说明 |
|------|--------|------|
| Python | .py | 通用编程语言 |
| R | .R | 统计分析语言 |
| Shell | .sh | 命令行脚本 |
| Perl | .pl | 文本处理语言 |
| Rust | .rs | 系统编程语言 |
| MATLAB | .m | 数值计算语言 |
| Julia | .jl | 科学计算语言 |
| Nextflow | .nf | 生信流程语言 |
| Snakemake | .smk | 生信流程语言 |
| WDL | .wdl | 工作流描述语言 |
| AWK | .awk | 文本处理工具 |

---

## 故障排查

### 问题1：端口被占用

**现象：** 部署时提示端口 8080 已被占用

**解决方法：**

```bash
# 查看端口占用情况
lsof -i :8080
# 或
netstat -tlnp | grep 8080

# 方法1: 停止占用端口的进程
kill -9 <PID>

# 方法2: 修改应用端口
# 编辑 docker-compose.yml，修改端口映射
ports:
  - "8081:80"  # 将 8080 改为 8081
```

### 问题2：容器启动失败

**现象：** `docker-compose ps` 显示容器状态为 Exit 或 Restarting

**解决方法：**

```bash
# 查看详细错误日志
docker-compose logs app

# 常见原因及解决：
# 1. 配置文件错误 - 检查 .env 文件格式
# 2. 端口冲突 - 参考问题1
# 3. 内存不足 - 增加服务器内存或 swap

# 检查配置文件语法
docker-compose config
```

### 问题3：数据库连接失败

**现象：** 应用日志显示数据库连接错误

**解决方法：**

```bash
# 检查 MySQL 容器状态
docker-compose logs mysql

# 等待 MySQL 完全启动 (首次启动可能需要1-2分钟)
docker-compose logs -f mysql

# 测试数据库连接
docker-compose exec app python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database connection OK')
"
```

### 问题4：前端页面空白

**现象：** 访问应用显示空白页面

**解决方法：**

```bash
# 检查 Nginx 日志
docker-compose exec app cat /var/log/nginx/error.log

# 检查前端文件是否存在
docker-compose exec app ls -la /app/frontend/dist/

# 如果 dist 目录为空，需要重新构建前端
# 在本地执行:
cd frontend
npm run build
git add .
git commit -m "Build frontend"
git push

# 服务器上重新部署
git pull
docker-compose up -d --build
```

### 问题5：API 请求 401 错误

**现象：** 登录后访问 API 返回 401 Unauthorized

**解决方法：**

```bash
# 检查 JWT 密钥配置
cat .env | grep JWT_SECRET_KEY

# 确保密钥不为空且格式正确
# 重启应用使配置生效
docker-compose restart app
```

---

## 数据备份与恢复

### SQLite 备份

```bash
# 备份数据库
docker cp $(docker-compose ps -q app):/app/backend/instance/bio_code_share.db ./backup_$(date +%Y%m%d).db

# 恢复数据库
docker cp ./backup_20240101.db $(docker-compose ps -q app):/app/backend/instance/bio_code_share.db
docker-compose restart app
```

### MySQL 备份

```bash
# 备份数据库
docker-compose exec mysql mysqldump -u root -p bio_code_share > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker-compose exec -T mysql mysql -u root -p bio_code_share < backup_20240101.sql
```

### 定时备份 (使用 cron)

```bash
# 编辑 crontab
crontab -e

# 添加每日凌晨2点备份任务
0 2 * * * cd /path/to/Code-platform && docker cp $(docker-compose ps -q app):/app/backend/instance/bio_code_share.db /backup/bio_code_share_$(date +\%Y\%m\%d).db
```

---

## 安全建议

1. **修改默认密钥**: 务必修改 `.env` 中的 `JWT_SECRET_KEY`
2. **使用 HTTPS**: 生产环境建议配置 SSL 证书
3. **定期备份**: 设置定时任务自动备份数据库
4. **更新依赖**: 定期更新 Python 和 npm 依赖包
5. **限制访问**: 使用防火墙限制不必要的端口访问
6. **强密码**: MySQL 使用强密码，避免使用默认密码

---

## 许可证

MIT License

---

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

GitHub: https://github.com/Wangjien/Code-platform

Email: wangje1569399536@163.com
