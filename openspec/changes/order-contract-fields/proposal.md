## Why

当前订单和合同管理模块存在字段不全、信息传递不便的问题，影响业务流转效率和数据一致性。随着业务需求升级，需要补充订单人数字段，并在合同新建/编辑时自动带入订单关键信息，减少手工录入和出错风险，提升用户体验。

## What Changes

- 订单管理：订单表新增“人数”字段，支持录入和展示
- 合同管理：新建/编辑合同时，自动从关联订单带入出行日期、天数、人数、定金、定金到账日期、尾款及到账日期，仅做展示不可编辑
- 合同列表：增加甲方、联系方式、乙方、订单编号字段，去掉客户列
- **BREAKING**：合同列表字段结构调整，部分字段只读

## Capabilities

### New Capabilities


## Capabilities

- `contract-list`: 合同列表字段结构调整，增加甲方、联系方式、乙方、订单编号，去掉客户列
- `order`: 新增人数字段，支持录入、展示、查询
- `contract`: 新建/编辑时自动带入订单关键信息，仅展示不可编辑，列表字段结构调整（增加甲方、联系方式、乙方、订单编号，去掉客户列）

## Impact

- backend/app/models/order.py, schemas/order.py, routers/order.py
- backend/app/models/contract.py, schemas/contract.py, routers/contract.py
- frontend/src/views/order/OrderListView.vue, api/order.ts
- frontend/src/views/contract/ContractListView.vue, api/contract.ts
- 相关数据库迁移脚本、前端类型定义、Mock 数据
- 影响订单、合同相关业务流程和页面
