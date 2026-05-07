## Purpose
用户认证与授权，仅包含登录、登出、Token 校验、权限校验等认证相关内容。

## Requirements


### Requirement: 管理员用户查询不返回系统管理员数据
后端 `GET /users` 接口，当调用方角色为 `admin` 时，SHALL 在查询结果中排除 `role = 'system_admin'` 的用户记录；当调用方角色为 `system_admin` 时，SHALL 返回全量用户列表。

#### Scenario: admin 查询用户列表
- **WHEN** `admin` 角色用户调用 `GET /api/v1/users`
- **THEN** 响应中不包含任何 `role = 'system_admin'` 的记录

#### Scenario: system_admin 查询用户列表
- **WHEN** `system_admin` 角色用户调用 `GET /api/v1/users`
- **THEN** 响应包含全量用户记录，包括其他 `system_admin` 账户

#### Scenario: admin 按角色筛选时不包含 system_admin
- **WHEN** `admin` 调用 `GET /api/v1/users?role=system_admin`
- **THEN** 响应返回空列表

### Requirement: 管理员不得创建系统管理员账户
后端 `POST /users` 接口，当调用方角色为 `admin` 且请求体 `role = 'system_admin'` 时，SHALL 返回 HTTP 403。

#### Scenario: admin 尝试创建 system_admin
- **WHEN** `admin` 角色用户调用 `POST /api/v1/users` 且 `body.role = 'system_admin'`
- **THEN** 接口返回 HTTP 403，detail 为"无权创建系统管理员账户"

#### Scenario: system_admin 创建任意角色用户
- **WHEN** `system_admin` 角色用户调用 `POST /api/v1/users`
- **THEN** 按正常流程创建用户，返回 HTTP 200

### Requirement: 前端角色筛选项对非系统管理员隐藏 system_admin 选项
在用户管理页的角色筛选下拉中，当登录用户角色非 `system_admin` 时，SHALL 不渲染"系统管理员"选项。

#### Scenario: admin 登录时筛选项不含系统管理员
- **WHEN** 角色为 `admin` 的用户进入用户管理页
- **THEN** 角色筛选下拉中不显示"系统管理员"选项

#### Scenario: system_admin 登录时筛选项包含系统管理员
- **WHEN** 角色为 `system_admin` 的用户进入用户管理页
- **THEN** 角色筛选下拉中显示"系统管理员"、"管理员"、"助理"全部选项
