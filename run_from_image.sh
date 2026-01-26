#!/bin/bash
set -euo pipefail

IMAGE_TAR_GZ=${1:-}
IMAGE_TAG=${2:-}
ENV_FILE=${3:-.env}

if [[ -z "$IMAGE_TAR_GZ" ]]; then
  echo "用法: ./run_from_image.sh <image.tar.gz> [image_tag] [.env路径]"
  echo "示例: ./run_from_image.sh image_release/code-platform__release-20260126120000.tar.gz code-platform:release-20260126120000 .env"
  exit 1
fi

if [[ ! -f "$IMAGE_TAR_GZ" ]]; then
  echo "[ERROR] 找不到镜像文件: $IMAGE_TAR_GZ"
  exit 1
fi

if [[ ! -f "./docker-compose.yml" ]]; then
  echo "[ERROR] 请在项目根目录执行该脚本（docker-compose.yml 不存在）"
  exit 1
fi

# 选择 compose 命令
COMPOSE_CMD=""
if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  echo "[ERROR] Docker Compose 未安装（需要 docker compose 或 docker-compose）"
  exit 1
fi

# 可选校验 sha256
SHA_FILE="$IMAGE_TAR_GZ.sha256"
if [[ -f "$SHA_FILE" ]]; then
  echo "[INFO] 检测到校验文件: $SHA_FILE，开始校验..."
  if command -v sha256sum >/dev/null 2>&1; then
    (cd "$(dirname "$SHA_FILE")" && sha256sum -c "$(basename "$SHA_FILE")")
  elif command -v shasum >/dev/null 2>&1; then
    expected=$(awk '{print $1}' "$SHA_FILE")
    actual=$(shasum -a 256 "$IMAGE_TAR_GZ" | awk '{print $1}')
    if [[ "$expected" != "$actual" ]]; then
      echo "[ERROR] sha256 校验失败"
      exit 1
    fi
  else
    echo "[WARN] 未找到 sha256sum/shasum，跳过校验"
  fi
  echo "[OK] sha256 校验通过"
fi

# 导入镜像
TMP_TAR=""
if [[ "$IMAGE_TAR_GZ" == *.gz ]]; then
  TMP_TAR=$(mktemp -t code_platform_image_XXXXXX.tar)
  echo "[INFO] 解压镜像包..."
  gunzip -c "$IMAGE_TAR_GZ" > "$TMP_TAR"
  echo "[INFO] 导入镜像..."
  docker load -i "$TMP_TAR"
  rm -f "$TMP_TAR"
else
  echo "[INFO] 导入镜像..."
  docker load -i "$IMAGE_TAR_GZ"
fi

# 确定镜像 tag
if [[ -z "$IMAGE_TAG" ]]; then
  IMAGE_TAG=$(docker images --format "{{.Repository}}:{{.Tag}}" | head -n 1)
  echo "[WARN] 未指定 image_tag，临时使用: $IMAGE_TAG"
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[WARN] 未找到 env 文件: $ENV_FILE，将继续启动（但强烈建议配置 JWT_SECRET_KEY / ALLOWED_ORIGINS / DATABASE_URI）"
fi

OVERRIDE_FILE="docker-compose.image.override.yml"
cat > "$OVERRIDE_FILE" <<EOF
services:
  app:
    image: ${IMAGE_TAG}
    build: null
EOF

echo "[INFO] 使用镜像启动（跳过构建）: $IMAGE_TAG"
if [[ -f "$ENV_FILE" ]]; then
  $COMPOSE_CMD --env-file "$ENV_FILE" -f docker-compose.yml -f "$OVERRIDE_FILE" up -d
else
  $COMPOSE_CMD -f docker-compose.yml -f "$OVERRIDE_FILE" up -d
fi

echo "[OK] 启动完成"
echo "[OK] 访问: http://<服务器IP>:8080"
echo "[INFO] 查看日志: $COMPOSE_CMD logs -f --tail=200"
