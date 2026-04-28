## ADDED Requirements

### Requirement: Days detail section is expanded by default
行程新建/编辑表单中，每日行程明细区块 SHALL 默认处于展开状态，用户打开表单即可直接编辑各天明细，无需手动点击展开。

#### Scenario: New form opens with days detail expanded
- **WHEN** 用户打开新建行程表单
- **THEN** 每日行程明细区块处于展开状态，所有天数条目均可见，可直接编辑

#### Scenario: Edit form opens with days detail expanded
- **WHEN** 用户打开已有行程的编辑表单
- **THEN** 每日行程明细区块处于展开状态，已有天数条目全部可见，无需额外点击

### Requirement: Itinerary form has no hint text at bottom
行程新建/编辑表单 SHALL NOT 在表单底部显示任何静态提示语、说明文字或 `<a-alert>` 等信息组件。

#### Scenario: New itinerary form has no bottom hint
- **WHEN** 用户打开新建行程表单
- **THEN** 表单底部不显示任何提示语或说明性文字

#### Scenario: Edit itinerary form has no bottom hint
- **WHEN** 用户打开编辑行程表单
- **THEN** 表单底部不显示任何提示语或说明性文字
