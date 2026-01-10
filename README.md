# 平台效果
![平台效果](imgs/image1.png)
![平台效果](imgs/image2.png)

# 本地开发启动

## 后端（Flask）

后端目录：`backend/`

```bash
cd backend

# 如已有 venv 可直接激活使用，否则建议新建 .venv
python app.py
```

默认端口：`http://localhost:5001`

## 前端（Vite + Vue3）

前端目录：`frontend/`

```bash
cd frontend
npm install
npm run dev
```

默认地址：`http://localhost:5173`

## 数据库迁移（SQLite，手动执行一次）

当前项目使用 `db.create_all()`，它不会自动给已有表“加列”。
如果你已经有历史数据库（例如 `backend/instance/bio_code_share.db`），在启用“后台管理 + 审核机制”前需要先手动迁移一次。

打开 SQLite 并执行（仅一次）：

```bash
sqlite3 backend/instance/bio_code_share.db
```

在 sqlite 交互界面执行：

```sql
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1;

ALTER TABLE codes ADD COLUMN status VARCHAR(20) DEFAULT 'approved';
ALTER TABLE codes ADD COLUMN reviewed_by INTEGER;
ALTER TABLE codes ADD COLUMN reviewed_at DATETIME;
ALTER TABLE codes ADD COLUMN review_reason TEXT;
```

说明：
- `status`：`pending/approved/rejected/disabled`
- 旧数据默认 `approved`，避免迁移后历史内容不可见

## 初始化首个管理员（一次性）

因为“后台提权(A3)”需要系统里先存在至少 1 个管理员，所以提供一个本地脚本用于初始化首个管理员。

```bash
python3 make_admin.py --email test@example.com
```

初始化后重新登录前端（刷新本地 `user` 信息），即可看到右上角下拉菜单的“后台管理”入口，或直接访问：

`http://localhost:5173/admin`

# Docker 部署指南
## 快速部署
### 1. 前置要求
- Docker 20.10+
- Docker Compose 2.0+

### 2. 一键部署

```bash
# 进入项目根目录
cd 代码分享平台

# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 访问地址
- 前端: http://localhost
- 后端 API: http://localhost/api

## 配置说明

### 环境变量
创建 `.env` 文件配置敏感信息：

```bash
# JWT 密钥 (生产环境必须修改)
JWT_SECRET_KEY=your-super-secret-key-change-in-production

# 如果使用 MySQL (可选)
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_USER=biocode
MYSQL_PASSWORD=biocode123
```

### 使用 MySQL 数据库

1. 编辑 `docker-compose.yml`，取消 MySQL 服务的注释

2. 修改后端环境变量：
```yaml
environment:
  - DATABASE_URI=mysql+pymysql://biocode:biocode123@mysql:3306/bio_code_share
```

3. 重新部署：
```bash
docker-compose down
docker-compose up -d --build
```

## 常用命令

```bash
# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看后端日志
docker-compose logs -f backend

# 进入后端容器
docker-compose exec backend sh

# 清理未使用的镜像
docker system prune -a
```

## 数据备份

### SQLite 数据备份
```bash
# 备份数据库
docker-compose exec backend cp /app/instance/bio_code_share.db /app/instance/backup.db
docker cp $(docker-compose ps -q backend):/app/instance/backup.db ./backup.db
```

### MySQL 数据备份 (如使用)
```bash
docker-compose exec mysql mysqldump -u root -p bio_code_share > backup.sql
```

## 外网部署配置

### 1. 创建 .env 配置文件

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置
vim .env
```

### 2. 配置内容

```bash
# JWT 密钥 (必须修改！)
JWT_SECRET_KEY=your-random-secret-key-at-least-32-characters

# 允许的域名 (填写您的域名或IP)
ALLOWED_ORIGINS=https://your-domain.com
# 多个域名用逗号分隔: https://domain1.com,https://domain2.com
```

### 3. 服务器防火墙

```bash
# 开放 80 端口 (HTTP)
sudo ufw allow 80

# 开放 443 端口 (HTTPS)
sudo ufw allow 443

# 如果使用云服务器，还需在安全组中开放对应端口
```

### 4. 配置 HTTPS (推荐)

修改 `frontend/nginx.conf`：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # ... 其余配置不变
}
```

### 5. 重新部署

```bash
docker-compose down
docker-compose up -d --build
```

## 生产环境建议

1. **HTTPS**: 使用 Let's Encrypt 免费 SSL 证书
2. **JWT 密钥**: 使用 `openssl rand -hex 32` 生成随机密钥
3. **数据库**: 生产环境建议使用 MySQL 或 PostgreSQL
4. **监控**: 添加日志收集和监控告警
5. **备份**: 定期备份数据库
6. **域名**: 使用域名而非 IP 地址访问
