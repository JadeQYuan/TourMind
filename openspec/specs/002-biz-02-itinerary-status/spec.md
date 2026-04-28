## Purpose
行程状态管理：撤销完成回退到进行中、分享码自动生成与永久保存、分享无需 API 调用。

## Requirements

### Requirement: Completed itinerary can be reverted to in-progress
系统 SHALL 允许将状态为 `completed` 的行程撤销回 `in_progress`；后端 `VALID_TRANSITIONS` SHALL 包含 `completed → in_progress` 的流转路径；前端 SHALL 在 `completed` 状态行程的操作区显示"撤销完成"按钮，点击后弹出确认对话框。

#### Scenario: Revert button visible for completed itinerary
- **WHEN** 用户查看行程列表，某行程状态为"已完成"
- **THEN** 该行程的操作栏显示"撤销完成"按钮

#### Scenario: Confirm dialog before revert
- **WHEN** 用户点击"撤销完成"按钮
- **THEN** 系统弹出确认对话框，说明操作将把行程状态改回"进行中"，用户确认后才执行

#### Scenario: Status changes to in_progress after revert confirmed
- **WHEN** 用户在确认对话框中点击"确认"
- **THEN** 行程状态变为"进行中"，列表刷新，操作栏恢复显示"标记完成"按钮

#### Scenario: Backend accepts completed to in_progress transition
- **WHEN** 前端调用 `PATCH /itineraries/{id}/status` 传入 `{ status: "in_progress" }`，行程当前状态为 `completed`
- **THEN** 后端接受请求，将状态更新为 `in_progress` 并返回成功

### Requirement: Share code is auto-generated at record creation
行程和合同在新建时 SHALL 自动生成唯一的 `share_token`（非 null），无需用户手动触发分享操作。

#### Scenario: New itinerary has share token
- **WHEN** 用户新建一条行程
- **THEN** 返回的行程数据中 `share_token` 为非空字符串

#### Scenario: Copied itinerary gets new share token
- **WHEN** 用户对一条行程执行复制操作
- **THEN** 副本的 `share_token` 是一个新的唯一值，与原记录不同

### Requirement: Itinerary share does not require API call
用户点击行程"分享"按钮 SHALL 直接复制分享链接，不调用任何后端接口。

#### Scenario: Share itinerary
- **WHEN** 用户点击行程列表的"分享"按钮
- **THEN** 分享链接立即被写入剪贴板，提示"分享链接已复制"
- **AND** 无网络请求发出

#### Scenario: Clipboard not available
- **WHEN** 用户点击分享但剪贴板 API 不可用
- **THEN** 弹出 Modal 展示分享链接，供用户手动复制

### Requirement: Share token is permanent after creation
`share_token` 在记录创建后 SHALL 不被清除，合同签署完成或撤销只变更 status，不改变 `share_token`。

#### Scenario: Share token persists after contract signing
- **WHEN** 客户完成合同签署
- **THEN** 合同的 `share_token` 保持不变（只有 status 变为 `signed`）

#### Scenario: Share token persists after revoke
- **WHEN** 用户点击"撤销"签署
- **THEN** 合同的 `share_token` 保持不变（只有 status 回到上一状态）
