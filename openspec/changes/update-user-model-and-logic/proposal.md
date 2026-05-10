## Why

当前用户模型与规范不一致，存在字段命名差异和额外的逻辑，需要对齐到规范同时保留现有功能。规范使用 `status` 字段而不是 `is_active`，并且没有 `must_change_password` 相关要求。

## What Changes

- **模型字段变更**：
  - 保留现有角色体系：`system_admin` / `admin` / `assistant`
  - 将 `is_active` (bool) 替换为 `status` (string)，枚举值为 `enabled` / `disabled`
  - 将 `last_login_at` 重命名为 `last_login`
  - 删除 `must_change_password` 字段
  - 新增 `remark` 字段（可选，最长 128 字符）
- **Schema 更新**：同步更新所有用户相关的 Pydantic Schema
- **路由逻辑调整**：
  - 移除所有与 `must_change_password` 相关的逻辑
  - 更新状态变更逻辑以使用 `status` 字段
  - 新增单个用户详情 GET 端点
  - 调整用户列表查询参数从 `is_active` 到 `status`
- **认证逻辑调整**：移除 `must_change_password` 相关逻辑

## Capabilities

- `user`: 更新用户模型和业务逻辑以符合规范

## Impact

- backend/app/models/user.py - 字段重命名、删除、新增
- backend/app/schemas/user.py - Schema 更新
- backend/app/schemas/auth.py - 认证相关 Schema 更新
- backend/app/routers/users.py - 用户管理路由逻辑更新
- backend/app/routers/auth.py - 认证路由逻辑更新
- backend/app/core/deps.py - 检查是否有 must_change_password 依赖
- backend/alembic/versions/ - 新增迁移脚本
- 影响用户管理和认证模块
