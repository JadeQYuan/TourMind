## 1. 前端实现

- [x] 1.1 views/contract/ 新增/编辑表单增加甲乙方及联系电话字段，甲方及电话自动从订单带入
- [x] 1.2 views/contract/ 合同详情页结构化分区展示基本信息、款项、行程、补充信息
- [x] 1.3 api/contract.ts、mock/contract.ts 同步支持新字段和结构化数据
- [x] 1.4 适配移动端视图，确保 Drawer 分区展示兼容

## 2. 后端实现

- [x] 2.1 models/contract.py、schemas/contract.py 增加 party_a、party_a_phone、party_b、party_b_phone 字段
- [x] 2.2 routers/contracts.py 支持新字段的创建、编辑、查询，甲方及电话从订单接口带入
- [x] 2.3 行程明细通过订单接口获取，接口防御性校验

## 3. 测试与兼容性

- [x] 3.1 新建、编辑、查看合同全流程测试，兼容旧数据
- [x] 3.2 Mock 层补充新字段及结构化数据的测试用例
- [x] 3.3 部署上线，监控异常日志
