## Purpose
合同创建：仅显示未关联合同的订单、行程存在性二次确认、产品字段自动预填、travel_notice 字段支持。

## Requirements

### Requirement: 新建合同仅显示未关联合同的订单
合同新建表单的订单下拉 SHALL 仅列出尚未创建合同的订单。已有关联合同的订单 SHALL 被排除在选项之外。

#### Scenario: 已有合同的订单不出现在下拉中
- **WHEN** 用户打开新建合同表单
- **THEN** 订单下拉中不包含已存在合同记录的订单

#### Scenario: 没有未关联订单时下拉为空
- **WHEN** 所有订单均已关联合同
- **THEN** 订单下拉显示空状态，提示"暂无可创建合同的订单"

### Requirement: 选中订单后检查行程存在性
选中订单后，系统 SHALL 查询该订单关联的行程；若无行程，SHALL 弹出二次确认 Modal。

#### Scenario: 有关联行程时直接继续
- **WHEN** 用户从下拉选中一个有关联行程的订单
- **THEN** 不弹出任何提示，表单可继续编辑

#### Scenario: 无关联行程时弹出二次确认
- **WHEN** 用户从下拉选中一个没有关联行程的订单
- **THEN** 弹出 Modal 提示"该订单尚未创建行程，是否继续创建合同？"，提供"继续"和"取消"按钮

#### Scenario: 用户取消确认后重置选择
- **WHEN** 无行程确认 Modal 中用户点击"取消"
- **THEN** 订单选择被清空，表单回到初始状态

### Requirement: 从产品预填费用条款字段
若所选订单关联了产品（`product_id` 非空），系统 SHALL 自动将产品的 `includes`、`excludes`、`travel_notice`、`cancellation_policy` 四个字段预填入合同表单，且对应表单域可编辑。

#### Scenario: 产品字段自动预填
- **WHEN** 用户选中一个关联产品的订单
- **THEN** 表单中"费用包含"、"费用不含"、"出行提示"、"取消政策"四个文本域被自动填入产品对应字段的内容

#### Scenario: 无产品时无预填
- **WHEN** 选中的订单 product_id 为 null
- **THEN** 上述四个文本域保持空白，用户可手动输入

#### Scenario: 预填内容可被用户手动修改
- **WHEN** 产品字段已预填后，用户修改某个文本域
- **THEN** 修改值被保留，不因其他操作被重置（切换订单除外）

### Requirement: 合同支持存储出行提示字段
合同数据模型 SHALL 包含独立的 `travel_notice`（出行提示）文本字段，可为空。

#### Scenario: 创建合同时传入 travel_notice
- **WHEN** `POST /contracts` 请求体包含 `travel_notice` 字段
- **THEN** 创建的合同记录中 `travel_notice` 存储该值

#### Scenario: travel_notice 为可选字段
- **WHEN** `POST /contracts` 请求体不包含 `travel_notice`
- **THEN** 创建成功，合同 `travel_notice` 为 null
