## Purpose
合同详情与编辑：pending_sign 状态下的编辑功能、详情页完整字段展示、签署页显示出行提示。

## Requirements

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

### Requirement: 合同详情页展示完整字段
`ContractDetailView` SHALL 展示以下全部字段：客户姓名、联系电话、出行人数、出发日期、返回日期、合同总额、定金、尾款及到账日期、费用包含、费用不含、取消政策、出行提示、备注、关联订单号、出行人列表（当 travelers 非空时）。

#### Scenario: 详情页显示出行提示
- **WHEN** 用户打开合同详情页
- **THEN** 基本信息卡片中显示"出行提示"字段内容（非空时）

#### Scenario: 详情页显示备注
- **WHEN** 合同存在 notes 字段且非空
- **THEN** 详情页底部显示"备注"卡片

#### Scenario: 详情页显示关联订单号
- **WHEN** 用户打开合同详情页
- **THEN** 基本信息区域显示关联订单编号（order_no）

### Requirement: 签署页展示出行提示
客户签署页（`ContractSignView`）SHALL 展示 `travel_notice` 字段（当非空时），位置在"包含项目"与"退改规则"之间或之后。后端 `ContractPublicOut` SHALL 包含 `travel_notice` 字段。

#### Scenario: 客户可在签署前看到出行提示
- **WHEN** 客户打开签署链接
- **THEN** 合同内容区域显示"出行提示"字段（非空时）
