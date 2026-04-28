## MODIFIED Requirements

### Requirement: 合同列表操作包含分享和编辑
对于 `pending_sign` 状态的合同，列表页 SHALL 显示"分享"和"编辑"两个操作按钮。`revoked` 和 `signed` 状态无签署/编辑操作。

#### Scenario: 待签署合同显示"查看"、"分享"和"编辑"
- **WHEN** 合同列表中包含一条 `pending_sign` 合同
- **THEN** 操作列显示"查看"、"分享"和"编辑"三个按钮

#### Scenario: 已签署或已撤销合同无分享/编辑操作
- **WHEN** 合同状态为 `signed` 或 `revoked`
- **THEN** 操作列不显示"分享"和"编辑"按钮

#### Scenario: 点击"分享"复制签署链接
- **WHEN** 用户点击 `pending_sign` 合同的"分享"按钮
- **THEN** 系统将 `{origin}/sign/{share_token}` 写入剪贴板，提示"签署链接已复制"

### Requirement: 状态标签全中文显示
所有合同视图中展示状态时，系统 SHALL 显示中文标签。`ContractListView` 的 `STATUS_LABEL` 和 `STATUS_COLOR` SHALL 只包含 3 个状态的映射：`pending_sign`、`signed`、`revoked`。

| 状态 key      | 中文标签 | 颜色 token |
|--------------|---------|-----------|
| pending_sign | 待签署   | orange    |
| signed       | 已签署   | success   |
| revoked      | 已撤销   | error     |

#### Scenario: 列表页状态标签为中文
- **WHEN** 合同列表渲染每行的状态列
- **THEN** 显示对应中文标签，不显示英文 key

#### Scenario: 筛选器选项为中文（3个）
- **WHEN** 用户在列表页打开状态筛选下拉
- **THEN** 选项仅包含「待签署」「已签署」「已撤销」3 个选项，不出现「进行中」「已完成」「已取消」

#### Scenario: 已撤销合同在列表显示中文状态
- **WHEN** 列表包含 `status = "revoked"` 的合同
- **THEN** 该行状态标签显示「已撤销」且标签颜色为 error（红色）
