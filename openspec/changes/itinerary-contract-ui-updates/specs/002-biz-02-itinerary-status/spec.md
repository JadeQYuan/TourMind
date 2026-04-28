## REMOVED Requirements

### Requirement: Completed itinerary can be reverted to in-progress
**Reason**: 业务决策取消"撤销完成"回退功能，改为在未开始阶段直接撤销行程。
**Migration**: 移除前端 `completed` 状态行程操作区的"撤销完成"按钮及其处理逻辑；移除后端 `VALID_TRANSITIONS` 中 `completed → in_progress` 条目。

## ADDED Requirements

### Requirement: Not-started itinerary can be cancelled
前端 SHALL 在 `not_started`（未开始）状态行程的操作区显示"撤销"按钮；点击后弹出确认对话框，用户确认后将行程状态变更为 `cancelled`（已撤销）；后端 `VALID_TRANSITIONS` SHALL 包含 `not_started → cancelled` 的流转路径。

#### Scenario: 撤销按钮仅对未开始行程显示
- **WHEN** 用户查看行程列表，某行程状态为"未开始"
- **THEN** 该行程的操作栏显示"撤销"按钮

#### Scenario: 其他状态不显示撤销按钮
- **WHEN** 用户查看行程列表，某行程状态为"行程中"、"已完成"或"已撤销"
- **THEN** 该行程的操作栏不显示"撤销"按钮

#### Scenario: 点击撤销弹出确认对话框
- **WHEN** 用户点击"未开始"行程的"撤销"按钮
- **THEN** 系统弹出确认对话框，说明操作将把行程状态变为"已撤销"，用户确认后才执行

#### Scenario: 确认后行程状态变为 cancelled
- **WHEN** 用户在确认对话框中点击"确认"
- **THEN** 行程状态变为"已撤销"，列表刷新，该行程操作栏不再显示"撤销"按钮

#### Scenario: Backend accepts not_started to cancelled transition
- **WHEN** 前端调用 `PATCH /itineraries/{id}/status` 传入 `{ status: "cancelled" }`，行程当前状态为 `not_started`
- **THEN** 后端接受请求，将状态更新为 `cancelled` 并返回成功
