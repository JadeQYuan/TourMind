## Purpose
全局规范：移动端布局、列表页交互、Drawer/表单/表格通用 UI 约定，以及 Mock 开发规范。

## Requirements

### Requirement: Mobile sidebar collapses to hamburger menu
在移动端（视口宽度 < 768px），系统 SHALL 隐藏内联侧边栏，转而在顶栏显示汉堡菜单按钮，点击后以 Drawer 形式展开导航菜单。

#### Scenario: Sidebar hidden on mobile
- **WHEN** 用户在移动端（< 768px）访问任意页面
- **THEN** 左侧固定侧边栏不可见，顶栏显示汉堡菜单图标

#### Scenario: Hamburger opens drawer menu
- **WHEN** 用户在移动端点击汉堡菜单图标
- **THEN** 从左侧滑出包含全部导航项的 Drawer，与桌面端菜单结构相同

#### Scenario: Navigation item closes drawer
- **WHEN** 用户在移动端 Drawer 菜单中点击某一导航项
- **THEN** Drawer 自动关闭，页面跳转至对应路由

### Requirement: Unified isMobile composable
系统 SHALL 提供 `useBreakpoint` composable（位于 `src/composables/useBreakpoint.ts`），导出 `isMobile`（响应式布尔值，`true` 表示视口 < 768px）供所有视图使用。

#### Scenario: isMobile reflects viewport width
- **WHEN** 视口宽度缩小至 767px
- **THEN** `isMobile` 返回 `true`

#### Scenario: isMobile updates on resize
- **WHEN** 用户调整浏览器窗口至 768px 及以上
- **THEN** `isMobile` 响应式更新为 `false`

#### Scenario: No duplicate resize listeners in list views
- **WHEN** 任意 ListView 使用 `isMobile`
- **THEN** 该视图不再自行注册 `window.addEventListener('resize', ...)`

### Requirement: List pages render as cards on mobile
所有列表页（Order、Product、Itinerary、Contract、Supplier、Bill、Account、User、AuditLog）在移动端 SHALL 以 `<a-card>` 卡片列表方式渲染数据，替代 `<a-table>` 表格。

#### Scenario: Table hidden on mobile
- **WHEN** 用户在移动端（`isMobile = true`）访问任意列表页
- **THEN** `<a-table>` 组件不渲染，显示卡片列表

#### Scenario: Table shown on desktop
- **WHEN** 用户在桌面端（`isMobile = false`）访问列表页
- **THEN** 显示原有 `<a-table>` 表格，卡片列表不渲染

### Requirement: Mobile card displays key fields per business entity
每类列表页的移动端卡片 SHALL 展示以下字段：

- **订单（Order）**：订单编号、客户名称、产品名、出发日期、状态、操作（编辑/删除）
- **产品（Product）**：产品名称、天数、价格、状态、操作（编辑/删除）
- **行程（Itinerary）**：标题、出发日期、天数、状态、操作（查看/编辑）
- **合同（Contract）**：合同编号、客户名称、签署日期、状态、操作（查看/下载）
- **供应商（Supplier）**：供应商名称、联系人、联系电话、状态
- **账单（Bill）**：账单编号、关联订单、金额、状态、操作（查看）
- **账户（Account）**：账户名、类型、余额、操作
- **用户（User）**：用户名、角色、状态、操作（编辑）
- **审计日志（AuditLog）**：操作时间、操作人、操作类型、对象

#### Scenario: Card action buttons are accessible
- **WHEN** 用户在移动端查看列表卡片
- **THEN** 操作按钮使用图标按钮展示，排布在卡片底部或右上角，可单手操作

### Requirement: Pagination works in card view
移动端卡片列表 SHALL 与桌面端共用同一分页组件，分页状态保持同步。

#### Scenario: Pagination below card list
- **WHEN** 用户在移动端滚动至卡片列表底部
- **THEN** 显示与桌面端一致的 `<a-pagination>` 分页控件

### Requirement: Mobile filter conditions in drawer
含查询条件的列表页在移动端 SHALL 隐藏内联筛选表单，更换为顶部"筛选"按钮，点击后打开底部 Drawer（`placement="bottom"`，高度约 60vh）。

#### Scenario: Inline filter form hidden on mobile
- **WHEN** 用户在移动端访问含筛选条件的列表页
- **THEN** 桌面端的筛选表单不渲染，页面顶部显示"筛选"按钮

#### Scenario: Filter drawer requires confirmation to apply
- **WHEN** 用户在移动端筛选 Drawer 中修改任意筛选字段
- **THEN** 列表数据不立即变化，等待用户点击"确认"按钮

#### Scenario: Active filter count badge on filter button
- **WHEN** 用户已应用至少一个非默认筛选条件
- **THEN** "筛选"按钮上显示对应数字徽标


### Requirement: Form drawer is recommended for create/edit
所有新建/编辑表单（包括合同、订单、行程等）**建议优先采用 Drawer（抽屉）模式**，以保持与全局 UI 交互一致性。桌面端推荐右侧宽 480px，移动端全屏（`isMobile ? '100%' : 480`）。如需特殊页面跳转或弹窗实现，须在模块规范中单独说明。

#### Scenario: Edit uses drawer by default
- **WHEN** 用户点击“编辑”按钮
- **THEN** 默认以 Drawer 形式打开编辑表单，宽度与新建/查看一致

#### Scenario: Drawer width matches view
- **WHEN** 用户在桌面端或移动端打开新建/编辑 Drawer
- **THEN** Drawer 宽度与查看抽屉一致，移动端全屏

### Requirement: Form fields render as single column on mobile
含多列网格布局的新建/编辑表单在移动端 SHALL 将所有 `<a-col>` 字段的 span 设置为 24（全宽单列）。

#### Scenario: Form single column on mobile
- **WHEN** 用户在移动端打开产品、订单或行程的新建/编辑 Drawer
- **THEN** 表单中所有字段以全宽单列显示

#### Scenario: Desktop form layout unchanged
- **WHEN** 用户在桌面端打开上述任意表单
- **THEN** 表单字段保持原有多列布局

### Requirement: Auto-trigger query on filter change
所有列表页的筛选字段值发生变化时，系统 SHALL 在**桌面端**自动触发查询并重置到第一页，无需用户点击"查询"按钮。移动端筛选由筛选 Drawer 的确认机制控制，不自动触发。

#### Scenario: Select filter triggers query automatically on desktop
- **WHEN** 用户在桌面端任意列表页更改下拉筛选
- **THEN** 系统自动重置分页到第一页并重新请求数据

#### Scenario: Text input triggers query on blur or enter on desktop
- **WHEN** 用户在桌面端关键词输入框中输入内容后按回车或失焦
- **THEN** 系统自动重置分页到第一页并重新请求数据

#### Scenario: Mobile filter changes do not auto-trigger query
- **WHEN** 用户在移动端筛选 Drawer 中修改任意筛选字段
- **THEN** 列表数据不立即变化，等待用户在 Drawer 内点击"确认"按钮

### Requirement: Unified reset button on list pages
所有列表页 SHALL 在筛选栏中提供"重置"按钮，点击后将所有筛选字段恢复到默认值并重新查询。

#### Scenario: Reset clears filters and re-queries
- **WHEN** 用户点击"重置"按钮
- **THEN** 关键词/日期等非状态字段清空，状态字段恢复默认值，分页回到第一页，并自动重新请求数据

### Requirement: Default active status filter
具有状态筛选的列表页，系统 SHALL 在页面初始加载时默认选中"有效"或"上架"状态。

#### Scenario: Product list defaults to on-sale status
- **WHEN** 用户进入产品列表页
- **THEN** 状态筛选默认显示"上架"，列表只显示 `status = 'active'` 的产品

#### Scenario: User/Account/Supplier lists default to active
- **WHEN** 用户进入用户、账户或供应商列表页
- **THEN** 状态筛选默认显示"有效/启用"，列表只显示 `is_active = true` 的记录

### Requirement: List pages support inline view drawer
每个业务列表页 SHALL 在每行/每张卡片上提供"查看"按钮，点击后在页面右侧以 Drawer 形式展示该记录的只读详情，宽度 480px，不跳转页面。

#### Scenario: View button opens drawer
- **WHEN** 用户在列表中点击某行的"查看"按钮
- **THEN** 页面右侧打开宽 480px 的 Drawer，展示加载中状态，随后显示该记录的详情字段

#### Scenario: Load failure closes drawer with error
- **WHEN** 查看抽屉发起 API 请求但请求失败
- **THEN** 系统显示错误提示（`message.error`），抽屉自动关闭

### Requirement: View drawer width matches edit drawer per module
每个列表视图的查看抽屉 SHALL 使用与该视图新建/编辑抽屉完全相同的 `:width` 表达式，且 SHALL 支持移动端全屏（`isMobile ? '100%' : <width>`）。

#### Scenario: Mobile view drawer is full screen
- **WHEN** 用户在移动端点击任意列表视图的"查看"按钮
- **THEN** 查看抽屉宽度为 `100%`，铺满屏幕

#### Scenario: Desktop view drawer matches edit drawer width
- **WHEN** 桌面端用户打开任意列表视图查看抽屉
- **THEN** 抽屉宽度与对应模块的编辑/新建抽屉一致

### Requirement: Form drawer footer is sticky
所有列表视图新建/编辑 Drawer 的操作按钮（取消/保存）SHALL 使用 `<template #footer>` 插槽固定在抽屉底部，不随内容滚动。

#### Scenario: Form drawer buttons fixed at bottom
- **WHEN** 用户在任意 Drawer 表单中查看内容超过视口高度时
- **THEN** 取消/保存按钮始终固定在 Drawer 底部，不随内容滚动

#### Scenario: Standalone route page buttons unaffected
- **WHEN** 用户通过独立路由访问表单页面
- **THEN** 按钮正常显示在表单内容底部，行为由 `showFooter` prop 控制

### Requirement: Table supports horizontal scroll when content overflows
所有列表视图的桌面端 `<a-table>` SHALL 设置 `:scroll="{ x: N }"`，其中 N 为所有列 width 之和，使表格可横向滚动而非内容被压缩。

#### Scenario: Table scrolls horizontally on narrow viewport
- **WHEN** 用户在桌面端打开任意列表页且浏览器窗口宽度小于表格的 scrollX 值
- **THEN** 表格下方出现横向滚动条，列内容保持原有宽度不被压缩

### Requirement: Action column is always visible during horizontal scroll
含操作列（`key: 'action'`）的列表视图 SHALL 为该列设置 `fixed: 'right'`。

#### Scenario: Action column stays fixed during horizontal scroll
- **WHEN** 用户在桌面端横向滚动一个宽表格
- **THEN** 「操作」列始终显示在表格最右侧，不随滚动消失

### Requirement: All columns have explicit width when scroll is enabled
所有启用了 `:scroll="{ x: N }"` 的表格，其 columns 定义中每列 SHALL 有显式的 `width` 值（整数，单位 px）。

#### Scenario: All columns have width defined
- **WHEN** 开启了横向滚动的表格渲染
- **THEN** 所有列均有明确的 width 值，不留空

### Requirement: Mock response functions have defensive param checks
所有 `mock/` 目录下的 response 函数，在使用 `params.id` 或 `params.token` 之前，SHALL 先检查 `params` 及对应字段是否存在；若不存在，SHALL 立即返回结构化错误响应 `{ code: 400, message: '参数错误' }`，不得抛出未捕获的异常。

#### Scenario: params undefined returns 400
- **WHEN** vite-plugin-mock 调用 response 函数时 `params` 为 `undefined`
- **THEN** 函数返回 `{ code: 400, message: '参数错误' }`，不抛出 TypeError

#### Scenario: params.id missing returns 400
- **WHEN** `params` 是空对象 `{}` 或不含 `id` 字段
- **THEN** 函数返回 `{ code: 400, message: '参数错误' }`，不执行后续查找逻辑

#### Scenario: Valid params execute normally
- **WHEN** `params.id` 或 `params.token` 有有效值
- **THEN** 函数按原有逻辑执行，返回正确数据或 404

### Requirement: Supplier and Account API have get method
`supplierApi` 和 `accountApi` SHALL 各自提供 `get(id: number)` 方法，从后端获取单条记录详情。

#### Scenario: supplierApi.get fetches single supplier
- **WHEN** 代码调用 `supplierApi.get(id)`
- **THEN** 发起 `GET /suppliers/:id` 请求，返回单条 `Supplier` 数据

#### Scenario: accountApi.get fetches single account
- **WHEN** 代码调用 `accountApi.get(id)`
- **THEN** 发起 `GET /accounts/:id` 请求，返回单条 `Account` 数据
