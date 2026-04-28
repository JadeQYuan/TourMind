## MODIFIED Requirements

### Requirement: 合同编辑功能（待签署状态）
`ContractFormView` SHALL 支持编辑模式（通过 `editId` prop 触发）：加载已有合同数据预填表单，保存时调用 `PUT /contracts/{id}`。编辑模式 SHALL 仅在 `pending_sign` 状态可访问。

#### Scenario: 编辑页预填数据
- **WHEN** 用户导航到 `/contracts/:id/edit`
- **THEN** 表单以该合同的现有字段（includes、excludes、travel_notice、cancellation_policy、notes）预填，订单信息以只读文本展示

#### Scenario: 编辑页保存成功
- **WHEN** 用户修改字段后点击"保存"
- **THEN** 调用 `PUT /contracts/{id}`，保存成功后 navigate 回详情页

#### Scenario: 编辑路由可访问
- **WHEN** 用户访问 `/contracts/:id/edit`
- **THEN** 系统渲染编辑表单页面，不出现 404

### Requirement: 合同表单和详情页甲乙方及联系方式同排展示（PC）
在 PC 端（breakpoint ≥ 992px），合同表单和详情页的甲方及联系方式、乙方及联系方式需同排展示，提升信息密度和可读性。移动端自动换行。

#### Scenario: PC 端同排展示
- **WHEN** 屏幕宽度 ≥ 992px
- **THEN** 甲乙方及联系方式同排展示

#### Scenario: 移动端自动换行
- **WHEN** 屏幕宽度 < 992px
- **THEN** 甲乙方及联系方式分行展示，保证表单和详情页可用性
