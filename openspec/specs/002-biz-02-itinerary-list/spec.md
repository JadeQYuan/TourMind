## Purpose
行程列表操作区：查看抽屉、编辑表单加载、双列布局、公开分享页、分享按钮可见性、标记完成时间限制、撤销时间限制，以及无撤销分享按钮。

## Requirements

### Requirement: Itinerary list view uses drawer
列表操作栏的"查看"按钮 SHALL 打开一个右侧抽屉（Drawer）展示行程详情，而非跳转至独立页面；抽屉内容 SHALL 包含基本信息（客户、日期、目的地、出行人员等）和每日行程明细，SHALL NOT 包含服务安排区块；抽屉以只读模式展示，不提供编辑操作。

#### Scenario: View button opens drawer
- **WHEN** 用户在行程列表点击某行的"查看"按钮
- **THEN** 页面右侧滑出抽屉，展示该行程的基本信息和每日行程明细，页面不跳转

#### Scenario: Drawer does not show service orders
- **WHEN** 抽屉展示行程详情
- **THEN** 抽屉内容中不包含"服务安排"区块（供应商订单列表）

#### Scenario: Drawer close returns to list
- **WHEN** 用户点击抽屉的关闭按钮或点击遮罩
- **THEN** 抽屉关闭，用户仍在行程列表页，列表状态不重置

### Requirement: No detail button in itinerary list actions
行程列表的操作栏 SHALL NOT 包含直接跳转至独立详情页的"详情"按钮；用户 SHALL 通过"查看"按钮打开抽屉查看行程内容。

#### Scenario: Detail button absent from action column
- **WHEN** 用户查看行程列表
- **THEN** 每行操作栏中不显示会跳转到 `/itineraries/:id` 页面的按钮

### Requirement: No revoke-share button in itinerary list
行程列表的操作区域 SHALL NOT 包含"撤销"分享链接按钮，无论桌面还是移动端。

#### Scenario: 桌面端行程列表无撤销按钮
- **WHEN** 用户查看桌面端行程列表，且某行程已有分享链接
- **THEN** 操作区域 SHALL 只显示"编辑"和"分享"按钮，不显示"撤销"按钮

#### Scenario: 移动端行程卡片无撤销按钮
- **WHEN** 用户查看移动端行程列表，且某行程已有分享链接
- **THEN** 卡片操作区 SHALL 只显示"编辑"和"分享"按钮，不显示"撤销"按钮

### Requirement: Edit form loads data correctly in drawer
行程编辑抽屉打开时，系统 SHALL 正确加载并显示目标行程的所有字段数据；无论组件是首次挂载还是 prop 变化触发，数据加载逻辑 SHALL 保持一致。

#### Scenario: Edit drawer shows populated form
- **WHEN** 用户点击某行程的"编辑"按钮，抽屉打开
- **THEN** 关联订单、目的地、日期、人数等字段均显示该行程的已有数据，表单不为空

#### Scenario: Create drawer shows empty form
- **WHEN** 用户点击"新建行程"，抽屉打开
- **THEN** 表单所有字段为空/默认值

### Requirement: Itinerary form uses 2-column layout
行程表单 SHALL 在关键字段区域采用双列布局（在 780px 宽度抽屉内清晰展示）：目的地与出行人数在同一行，出发日期与结束日期在同一行。

#### Scenario: Date and pax fields in two columns
- **WHEN** 用户查看新建或编辑行程表单
- **THEN** 出发日期和结束日期各占半宽显示在同一行；目的地和出行人数各占半宽显示在同一行

### Requirement: Public share page is a separate view
行程公开分享链接（`/public/itinerary/:token`）SHALL 使用独立的 `ItineraryShareView.vue` 组件，与内部查看抽屉完全分离；分享页 SHALL 展示行程基本信息和每日行程明细，SHALL NOT 包含服务安排；分享页 SHALL NOT 显示任何需要登录才能执行的操作按钮。

#### Scenario: Share link loads itinerary via token
- **WHEN** 用户（含未登录）访问 `/public/itinerary/{token}`
- **THEN** 页面使用 token 调用公开 API 加载行程内容并显示，不要求登录

#### Scenario: Share page has no service orders section
- **WHEN** 行程分享页内容加载完成
- **THEN** 页面不显示服务安排（供应商订单）区块

#### Scenario: Share page has no authenticated action buttons
- **WHEN** 任意用户访问行程分享页
- **THEN** 页面不显示"开始执行"、"标记完成"、"编辑"、"撤销完成"等操作按钮

### Requirement: Share button available only for active statuses
行程操作区（列表页操作栏及详情页操作区）的"分享"按钮 SHALL 仅对 `not_started` 和 `in_progress` 状态的行程可见；`completed` 和 `cancelled` 状态的行程 SHALL NOT 显示"分享"按钮。

#### Scenario: Share button hidden for completed itinerary
- **WHEN** 用户查看行程列表，某行程状态为"已完成"
- **THEN** 该行程操作栏不显示"分享"按钮

#### Scenario: Share button hidden for cancelled itinerary
- **WHEN** 用户查看行程列表，某行程状态为"已撤销"
- **THEN** 该行程操作栏不显示"分享"按钮

#### Scenario: Share button visible for not_started itinerary
- **WHEN** 用户查看行程列表，某行程状态为"未开始"
- **THEN** 该行程操作栏显示"分享"按钮，点击后正常生成/复制分享链接

#### Scenario: Share button visible for in-progress itinerary
- **WHEN** 用户查看行程列表，某行程状态为"行程中"
- **THEN** 该行程操作栏显示"分享"按钮

### Requirement: Complete action available only after trip ends
行程操作区的"标记完成"按钮 SHALL 仅在同时满足以下两个条件时显示：（1）行程状态为 `in_progress`；（2）当天日期严格晚于行程结束日期（`end_date`）。不满足任一条件时按钮 SHALL NOT 显示。点击后直接将状态变更为 `completed`，列表刷新，不跳转页面，无需额外警告提示。

#### Scenario: Mark complete button hidden when trip not yet ended
- **WHEN** 用户查看行程列表，某行程状态为"行程中"且当天日期 ≤ `end_date`
- **THEN** 操作栏 SHALL NOT 显示"标记完成"按钮

#### Scenario: Mark complete button visible when trip has ended
- **WHEN** 用户查看行程列表，某行程状态为"行程中"且当天日期严格晚于 `end_date`
- **THEN** 操作栏显示"标记完成"按钮

#### Scenario: Mark complete updates status in place
- **WHEN** 用户点击"标记完成"按钮
- **THEN** 行程状态变为"已完成"，列表刷新，不跳转页面

### Requirement: Cancel action time-restricted
行程操作区的"撤销行程"按钮 SHALL 仅在同时满足以下两个条件时显示：（1）行程状态为 `not_started` 或 `in_progress`；（2）当天日期早于或等于行程结束日期（`end_date`）。行程已结束（`today > end_date`）时按钮 SHALL NOT 显示。

#### Scenario: Cancel button hidden when trip has already ended
- **WHEN** 用户查看行程列表，某 `not_started` 或 `in_progress` 行程，且当天日期严格晚于 `end_date`
- **THEN** 操作栏 SHALL NOT 显示"撤销行程"按钮

#### Scenario: Cancel button visible when trip has not ended
- **WHEN** 用户查看行程列表，某 `not_started` 或 `in_progress` 行程，且当天日期 ≤ `end_date`
- **THEN** 操作栏显示"撤销行程"按钮
