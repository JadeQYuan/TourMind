## Why

合同管理模块在实际业务中，新增/编辑合同时，用户需要先选择关联订单，确保合同与订单数据一致性。同时，提升表单在 PC 端的可用性和信息展示效率。

## What Changes

- 合同新增/编辑表单，订单选择项移至最顶部，必须先选订单后填写其他信息
- PC 端甲方及联系方式、乙方及联系方式同排展示，提升信息密度和录入效率
- 表单样式和交互优化，兼容移动端

## Capabilities

### New Capabilities
- `contract-form-order-and-style`: 合同表单支持订单优先选择及甲乙方信息同排展示

### Modified Capabilities
- `002-biz-03-contract-creation`: 合同创建流程需先选订单
- `002-biz-03-contract-detail`: 合同表单和详情页样式优化，甲乙方信息同排

## Impact

- 前端：views/contract/ContractFormView.vue, ContractDetailView.vue, types/index.ts, api/contract.ts
- Mock：mock/contract.ts, mock/_data.ts
- 后端：app/routers/contracts.py, schemas/contract.py
- 相关 Specs：002-biz-03-contract-creation, 002-biz-03-contract-detail
