## Purpose
订单管理：表单字段校验、产品关联自动填充天数，以及订单状态由账单收款自动推进。

## Requirements

### Requirement: Order form product and supplier are required
订单新建或编辑表单保存时，系统 SHALL 校验 `product_id` 和 `supplier_id` 字段不为空；任一字段为空时 SHALL 阻止提交并显示错误提示。

#### Scenario: Save blocked when product is empty
- **WHEN** 用户在订单表单中未选择产品，点击"保存"
- **THEN** 系统显示错误提示"请选择产品"，不提交请求，抽屉保持打开

#### Scenario: Save blocked when supplier is empty
- **WHEN** 用户在订单表单中未选择供应商，点击"保存"
- **THEN** 系统显示错误提示"请选择供应商"，不提交请求，抽屉保持打开

#### Scenario: Form fields are visually marked as required
- **WHEN** 用户打开订单新建或编辑抽屉
- **THEN** 产品和供应商字段旁均显示必填标记（`required` 属性）

### Requirement: Order form days auto-filled from selected product
用户在订单表单中选择产品时，系统 SHALL 自动将 `form.days` 设置为所选产品的 `days` 值；用户 SHALL 可在自动填充后手动修改天数。

#### Scenario: Days auto-filled on product selection
- **WHEN** 用户在订单表单中选择某产品
- **THEN** 天数输入框的值自动变更为该产品的 `days` 字段值

#### Scenario: Days remain editable after auto-fill
- **WHEN** 天数已被自动填入
- **THEN** 用户仍可直接修改天数输入框的值

#### Scenario: No auto-fill when product is cleared
- **WHEN** 用户清除产品选择（allow-clear）
- **THEN** 天数字段值不变，保持用户最后输入或已有的值

### Requirement: No manual status change button on orders
订单列表操作栏 SHALL NOT 包含"变更状态"按钮；订单状态 SHALL 由系统根据收款自动推进。

#### Scenario: Change status button absent
- **WHEN** 用户查看订单列表
- **THEN** 每行操作栏只显示"编辑"按钮（已完成订单为禁用状态），不显示"变更状态"下拉

### Requirement: Completed orders cannot be edited
状态为 `completed`（已完成）的订单，其编辑按钮 SHALL 处于禁用状态，点击无效。

#### Scenario: Edit button disabled for completed order
- **WHEN** 用户查看订单列表，某行订单状态为"已完成"
- **THEN** 该行"编辑"按钮显示为禁用（`disabled`）

#### Scenario: Edit button enabled for non-completed order
- **WHEN** 订单状态为"待下定"或"待付款"
- **THEN** 该行"编辑"按钮可正常点击

### Requirement: Income bill auto-advances linked order status
收入类账单（`bill_type === 'income'`）关联了订单并保存成功后，系统 SHALL 根据以下规则自动推进订单状态：
- 若订单当前状态为 `pending_deposit`，SHALL 自动变更为 `pending_payment`
- 若订单当前状态为 `pending_payment` 且该订单的累计收入账单总额 ≥ 订单价格，SHALL 自动变更为 `completed`

#### Scenario: First income bill changes status to pending_payment
- **WHEN** 用户录入一笔收入账单并关联状态为"待下定"的订单，保存成功
- **THEN** 该订单状态自动变更为"待付款"

#### Scenario: Full payment received changes status to completed
- **WHEN** 用户录入一笔收入账单关联状态为"待付款"的订单，保存成功，且该订单累计收入账单总额 ≥ 订单价格
- **THEN** 该订单状态自动变更为"已完成"

#### Scenario: Partial payment does not complete order
- **WHEN** 用户录入一笔收入账单关联状态为"待付款"的订单，保存成功，但累计收入总额 < 订单价格
- **THEN** 订单状态保持"待付款"，不自动变更
