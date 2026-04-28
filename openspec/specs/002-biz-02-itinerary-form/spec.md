## Purpose
行程表单 UX：关联订单联动目的地自动填充、出行人员字符串字段、从产品模板自动填充每日明细、取消导航、编辑路由加载数据。

## Requirements

### Requirement: Destination auto-filled from linked order's product
选择关联订单时，系统 SHALL 自动将该订单对应产品的 `destination` 字段写入行程表单的目的地字段；若产品无目的地信息，目的地字段保持原值不变。

#### Scenario: Destination filled on order selection
- **WHEN** 用户在行程表单中选择一个关联订单
- **THEN** 目的地字段自动填入该订单对应产品的目的地；若字段原本为空则直接填入，若已有值则覆盖

#### Scenario: Destination unchanged when product has no destination
- **WHEN** 用户选择的关联订单对应产品没有目的地信息
- **THEN** 目的地字段值不变，用户可继续手动填写

### Requirement: Travelers entered as single-line text
出行人员名单 SHALL 使用单个文本输入框（`<a-textarea>`）录入，用户输入的内容以字符串形式直接存储；系统 SHALL NOT 对输入内容做任何解析或转换为对象数组；加载已有行程时 SHALL 直接将 `travelers` 字符串值绑定到输入框，无需格式化处理。

#### Scenario: Single input displays travelers string directly
- **WHEN** 用户打开已有行程的编辑表单
- **THEN** 出行人员区域显示为单个输入框，内容为服务端返回的 `travelers` 字符串（如 `"张三, 李四"`），不做任何数组解析

#### Scenario: Input saved as string without parsing
- **WHEN** 用户在出行人员输入框中输入"张三, 李四 王五"并点击保存
- **THEN** 系统将 `"张三, 李四 王五"` 作为字符串直接提交，不解析为数组

#### Scenario: Empty input results in null travelers
- **WHEN** 用户清空出行人员输入框
- **THEN** 保存时 `travelers` 字段为空字符串或 null

#### Scenario: Backend accepts and returns travelers as string
- **WHEN** 前端提交行程创建或更新请求，`travelers` 字段为字符串
- **THEN** 后端将字符串原样存储至数据库，并在读取时原样返回，无 JSON 序列化/反序列化

#### Scenario: Mock data uses string for travelers
- **WHEN** 前端在开发模式下使用 Mock 数据
- **THEN** Mock 中的行程 `travelers` 字段为字符串类型（如 `"张三, 李四"`），而非对象数组

### Requirement: Remove fill-from-template button
行程表单 SHALL NOT 显示"从产品模板填入"按钮及其说明文字；产品模板填入逻辑仅在切换关联订单时自动触发。

#### Scenario: No fill button visible in form
- **WHEN** 用户查看行程新建或编辑表单
- **THEN** 每日行程明细区域上方不显示"从产品模板填入"按钮

### Requirement: Cancel navigates to itinerary list
在路由页面模式（非组件嵌入）下，点击取消 SHALL 跳转到 `/itineraries`；在组件嵌入模式下，取消 SHALL 继续触发 `cancel` emit。

#### Scenario: Cancel in route page navigates to list
- **WHEN** 用户通过 `/itineraries/create` 或 `/itineraries/:id/edit` 访问行程表单，点击"取消"
- **THEN** 页面导航至 `/itineraries`（行程列表页）

#### Scenario: Cancel in embedded mode emits cancel
- **WHEN** 行程表单以组件嵌入方式使用（`editId` prop 存在），用户点击"取消"
- **THEN** 组件触发 `cancel` emit，不执行路由跳转

### Requirement: 选择订单后自动填充每日明细
新建行程表单中，用户选择关联订单后，系统 SHALL 立即（无需额外操作）检索该订单关联产品的行程模板，并将其内容自动写入每日明细字段，日期依据订单出发日期逐日推算。本行为仅在新建行程模式下生效，编辑模式下 SHALL NOT 触发。

#### Scenario: 有模板订单 — 自动填充成功
- **WHEN** 用户在新建行程表单中选择一个关联了含行程模板产品的订单
- **THEN** 系统立即调用产品详情接口，将模板内容写入每日明细；每条记录的日期从订单出发日期起逐日递增（第N天 = 出发日 + N-1天）

#### Scenario: 编辑模式不触发
- **WHEN** 用户在编辑已有行程的表单中切换关联订单
- **THEN** 系统不自动触发填充，每日明细内容保持不变

#### Scenario: 多次快速切换订单
- **WHEN** 用户在短时间内多次切换订单
- **THEN** 系统以最后一次选择的订单为准触发填充，不产生并发错误或数据错乱

### Requirement: 已有内容时确认覆盖
当用户已在每日明细中输入内容（至少有一条记录的行程详情字段不为空）时，系统 SHALL 在触发自动填充前弹出确认对话框；用户确认后方可执行填充，用户取消则 SHALL 中止填充并将订单选择恢复为原值。

#### Scenario: 弹出确认框
- **WHEN** 用户选择新订单且当前 days_detail 中存在至少一条 details 非空的记录
- **THEN** 系统弹出包含"确认替换"和"取消"选项的确认对话框，不直接覆盖内容

#### Scenario: 用户取消覆盖
- **WHEN** 出现确认对话框后，用户点击"取消"
- **THEN** form.customer_order_id 恢复为切换前的值，days_detail 内容保持不变

#### Scenario: 用户确认覆盖
- **WHEN** 出现确认对话框后，用户点击"确认替换"
- **THEN** 系统执行模板填充，新订单产品模板内容替换 days_detail

### Requirement: 无模板或无产品时友好提示
当所选订单关联的产品不含行程模板（itinerary_template 为空数组或 null）时，系统 SHALL 显示警告提示；当所选订单未关联产品时，系统 SHALL 静默跳过自动填充，不展示错误。

#### Scenario: 产品无行程模板
- **WHEN** 用户选择的订单关联产品的 itinerary_template 为空或 null
- **THEN** 系统显示 warning 提示"产品没有行程模板"，days_detail 保持不变（不清空）

#### Scenario: 订单无关联产品
- **WHEN** 用户选择的订单 product_id 为 null 或 undefined
- **THEN** 系统静默跳过自动填充，不弹出任何提示或错误，days_detail 保持不变

### Requirement: 行程编辑页通过路由访问时加载已有数据
当用户通过路由 `/itineraries/:id/edit` 访问编辑页时，系统 SHALL 自动加载该行程的已有数据并填入表单。

#### Scenario: 路由访问编辑页时表单有数据
- **WHEN** 用户导航到 `/itineraries/123/edit`
- **THEN** 表单 SHALL 显示 ID 为 123 的行程的关联订单、目的地、日期、出行人员等所有字段数据

#### Scenario: 路由访问新建页时表单为空
- **WHEN** 用户导航到 `/itineraries/create`（`routeId` 为 null）
- **THEN** 表单 SHALL 保持空白，不触发数据加载
