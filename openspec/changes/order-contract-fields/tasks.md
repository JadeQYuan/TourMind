## 1. 订单模块

- [x] 1.1 backend/app/models/order.py 新增“人数”字段，生成 Alembic 迁移脚本（已存在，脚本跳过）
	- [x] 1.2 backend/app/schemas/order.py、routers/order.py 支持人数字段的录入、展示、查询（已支持）
	- [x] 1.3 frontend/src/views/order/OrderListView.vue、api/order.ts、types/ 新增/展示/查询人数字段（已支持）
	- [x] 1.4 mock/order.ts 补充人数字段（已支持）

## 2. 合同模块

	- [x] 2.1 frontend/src/views/contract/ContractForm.vue 新建/编辑时自动带入订单出行日期、天数、人数、定金、定金到账日期、尾款及到账日期，字段只读（已支持）
	- [x] 2.2 backend/app/models/contract.py、schemas/contract.py、routers/contract.py 支持合同只读展示订单关键信息（已支持）
	- [x] 2.3 mock/contract.ts 补充相关字段（已支持）

## 3. 合同列表字段结构调整

	- [x] 3.1 frontend/src/views/contract/ContractListView.vue、api/contract.ts、types/ 增加甲方、联系方式、乙方、订单编号字段，去掉客户列（已支持）
	- [x] 3.2 backend/app/models/contract.py、schemas/contract.py、routers/contract.py 同步调整合同列表字段（已支持）
	- [x] 3.3 mock/contract.ts、合同导出逻辑同步字段变更（已支持）

## 4. 测试与文档

	- [x] 4.1 补充/更新前后端测试用例，覆盖新增/变更字段（已覆盖）
	- [x] 4.2 更新相关开发文档，说明字段变更及兼容性处理（已完成）
