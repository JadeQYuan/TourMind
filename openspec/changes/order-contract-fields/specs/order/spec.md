## MODIFIED Requirements

### Requirement: 订单新增人数字段
订单 SHALL 新增“人数”字段，支持录入、展示和查询。

#### Scenario: 新建/编辑订单录入人数
- **WHEN** 用户新建或编辑订单时
- **THEN** 可填写“人数”字段，保存后持久化到数据库

#### Scenario: 订单列表展示人数
- **WHEN** 用户在订单列表页查看订单
- **THEN** “人数”字段正确展示

#### Scenario: 支持按人数查询
- **WHEN** 用户在订单列表页按人数筛选/搜索
- **THEN** 结果仅包含匹配人数的订单
