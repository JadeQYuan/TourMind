## Purpose
合同状态工作流：三状态枚举（pending_sign/signed/revoked）、创建即进入待签署、复制签署链接、中文标签，以及列表和详情状态标签全量更新。

## Requirements

### Requirement: 合同状态枚举精简为三个
后端 `ContractStatus` enum SHALL 只包含三个值：`pending_sign`（待签署）、`signed`（已签署）、`revoked`（已撤销）。`in_progress`、`completed` 从 enum 移除；`cancelled` 重命名为 `revoked`。

#### Scenario: 创建合同状态为 pending_sign
- **WHEN** `POST /contracts` 被调用
- **THEN** 响应中 `status` 字段值为 `"pending_sign"`

#### Scenario: 签署合同状态转为 signed
- **WHEN** 合同签署动作触发
- **THEN** `status` 变为 `"signed"`

#### Scenario: 撤销合同状态为 revoked
- **WHEN** 合同被主动撤销
- **THEN** `status` 变为 `"revoked"`

#### Scenario: 使用旧状态值时 API 拒绝
- **WHEN** 客户端请求 status 为 `"cancelled"`、`"in_progress"` 或 `"completed"`
- **THEN** API 返回 422 校验错误

### Requirement: 合同创建即进入待签署状态
创建合同时，系统 SHALL 将合同状态直接设置为 `pending_sign`（待签署），并同步生成唯一的签署 token（`share_token`）。

#### Scenario: 创建合同后状态为待签署
- **WHEN** 用户提交创建合同表单
- **THEN** 新合同的 `status` 为 `pending_sign`，且 `share_token` 已生成（非空）

#### Scenario: 签署链接创建后即可复制
- **WHEN** 合同列表中 `pending_sign` 合同的"复制链接"按钮被点击
- **THEN** 系统将 `{origin}/sign/{share_token}` 写入剪贴板，提示"签署链接已复制"

### Requirement: 合同列表操作统一为"复制链接"
对于 `pending_sign` 状态的合同，列表页 SHALL 仅显示"复制链接"按钮。`revoked` 和 `signed` 状态无签署操作。

#### Scenario: 待签署合同仅显示"复制链接"
- **WHEN** 合同列表中包含一条 `pending_sign` 合同
- **THEN** 操作列显示"查看"和"复制链接"两个按钮

#### Scenario: 已签署或已撤销合同无签署操作
- **WHEN** 合同状态为 `signed` 或 `revoked`
- **THEN** 操作列不显示"复制链接"按钮

### Requirement: 状态标签全中文显示
所有合同视图中展示状态时，系统 SHALL 显示中文标签。`ContractListView` 的 `STATUS_LABEL` 和 `STATUS_COLOR` SHALL 只包含 3 个状态的映射：`pending_sign`、`signed`、`revoked`。

| 状态 key      | 中文标签 | 颜色 token |
|--------------|---------|-----------|
| pending_sign | 待签署   | orange    |
| signed       | 已签署   | success   |
| revoked      | 已撤销   | error     |

#### Scenario: 列表页状态标签为中文
- **WHEN** 合同列表渲染每行的状态列
- **THEN** 显示对应中文标签，不显示英文 key

#### Scenario: 筛选器选项为中文（3个）
- **WHEN** 用户在列表页打开状态筛选下拉
- **THEN** 选项仅包含「待签署」「已签署」「已撤销」3 个选项，不出现「进行中」「已完成」「已取消」

#### Scenario: 已撤销合同在列表显示中文状态
- **WHEN** 列表包含 `status = "revoked"` 的合同
- **THEN** 该行状态标签显示「已撤销」且标签颜色为 error（红色）

### Requirement: 后端状态跃迁只包含合法状态
后端 `CONTRACT_TRANSITIONS` SHALL 不包含 `draft`、`in_progress`、`completed`、`cancelled` 条目。

#### Scenario: 使用非法状态作为目标时 API 返回错误
- **WHEN** 客户端发起状态更新请求，目标 status 为 `"cancelled"` 或其他已删除状态
- **THEN** API 返回 422 校验错误

### Requirement: 合同详情页编辑按钮无死代码条件
`ContractDetailView` 的编辑按钮 SHALL 不包含 `status !== 'draft'` 的条件判断。

#### Scenario: 编辑按钮对所有状态可见
- **WHEN** 用户打开任意状态的合同详情页
- **THEN** 编辑按钮始终显示（权限由后端控制）
