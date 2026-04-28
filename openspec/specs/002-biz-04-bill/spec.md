## Purpose
账单管理：支出账单关联订单与供应商自动填充，收入账单触发订单状态推进，支出账单不触发推进。

## Requirements

### Requirement: 支出账单可关联订单
账单表单处于支出类型时，SHALL 显示"关联订单"选择器，供用户选择关联的业务订单。

#### Scenario: 支出账单显示关联订单选择器
- **WHEN** 用户在账单表单中选择"支出"类型
- **THEN** 表单中 SHALL 显示"关联订单"选择器

#### Scenario: 支出账单可选择订单
- **WHEN** 用户在支出表单中点击"关联订单"选择器
- **THEN** 下拉列表 SHALL 显示所有非已完成订单，格式为"订单号 · 客户姓名"

#### Scenario: 支出账单未选择订单时可正常保存
- **WHEN** 用户未选择关联订单直接保存支出账单
- **THEN** 系统 SHALL 正常保存，`customer_order_id` 为空

### Requirement: 支出账单选择订单后自动填充供应商
当用户为支出账单选择关联订单时，系统 SHALL 自动将该订单对应的供应商填入"供应商"字段。

#### Scenario: 选择订单后供应商自动填充
- **WHEN** 用户在支出账单表单中选择一个关联订单
- **THEN** "供应商"字段 SHALL 自动设置为该订单的供应商

#### Scenario: 清除订单后供应商清空
- **WHEN** 用户清空"关联订单"字段
- **THEN** "供应商"字段 SHALL 同步清空

#### Scenario: 切换账单类型时关联订单清空
- **WHEN** 用户从"支出"切换到"收入"或反向切换
- **THEN** "关联订单"和"供应商"字段 SHALL 同步清空，避免脏数据

### Requirement: 收入账单关联订单仅触发状态推进
账单保存后，SHALL 仅在 `bill_type === 'income'` 且有 `customer_order_id` 时调用 `checkAndAdvanceOrderStatus`；支出账单保存不触发订单状态推进逻辑。

#### Scenario: 支出账单保存不推进订单状态
- **WHEN** 用户保存一笔支出账单（`bill_type === 'expense'`），即使关联了订单
- **THEN** 系统 SHALL 不调用 `checkAndAdvanceOrderStatus`，订单状态保持不变
