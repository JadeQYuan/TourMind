## Why

当前用户列表和用户新增功能对所有管理员角色的权限区分不够细致，导致管理员可以看到和操作系统管理员账户，存在安全和权限越权风险。需要根据角色严格区分可见范围和可添加用户类型。

## What Changes

- 用户列表：
  - 系统管理员可查看所有用户（包括系统管理员、管理员、助理）。
  - 管理员仅可查看非系统管理员用户（即管理员、助理）。
- 新增用户：
  - 系统管理员可添加所有角色的用户。
  - 管理员仅可添加管理员和助理，不能添加系统管理员。
- **BREAKING**：管理员无法再看到或添加系统管理员。

## Capabilities

### Modified Capabilities
- `user`: 用户管理模块的列表与新增逻辑需根据当前登录用户角色调整

## Impact

- 影响后端：`backend/app/routers/users.py`、权限校验相关依赖
- 影响前端：`frontend/src/views/user/UserListView.vue`、`frontend/src/api/user.ts`
- 影响 API：用户列表查询、新增用户接口
- 影响角色权限体系和部分测试用例
