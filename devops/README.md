# TourMind DevOps

本目录包含 TourMind 的构建与部署脚本。

## 目录结构

```
devops/
├── docker-compose.yml      # 服务编排（db / backend / nginx）
├── .env.example            # 环境变量模板
├── dist/                   # 构建产物（.tar.gz 发布包，已 git ignore）
└── scripts/
    ├── build.sh / build.ps1    # 构建 + 打包
    └── deploy.sh / deploy.ps1  # 部署 + 迁移
```

---

## 快速开始

### 1. 准备环境配置

```bash
cp devops/.env.example .env
# 编辑 .env，填写数据库密码、SECRET_KEY 等
```

### 2. 构建发布包

**Linux / macOS**
```bash
cd devops/scripts
./build.sh               # 自动从 git 生成版本号
./build.sh v1.2.0        # 指定版本号
```

**Windows (PowerShell)**
```powershell
cd devops\scripts
.\build.ps1              # 自动从 git 生成版本号
.\build.ps1 -Tag v1.2.0  # 指定版本号
```

构建完成后输出：
```
  版本:       v1.2.0
  发布包:     devops/dist/tourmind-v1.2.0.tar.gz
  部署:       ./deploy.sh up v1.2.0 devops/dist/tourmind-v1.2.0.tar.gz
```

### 3. 部署

将发布包（`.tar.gz`）传到服务器后执行：

**Linux / macOS**
```bash
# 首次部署 / 版本升级（从发布包加载镜像）
./deploy.sh up v1.2.0 /path/to/tourmind-v1.2.0.tar.gz

# 其他操作
./deploy.sh restart
./deploy.sh stop
./deploy.sh logs
./deploy.sh status
```

**Windows (PowerShell)**
```powershell
# 首次部署 / 版本升级
.\deploy.ps1 -Action up -Tag v1.2.0 -Bundle C:\path\to\tourmind-v1.2.0.tar.gz

# 其他操作
.\deploy.ps1 -Action restart
.\deploy.ps1 -Action stop
.\deploy.ps1 -Action logs
.\deploy.ps1 -Action status
```

---

## 版本号策略

脚本使用 `git describe` 自动生成版本号：

| 场景 | 生成版本 |
|------|---------|
| 当前提交有 tag，工作区干净 | `v1.0.0` |
| tag 后有 3 次提交 | `v1.0.0-3-gabcdef` |
| 有未提交改动 | `v1.0.0-3-gabcdef+dirty` |
| 仓库没有任何 tag | `20260416.1430`（时间戳兜底） |

**推荐发布流程：**
```bash
git tag v1.0.0
./build.sh        # → 产出 tourmind-v1.0.0.tar.gz
```

> `+dirty` 后缀提示工作区有未提交改动，建议先 `git commit` 再构建正式包。

---

## 发布包说明

- 两个镜像（`tourmind/backend` + `tourmind/nginx`）被合并打包进同一个 `.tar.gz`
- 部署时执行 `docker load` 直接从包中恢复镜像，**无需网络、无需 Registry**
- `devops/dist/` 已加入 `.gitignore`，发布包不会提交到仓库

---

## 环境变量说明

参见 [.env.example](.env.example)，关键配置项：

| 变量 | 说明 |
|------|------|
| `POSTGRES_USER` | 数据库用户名 |
| `POSTGRES_PASSWORD` | 数据库密码（生产环境请使用强密码）|
| `POSTGRES_DB` | 数据库名 |
| `SECRET_KEY` | JWT 签名密钥（生产环境随机生成）|
| `DEBUG` | `false`（生产）/ `true`（开发）|
