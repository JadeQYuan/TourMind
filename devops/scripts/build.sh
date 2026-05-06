#!/usr/bin/env bash
# build.sh — 构建并打包 TourMind Docker 镜像
# 用法: ./build.sh [TAG]
#
# 版本号策略:
#   不传 TAG  → 自动从 git 生成:
#               有 tag  → v1.0.0                 (正式发布)
#               无 tag  → v1.0.0-3-gabcdef       (含偏移量+哈希)
#               工作区脏 → v1.0.0-3-gabcdef+dirty
#               无任何 tag → 回落到时间戳 20260416.1430
#   传 TAG    → 直接使用，如 v1.1.0 或 20260416-hotfix
#
#   推荐发布流:
#     git tag v1.0.0 && ./build.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEVOPS="${SCRIPT_DIR}/.."
ROOT="${DEVOPS}/.."
DIST="${DEVOPS}/dist"

log()  { echo -e "\033[36m[BUILD]\033[0m $*"; }
ok()   { echo -e "\033[32m[OK]\033[0m    $*"; }
err()  { echo -e "\033[31m[ERR]\033[0m   $*"; exit 1; }

# ---------- 版本号 ----------
if [ -n "${1:-}" ]; then
    TAG="${1}"
else
    TAG=$(git -C "${ROOT}" describe --tags --always --dirty="+dirty" 2>/dev/null \
          || date +%Y%m%d.%H%M)
fi

# 本地镜像始终用 tourmind/ 前缀（与 docker-compose.yml 中 image: 字段一致）
LOCAL_PREFIX="tourmind"
BUNDLE="${DIST}/tourmind-${TAG}.tar.gz"

log "版本: ${TAG}"
mkdir -p "${DIST}"

# ---------- 依赖检查 ----------
command -v npm    &>/dev/null || err "未找到 npm 命令，请安装 Node.js 20+"
command -v docker &>/dev/null || err "未找到 docker 命令"

# ---------- 退出时自动清理临时产物 ----------
cleanup() {
    log "清理临时构建产物..."
    rm -rf "${ROOT}/backend/packages"
    rm -rf "${ROOT}/frontend/dist"
}
trap cleanup EXIT

# ---------- 前端编译 ----------
log "编译前端..."
cd "${ROOT}/frontend"
npm ci --prefer-offline
npm run build
ok "前端编译完成 → frontend/dist/"

# ---------- 后端依赖（在 python:3.10-slim 容器内安装，确保 Linux 平台兼容性）----------
log "安装后端依赖..."
BACKEND_PKGS="${ROOT}/backend/packages"
rm -rf "${BACKEND_PKGS}"
docker run --rm \
    -v "${ROOT}/backend/requirements.txt:/requirements.txt:ro" \
    -v "${BACKEND_PKGS}:/packages" \
    python:3.10-slim \
    pip install --no-cache-dir --target /packages -r /requirements.txt
ok "后端依赖安装完成"

# ---------- backend ----------
log "构建 backend 镜像..."
docker build \
    -t "${LOCAL_PREFIX}/backend:${TAG}" \
    -t "${LOCAL_PREFIX}/backend:latest" \
    -f "${ROOT}/backend/Dockerfile" \
    "${ROOT}/backend"
ok "backend:${TAG}"

# ---------- nginx（使用已编译的前端静态文件）----------
log "构建 nginx 镜像..."
docker build \
    -t "${LOCAL_PREFIX}/nginx:${TAG}" \
    -t "${LOCAL_PREFIX}/nginx:latest" \
    -f "${ROOT}/frontend/Dockerfile" \
    "${ROOT}/frontend"
ok "nginx:${TAG}"

# ---------- 打包发布包 ----------
log "打包发布包 → $(basename "${BUNDLE}") ..."
docker save \
    "${LOCAL_PREFIX}/backend:${TAG}" \
    "${LOCAL_PREFIX}/nginx:${TAG}" \
    | gzip -9 > "${BUNDLE}"

BUNDLE_SIZE=$(du -sh "${BUNDLE}" | cut -f1)
ok "发布包: ${BUNDLE}  (${BUNDLE_SIZE})"

echo ""
echo "──────────────────────────────────────────────────"
printf "  %-10s %s\n" "版本:"   "${TAG}"
printf "  %-10s %s\n" "发布包:" "${BUNDLE}"
printf "  %-10s %s\n" "部署:"   "./deploy.sh up ${TAG} ${BUNDLE}"
echo "──────────────────────────────────────────────────"

