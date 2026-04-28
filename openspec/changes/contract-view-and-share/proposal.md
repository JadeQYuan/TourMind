## Why

当前合同管理功能存在信息录入不全、查看内容分散的问题，影响业务流转效率和合同合规性。随着业务量增长，需提升合同录入与查看的完整性和便捷性。

## What Changes

- 新增/编辑合同时，支持录入甲方、联系电话，乙方、联系电话，甲方及联系电话默认从订单带入并可编辑
- 合同查看页内容结构化，分为：
  - 基本信息（甲乙方、联系电话、出行日期、人数、天数等）
  - 款项信息（订单金额及大写金额）
  - 行程明细（自动关联订单行程）
  - 补充信息（新增时填写的其它字段）
- 合同数据结构、API、前端表单与详情视图同步调整

## Capabilities

### New Capabilities
- contract-party-fields: 合同新增甲乙方及联系电话字段，支持从订单带入与编辑
- contract-view-structure: 合同查看页内容结构化展示，分区显示基本信息、款项、行程、补充信息

### Modified Capabilities
- 002-biz-03-contract-creation: 合同创建流程需支持甲乙方及联系电话字段的自动带入与编辑
- 002-biz-03-contract-detail: 合同详情页需按新结构展示内容，支持分区与字段扩展

## Impact

- 涉及前端 views/contract/、api/contract.ts、mock/contract.ts
- 涉及后端 models/contract.py、schemas/contract.py、routers/contracts.py
- 影响合同相关 API、订单-合同数据流、行程数据获取