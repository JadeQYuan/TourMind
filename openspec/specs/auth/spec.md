## Purpose
用户认证与权限管理：密码修改、右上角用户信息展示、角色权限控制。

## Requirements

### Requirement: 用户可在右上角自助修改密码
在系统布局右上角用户信息区，系统 SHALL 提供"修改密码"入口；用户点击后 SHALL 弹出包含当前密码、新密码、确认新密码三个字段的 Modal；提交前系统 SHALL 校验新密码长度 ≥ 8 且包含大写字母、小写字母、数字；提交成功后 SHALL 显示成功提示，然后执行登出并跳转至登录页。

#### Scenario: 用户成功修改密码
- **WHEN** 用户填写正确的当前密码和符合强度要求的新密码，点击"确认修改"
- **THEN** 调用 `authApi.changePassword`，成功后显示"密码修改成功，请重新登录"，约 1.5s 后执行 `auth.logout()` 并跳转 `/login`

#### Scenario: 当前密码错误
- **WHEN** 用户填写错误的当前密码，点击"确认修改"
- **THEN** 后端返回 400，前端通过 `message.error` 提示"当前密码错误"，Modal 保持打开

#### Scenario: 新密码不符合强度要求
- **WHEN** 新密码少于 8 位，或不包含大写字母，或不包含小写字母，或不包含数字
- **THEN** 前端在提交前用 `message.error` 提示具体原因，不发送请求

#### Scenario: 两次密码不一致
- **WHEN** 新密码与确认新密码不一致
- **THEN** 前端用 `message.error('两次密码不一致')` 提示，不发送请求

#### Scenario: 关闭 Modal 后表单清空
- **WHEN** 用户关闭修改密码 Modal
- **THEN** 三个密码字段均被清空，下次打开时为初始状态

### Requirement: 右上角用户信息正确显示姓名及样式
右上角触发区 SHALL 显示用户头像（首字）与姓名（`full_name`）；头像背景色 SHALL 与角色对应（system_admin 红色、admin 绿色、assistant 蓝色）；悬浮卡 SHALL 显示完整 `full_name`，不得引用 `user.name`。

#### Scenario: 头像显示首字及对应颜色
- **WHEN** 任意角色用户登录后查看右上角
- **THEN** 头像显示 `full_name` 的第一个字，背景色按角色对应颜色显示

#### Scenario: 悬浮卡显示正确姓名
- **WHEN** 用户 hover 右上角触发区
- **THEN** 悬浮卡姓名区域显示 `auth.user.full_name`，非空白

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
