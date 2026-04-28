## 1. 前端实现

- [x] 1.1 `views/contract/ContractFormView.vue`：将订单选择项移至表单最顶部，未选订单时其他字段禁用
- [x] 1.2 `views/contract/ContractFormView.vue`：订单选择后自动填充甲乙方及联系方式
- [x] 1.3 `views/contract/ContractFormView.vue`：PC 端甲乙方及联系方式同排展示，移动端自动换行
- [x] 1.4 `views/contract/ContractDetailView.vue`：PC 端甲乙方及联系方式同排展示，移动端自动换行
- [x] 1.5 `types/index.ts`：ContractCreate/Update 类型调整，确保订单 id、甲乙方信息必填
- [x] 1.6 `api/contract.ts`：API 参数顺序、类型校验同步调整

## 2. Mock 层支持

- [x] 2.1 `mock/contract.ts`、`mock/_data.ts`：Mock 新建/编辑接口参数校验，未传订单 id 返回错误
- [x] 2.2 `mock/_data.ts`：Mock 数据结构补充甲乙方及联系方式字段

## 3. 后端实现

- [x] 3.1 `app/routers/contracts.py`：接口参数顺序、schema 校验同步调整，未传订单 id 返回 422
- [x] 3.2 `schemas/contract.py`：ContractCreate/Update schema 校验订单 id、甲乙方信息必填

## 4. 兼容性与测试

- [x] 4.1 前端表单在 PC/移动端响应式测试，确保同排/换行逻辑无误
- [x] 4.2 Mock 层防御性测试，未传订单 id 场景
- [x] 4.3 后端接口未传订单 id 返回 422 测试
