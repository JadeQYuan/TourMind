#!/usr/bin/env bash
# deploy.sh — 部署 / 更新 TourMind 服务
# 用法: ./deploy.sh [ACTION] [TAG] [BUNDLE]
#   ACTION: up（默认）| restart | stop | logs | status
#   TAG:    镜像标签，默认 latest
#   BUNDLE: 发布包路径（.tar.gz），有则先 docker load，无则直接用已有镜像

set -euo pipefail

ACTION="${1:-up}"
TAG="${2:-latest}"
BUNDLE="${3:-}"
DEVOPS="$(cd "$(dirname "$0")" && pwd)"
COMPOSE="${DEVOPS}/docker-compose.yml"
ENV_FILE="${DEVOPS}/../.env"

log()  { echo -e "\033[36m[DEPLOY]\033[0m $*"; }
ok()   { echo -e "\033[32m[OK]\033[0m     $*"; }
err()  { echo -e "\033[31m[ERR]\033[0m    $*"; exit 1; }

# ---------- 检查依赖 ----------
command -v docker &>/dev/null || err "未找到 docker 命令"

# ---------- 检查 .env ----------
[ -f "${ENV_FILE}" ] || err ".env 文件不存在: ${ENV_FILE}
请先复制 devops/.env.example 到项目根目录并填写配置"
log "使用环境配置: ${ENV_FILE}"

export TOURMIND_TAG="${TAG}"

# ---------- 执行操作 ----------
case "${ACTION}" in
    up)
        # 加载镜像（从发布包 或 registry）
        if [ -n "${BUNDLE}" ]; then
            [ -f "${BUNDLE}" ] || err "发布包不存在: ${BUNDLE}"
            log "从发布包加载镜像: $(basename "${BUNDLE}") ..."
            docker load < "${BUNDLE}"
            ok "镜像加载完成"
            COMPOSE_UP_FLAGS="--no-build"
        else
            log "拉取基础镜像..."
            docker compose -f "${COMPOSE}" pull db
            COMPOSE_UP_FLAGS=""
        fi

        log "启动服务（Tag=${TAG}）..."
        # shellcheck disable=SC2086
        docker compose -f "${COMPOSE}" up -d --remove-orphans ${COMPOSE_UP_FLAGS}

        log "等待数据库就绪..."
        sleep 5

        log "执行数据库迁移..."
        docker exec tourmind-api alembic upgrade head

        ok "部署完成"
        docker compose -f "${COMPOSE}" ps
        ;;
    restart)
        log "重启服务..."
        docker compose -f "${COMPOSE}" restart
        ok "重启完成"
        ;;
    stop)
        log "停止服务..."
        docker compose -f "${COMPOSE}" down
        ok "已停止（数据卷保留）"
        ;;
    logs)
        docker compose -f "${COMPOSE}" logs -f --tail=100
        ;;
    status)
        docker compose -f "${COMPOSE}" ps
        ;;
    *)
        err "未知操作: ${ACTION}，可选: up | restart | stop | logs | status"
        ;;
esac

