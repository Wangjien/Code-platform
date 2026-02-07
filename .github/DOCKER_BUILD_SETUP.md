# GitHub Actions Docker 镜像自动构建配置指南

本文档说明如何配置 GitHub Actions 自动构建并发布 Docker 镜像。

## 前置条件

1. 拥有 Docker Hub 账号
2. 拥有 GitHub 仓库的管理员权限

## 配置步骤

### 1. 创建 Docker Hub Access Token

1. 登录 [Docker Hub](https://hub.docker.com/)
2. 点击右上角头像 → **Account Settings**
3. 选择 **Security** → **New Access Token**
4. 输入 Token 描述（如 `github-actions`）
5. 选择权限：**Read, Write, Delete**
6. 点击 **Generate**，复制生成的 Token

### 2. 配置 GitHub Secrets

在 GitHub 仓库中配置以下 Secrets：

1. 进入仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**，添加以下两个 Secret：

| Secret 名称 | 值 |
|-------------|-----|
| `DOCKERHUB_USERNAME` | 你的 Docker Hub 用户名 |
| `DOCKERHUB_TOKEN` | 上一步生成的 Access Token |

### 3. 修改镜像仓库名称（可选）

如果你的 Docker Hub 用户名不是 `wangjien`，需要修改工作流文件：

编辑 `.github/workflows/docker-build.yml` 和 `.github/workflows/release.yml`：

```yaml
env:
  DOCKERHUB_REPO: 你的用户名/code-platform
  GHCR_REPO: ghcr.io/你的用户名/code-platform
```

## 触发构建

### 自动触发

| 事件 | 镜像标签 |
|------|----------|
| 推送到 `master`/`main` 分支 | `latest` |
| 创建 Release (如 `v1.0.0`) | `1.0.0`, `1.0`, `1`, `latest` |
| Pull Request | `pr-123`（仅构建，不推送） |

### 手动触发

1. 进入仓库 → **Actions** → **Build and Push Docker Image**
2. 点击 **Run workflow**
3. 可选填写自定义标签

## 发布新版本

1. 在 GitHub 仓库点击 **Releases** → **Create a new release**
2. 创建新 Tag，格式：`v1.0.0`（遵循语义化版本）
3. 填写 Release 标题和说明
4. 点击 **Publish release**

发布后会自动：
- 构建 Docker 镜像
- 推送到 Docker Hub 和 GHCR
- 生成 `tar.gz` 镜像文件并附加到 Release
- 更新 Release Notes 添加拉取命令

## 镜像使用

### 从 Docker Hub 拉取

```bash
docker pull wangjien/code-platform:latest
docker pull wangjien/code-platform:1.0.0
```

### 从 GitHub Container Registry 拉取

```bash
docker pull ghcr.io/wangjien/code-platform:latest
docker pull ghcr.io/wangjien/code-platform:1.0.0
```

### 使用离线镜像包

从 Release 页面下载 `code-platform-x.x.x.tar.gz`：

```bash
# 验证校验和
sha256sum -c code-platform-1.0.0.tar.gz.sha256

# 导入镜像
gunzip -c code-platform-1.0.0.tar.gz | docker load

# 启动
docker compose -f docker-compose.hub.yml up -d
```

## 常见问题

### Q: 构建失败，提示权限不足

确保已正确配置 `DOCKERHUB_USERNAME` 和 `DOCKERHUB_TOKEN` Secrets。

### Q: 推送到 GHCR 失败

检查仓库 Settings → Actions → General → Workflow permissions，确保选择了 **Read and write permissions**。

### Q: 前端构建失败

确保 `frontend/package-lock.json` 文件已提交到仓库。

## 支持的平台

镜像支持以下 CPU 架构：
- `linux/amd64` (Intel/AMD 64位)
- `linux/arm64` (ARM 64位，如 Apple M1/M2、树莓派4)
