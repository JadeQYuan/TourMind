#!/usr/bin/env pwsh
# build.ps1 — 构建并打包 TourMind Docker 镜像
# 用法: .\build.ps1 [-Tag "v1.0.0"]
#
# 版本号策略:
#   不传 -Tag  → 自动从 git 生成:
#               有 tag  → v1.0.0
#               无 tag  → v1.0.0-3-gabcdef
#               工作区脏 → v1.0.0-3-gabcdef+dirty
#               无任何 tag → 回落到时间戳 20260416.1430
#   传 -Tag   → 直接使用

param(
    [string]$Tag = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$DEVOPS = Split-Path -Parent $PSScriptRoot
$ROOT   = Split-Path -Parent $DEVOPS
$DIST   = "$DEVOPS\dist"

function Log($msg) { Write-Host "[BUILD] $msg" -ForegroundColor Cyan }
function Ok($msg)  { Write-Host "[OK]    $msg" -ForegroundColor Green }
function Err($msg) { Write-Host "[ERR]   $msg" -ForegroundColor Red; exit 1 }

# ---------- 版本号 ----------
if ($Tag -eq "") {
    $gitTag = git -C $ROOT describe --tags --always --dirty="+dirty" 2>$null
    $Tag = if ($gitTag) { $gitTag } else { Get-Date -Format "yyyyMMdd.HHmm" }
}

# 本地镜像始终用 tourmind/ 前缀（与 docker-compose.yml 中 image: 字段一致）
$LOCAL_PREFIX = "tourmind"
$BUNDLE = "$DIST\tourmind-${Tag}.tar.gz"

Log "版本: $Tag"
New-Item -ItemType Directory -Force -Path $DIST | Out-Null

# ---------- 依赖检查 ----------
if (-not (Get-Command npm    -ErrorAction SilentlyContinue)) { Err "未找到 npm 命令，请安装 Node.js 20+" }
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Err "未找到 docker 命令" }

$BACKEND_PKGS = "$ROOT\backend\packages"

try {
    # ---------- 前端编译 ----------
    Log "编译前端..."
    Push-Location "$ROOT\frontend"
    npm ci --prefer-offline
    if ($LASTEXITCODE -ne 0) { Err "npm ci 失败" }
    npm run build
    if ($LASTEXITCODE -ne 0) { Err "前端编译失败" }
    Pop-Location
    Ok "前端编译完成 → frontend/dist/"

    # ---------- 后端依赖（在 python:3.10-slim 容器内安装，确保 Linux 平台兼容性）----------
    Log "安装后端依赖..."
    Remove-Item -Recurse -Force $BACKEND_PKGS -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $BACKEND_PKGS | Out-Null
    # Windows 路径需转换为 Docker 兼容格式
    $reqPath  = (Resolve-Path "$ROOT\backend\requirements.txt").Path -replace '\\', '/'
    $pkgsPath = (Resolve-Path $BACKEND_PKGS).Path -replace '\\', '/'
    docker run --rm `
        -v "${reqPath}:/requirements.txt:ro" `
        -v "${pkgsPath}:/packages" `
        python:3.10-slim `
        pip install --no-cache-dir --target /packages -r /requirements.txt
    if ($LASTEXITCODE -ne 0) { Err "后端依赖安装失败" }
    Ok "后端依赖安装完成"

    # ---------- 构建 backend ----------
    Log "构建 backend 镜像..."
    docker build `
        -t "${LOCAL_PREFIX}/backend:${Tag}" `
        -t "${LOCAL_PREFIX}/backend:latest" `
        -f "$ROOT\backend\Dockerfile" `
        "$ROOT\backend"
    if ($LASTEXITCODE -ne 0) { Err "backend 构建失败" }
    Ok "backend:${Tag}"

    # ---------- 构建 nginx（使用已编译的前端静态文件）----------
    Log "构建 nginx 镜像..."
    docker build `
        -t "${LOCAL_PREFIX}/nginx:${Tag}" `
        -t "${LOCAL_PREFIX}/nginx:latest" `
        -f "$ROOT\frontend\Dockerfile" `
        "$ROOT\frontend"
    if ($LASTEXITCODE -ne 0) { Err "nginx 构建失败" }
    Ok "nginx:${Tag}"

} finally {
    # ---------- 清理临时构建产物 ----------
    Log "清理临时构建产物..."
    Remove-Item -Recurse -Force $BACKEND_PKGS -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "$ROOT\frontend\dist" -ErrorAction SilentlyContinue
}

# ---------- 打包发布包 ----------
Log "打包发布包 → tourmind-${Tag}.tar.gz ..."
docker save `
    "${LOCAL_PREFIX}/backend:${Tag}" `
    "${LOCAL_PREFIX}/nginx:${Tag}" `
    | & { param($input) $input | Set-Content -Encoding Byte $BUNDLE }
if ($LASTEXITCODE -ne 0) { Err "打包失败" }
$bundleSize = "{0:N1} MB" -f ((Get-Item $BUNDLE).Length / 1MB)
Ok "发布包: $BUNDLE  ($bundleSize)"

Write-Host ""
Write-Host "──────────────────────────────────────────────────"
Write-Host ("  {0,-10} {1}" -f "版本:",   $Tag)
Write-Host ("  {0,-10} {1}" -f "发布包:", $BUNDLE)
Write-Host ("  {0,-10} {1}" -f "部署:",   ".\deploy.ps1 -Tag '$Tag' -Bundle '$BUNDLE'")
Write-Host "──────────────────────────────────────────────────"
