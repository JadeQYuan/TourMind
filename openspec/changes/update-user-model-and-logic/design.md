## Context

当前用户模型与用户规范存在字段和逻辑上的差异：
- 状态字段使用 `is_active` (bool)，规范使用 `status` (string)
- 存在 `must_change_password` 字段和相关逻辑，规范未提及
- 缺少 `remark` 字段
- 字段命名与规范不一致

## Goals / Non-Goals

**Goals:**
- 将 `is_active` 替换为 `status` 字段（string 类型，枚举值 enabled/disabled）
- 保持现有角色体系：system_admin / admin / assistant
- 删除 `must_change_password` 字段及所有相关逻辑
- 添加 `remark` 字段（可选，最长 128 字符）
- 将 `last_login_at` 重命名为 `last_login`
- 更新所有相关的 Schema、路由、认证逻辑
- 添加单个用户详情 GET 端点

**Non-Goals:**
- 不修改角色体系
- 不修改其他用户功能逻辑
- 不涉及前端页面修改（需同步更新）

## Decisions

- **字段映射**：
  - `is_active: True` → `status: "enabled"`
  - `is_active: False` → `status: "disabled"`
- **数据库迁移**：使用 Alembic 处理字段变更
- **查询参数**：将路由中的 `is_active` 查询参数改为 `status`
- **删除内容**：
  - 模型中 `must_change_password` 字段
  - Schema 中相关字段
  - 认证、用户管理路由中的相关逻辑
- **新增内容**：
  - `remark` 字段（可选，String(128)）
  - 单个用户详情 GET 端点 `/users/{user_id}`

## Risks / Trade-offs

- [风险] 前端依赖现有字段和逻辑 → [缓解] 需同步更新前端
- [风险] `must_change_password` 逻辑在生产环境使用 → [缓解] 确认后再删除

## Migration Plan

1. 备份数据库
2. 更新后端用户模型、Schema
3. 更新用户管理和认证路由逻辑
4. 生成 Alembic 迁移脚本
5. 执行迁移脚本
6. 验证功能正常

## Open Questions

- 前端是否依赖 `must_change_password` 逻辑？（需确认）
- 是否需要保留历史数据的 `must_change_password` 状态？
