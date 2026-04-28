## Why

行程管理与合同管理的部分 UI 文案、交互行为与实际业务用语存在偏差，影响操作一致性；同时行程明细每次新增/编辑均需手动展开，增加操作成本。

## What Changes

**行程管理**
- 对 `not_started`（未开始）状态的行程新增"撤销"操作，确认后行程状态变为 `cancelled`（已撤销）
- 行程列表中目的地字段后面不再显示行程状态标签
- 新增/编辑行程时，每日行程明细区块默认展开，无需用户手动点击展开
- 新增/编辑行程表单下方不显示提示语

**合同管理**
- 合同状态保持三个：`pending_sign`（待签署）、`signed`（已签署）、`revoked`（已撤销），确保不出现其他状态
- 合同列表新增"编辑"操作按钮（对 `pending_sign` 状态合同可用）
- 合同列表"复制链接"按钮文案改为"分享"
- 新增/编辑合同表单下方不显示提示语

## Capabilities

### New Capabilities
<!-- 无新能力引入 -->

### Modified Capabilities
- `002-biz-02-itinerary-status`: 新增未开始行程"撤销"操作（`not_started → cancelled`）
- `002-biz-02-itinerary-list`: 目的地字段后不再显示行程状态标签
- `002-biz-02-itinerary-form`: 新增/编辑时每日行程明细默认展开；表单下方无提示语
- `002-biz-03-contract-status`: 确保三状态体系（待签署/已签署/已撤销）；"复制链接"改为"分享"；新增"编辑"按钮
- `002-biz-03-contract-creation`: 新增/编辑合同表单下方不显示提示语

## Impact

- 前端：`views/itinerary/`（列表组件、表单组件）、`views/contract/`（列表组件、详情组件）
- Mock：`mock/itinerary.ts`、`mock/contract.ts`（无结构变更，仅 UI 文案）
- 后端：无变更
