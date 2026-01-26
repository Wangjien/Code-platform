#!/bin/bash
set -euo pipefail

TAG=${1:-code-platform:release-$(date +%Y%m%d%H%M%S)}
OUT_DIR=${2:-./image_release}

if [[ ! -f "./Dockerfile" ]]; then
  echo "[ERROR] 请在项目根目录执行该脚本（Dockerfile 不存在）"
  exit 1
fi

if [[ ! -f "./frontend/dist/index.html" ]]; then
  echo "[WARN] 未检测到 ./frontend/dist/index.html"
  echo "[WARN] 当前 Dockerfile 会 COPY frontend/dist 到镜像中；如果 dist 不存在会导致镜像无法正常提供前端页面"
fi

mkdir -p "$OUT_DIR"

echo "[INFO] 构建镜像: $TAG"
docker build -t "$TAG" .

safe_tag=$(echo "$TAG" | tr '/:' '__')
TAR_PATH="$OUT_DIR/${safe_tag}.tar"
GZ_PATH="$TAR_PATH.gz"
SHA_PATH="$GZ_PATH.sha256"

echo "[INFO] 导出镜像到: $GZ_PATH"
docker save "$TAG" -o "$TAR_PATH"
gzip -f "$TAR_PATH"

if command -v sha256sum >/dev/null 2>&1; then
  sha256sum "$GZ_PATH" > "$SHA_PATH"
elif command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "$GZ_PATH" > "$SHA_PATH"
else
  echo "[WARN] 未找到 sha256sum/shasum，跳过生成校验文件"
fi

echo "[OK] 镜像导出完成"
echo "[OK] 镜像名: $TAG"
echo "[OK] 文件: $GZ_PATH"
