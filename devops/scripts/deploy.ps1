#!/usr/bin/env pwsh
# deploy.ps1 — 部署 / 更新 TourMind 服务
# 用法: .\deploy.ps1 [-Action up|restart|stop|logs|status] [-Tag "v1.0.0"] [-Bundle ".\dist\tourmind-v1.0.0.tar.gz"]
#   -Bundle 有则先 docker load，无则直接用已有镜像

param(
    [ValidateSet("up","restart","stop","logs","status")]
    [string]$Action  = "up",
    [string]$Tag     = "latest",
    [string]$Bundle  = "",
    [string]$EnvFile = "$PSScriptRoot\..\.env"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$DEVOPS  = $PSScriptRoot
$COMPOSE = "$DEVOPS\docker-compose.yml"

function Log($msg) { Write-Host "[DEPLOY] $msg" -ForegroundColor Cyan }
function Ok($msg)  { Write-Host "[OK]     $msg" -ForegroundColor Green }
function Err($msg) { Write-Host "[ERR]    $msg" -ForegroundColor Red; exit 1 }

# ---------- 检查依赖 ----------
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Err "未找到 docker 命令" }

# ---------- 检查 .env ----------
if (-not (Test-Path $EnvFile)) {
    Err ".env 文件不存在: $EnvFile`n请先复制 devops/.env.example 到项目根目录并填写配置"
}
Log "使用环境配置: $EnvFile"

# ---------- 注入 TAG 环境变量（供 compose 使用） ----------
$env:TOURMIND_TAG = $Tag

# ---------- 执行操作 ----------
switch ($Action) {
    "up" {
        # 加载镜像（从发布包 或 registry）
        if ($Bundle -ne "") {
            if (-not (Test-Path $Bundle)) { Err "发布包不存在: $Bundle" }
            Log "从发布包加载镜像: $(Split-Path -Leaf $Bundle) ..."
            Get-Content -Encoding Byte $Bundle | docker load
            if ($LASTEXITCODE -ne 0) { Err "镜像加载失败" }
            Ok "镜像加载完成"
            $upFlags = "--no-build"
        } else {
            Log "拉取基础镜像..."
            docker compose -f $COMPOSE pull db
            $upFlags = ""
        }

        Log "启动服务（Tag=$Tag）..."
        $cmdArgs = @("-f", $COMPOSE, "up", "-d", "--remove-orphans")
        if ($upFlags) { $cmdArgs += $upFlags }
        docker compose @cmdArgs
        if ($LASTEXITCODE -ne 0) { Err "启动失败" }

        Log "等待数据库就绪..."
        Start-Sleep -Seconds 5

        Log "执行数据库迁移..."
        docker exec tourmind-api alembic upgrade head
        if ($LASTEXITCODE -ne 0) { Err "数据库迁移失败" }

        Ok "部署完成"
        docker compose -f $COMPOSE ps
    }
    "restart" {
        Log "重启服务..."
        docker compose -f $COMPOSE restart
        Ok "重启完成"
    }
    "stop" {
        Log "停止服务..."
        docker compose -f $COMPOSE down
        Ok "已停止（数据卷保留）"
    }
    "logs" {
        docker compose -f $COMPOSE logs -f --tail=100
    }
    "status" {
        docker compose -f $COMPOSE ps
    }
}
