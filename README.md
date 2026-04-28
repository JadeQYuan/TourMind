# 智游管家 · TourMind

面向中小型旅行社的轻量化一体化旅游业务管理平台，以**下单 → 出行程 → 付款**三步主线贯通业务，产品/供应商/账户一次配置即可复用。

---

## 功能模块

| 模块 | 说明 |
|------|------|
| 产品管理 | 维护可销售的标准旅游产品，含行程模板、报价基准 |
| 行程管理 | 创建出行行程，关联产品自动填入路线；管理每日明细与供应商订单 |
| 合同管理 | 从行程生成合同，客户手机号验证后在线电子签署 |
| 账单管理 | 记录收支流水，实时查看每笔行程的盈亏情况 |
| 供应商管理 | 维护合作的交通、住宿、景区等供应商信息 |
| 账户管理 | 管理银行卡、微信、支付宝等收款账户 |
| 用户管理 | 多角色权限控制（管理员 / 销售 / 财务 / 只读） |

---

## 技术栈

**后端**
- Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL 16 · Alembic

**前端**
- Vue 3 · TypeScript · Vite · Ant Design Vue 4.x · Pinia · Vue Router 4

**部署**
- Docker · Docker Compose · Nginx

---

## 项目结构

```
TourMind/
├── backend/            # FastAPI 后端服务
│   ├── app/
│   │   ├── core/       # 配置、数据库、依赖注入
│   │   ├── models/     # SQLAlchemy 模型
│   │   ├── schemas/    # Pydantic 请求/响应结构
│   │   └── routers/    # API 路由
│   └── alembic/        # 数据库迁移
├── frontend/           # Vue 3 前端应用
│   ├── src/
│   │   ├── views/      # 页面组件
│   │   ├── api/        # 后端接口封装
│   │   ├── stores/     # Pinia 状态管理
│   │   └── types/      # TypeScript 类型定义
│   └── mock/           # vite-plugin-mock 接口模拟
├── mock/               # 共享 Mock 数据
├── devops/             # 构建与部署配置
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── dist/           # 构建产物（git ignored）
│   └── scripts/
│       ├── build.sh / build.ps1
│       └── deploy.sh / deploy.ps1
└── docs/               # 产品与技术文档
```

---

## 本地开发

### 前置要求

- Node.js 20+
- Python 3.12+
- PostgreSQL 16（或使用 Docker 启动）

### 启动后端

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 复制并配置环境变量
cp devops/.env.example .env
# 编辑 .env，填写本地数据库连接

# 执行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

### 启动前端

```bash
cd frontend
npm install
npm run dev   # → http://localhost:5173
```

前端开发模式使用 `vite-plugin-mock` 模拟接口，无需后端即可运行。

默认账号：`admin` / `admin123`

---

## 构建与部署

详见 [devops/README.md](devops/README.md)，简要流程：

```bash
# 1. 配置环境变量
cp devops/.env.example .env

# 2. 构建发布包（自动从 git tag 生成版本号）
cd devops/scripts
./build.sh           # Linux / macOS
.\build.ps1          # Windows PowerShell

# 3. 将发布包传至服务器后部署
./deploy.sh up v1.0.0 /path/to/tourmind-v1.0.0.tar.gz
```

---

## 文档

| 文件 | 说明 |
|------|------|
| [docs/产品需求文档(PRD).md](docs/产品需求文档(PRD).md) | 功能需求与业务流程 |
| [docs/技术选型方案.md](docs/技术选型方案.md) | 技术栈选型依据 |
| [docs/系统架构设计.md](docs/系统架构设计.md) | 系统架构与模块设计 |
| [docs/数据库设计.md](docs/数据库设计.md) | 数据库表结构设计 |
| [devops/README.md](devops/README.md) | 构建与部署操作手册 |
