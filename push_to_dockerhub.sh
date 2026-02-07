#!/bin/bash
# ============================================================
# 推送镜像到 Docker Hub
# ============================================================
# 使用方式：
#   ./push_to_dockerhub.sh [版本号]
#   ./push_to_dockerhub.sh 1.0.0
#   ./push_to_dockerhub.sh latest
# ============================================================

set -euo pipefail

# Docker Hub 用户名（请修改为你的用户名）
DOCKERHUB_USER=${DOCKERHUB_USER:-wangjien}
IMAGE_NAME="code-platform"
VERSION=${1:-latest}

FULL_IMAGE_NAME="${DOCKERHUB_USER}/${IMAGE_NAME}"

echo "=============================================="
echo "推送镜像到 Docker Hub"
echo "=============================================="
echo "镜像: ${FULL_IMAGE_NAME}:${VERSION}"
echo ""

# 检查是否在项目根目录
if [[ ! -f "./Dockerfile" ]]; then
    echo "[ERROR] 请在项目根目录执行该脚本"
    exit 1
fi

# 检查前端是否已构建
if [[ ! -f "./frontend/dist/index.html" ]]; then
    echo "[WARN] 未检测到 ./frontend/dist/index.html"
    echo "[INFO] 正在构建前端..."
    cd frontend
    npm ci
    npm run build
    cd ..
fi

# 登录 Docker Hub（如果未登录）
echo "[INFO] 检查 Docker Hub 登录状态..."
if ! docker info 2>/dev/null | grep -q "Username"; then
    echo "[INFO] 请登录 Docker Hub..."
    docker login
fi

# 构建镜像
echo "[INFO] 构建镜像: ${FULL_IMAGE_NAME}:${VERSION}"
docker build -t "${FULL_IMAGE_NAME}:${VERSION}" .

# 如果版本不是 latest，同时打上 latest 标签
if [[ "$VERSION" != "latest" ]]; then
    echo "[INFO] 同时标记为 latest..."
    docker tag "${FULL_IMAGE_NAME}:${VERSION}" "${FULL_IMAGE_NAME}:latest"
fi

# 推送镜像
echo "[INFO] 推送镜像到 Docker Hub..."
docker push "${FULL_IMAGE_NAME}:${VERSION}"

if [[ "$VERSION" != "latest" ]]; then
    docker push "${FULL_IMAGE_NAME}:latest"
fi

echo ""
echo "=============================================="
echo "[OK] 镜像推送成功！"
echo "=============================================="
echo ""
echo "用户可以通过以下方式拉取镜像："
echo "  docker pull ${FULL_IMAGE_NAME}:${VERSION}"
echo ""
echo "或使用 docker-compose.hub.yml 一键部署："
echo "  curl -O https://raw.githubusercontent.com/Wangjien/Code-platform/master/docker-compose.hub.yml"
echo "  curl -O https://raw.githubusercontent.com/Wangjien/Code-platform/master/.env.example"
echo "  cp .env.example .env"
echo "  # 编辑 .env 配置"
echo "  docker compose -f docker-compose.hub.yml up -d"
echo ""
