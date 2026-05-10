# 供应商和产品模型更新任务列表

## 后端任务

### 1. 供应商模型更新
- [x] 更新 app/models/supplier.py 模型
- [x] 更新 app/schemas/supplier.py 验证模型
- [x] 更新 app/routers/suppliers.py 路由逻辑

### 2. 产品模型更新
- [x] 更新 app/models/product.py 模型
- [x] 更新 app/schemas/product.py 验证模型
- [x] 更新 app/routers/products.py 路由逻辑

## 前端任务

### 3. 类型定义更新
- [x] 更新 src/types/index.ts 中的 Supplier 和 Product 接口

### 4. 供应商页面更新
- [x] 更新 src/views/supplier/SupplierListView.vue 页面

### 5. 产品页面更新
- [x] 更新 src/views/product/ProductListView.vue 页面

## 数据库任务

### 6. 数据迁移（待创建）
- [ ] 创建 Alembic 迁移脚本
- [ ] 执行数据迁移
  - 供应商数据迁移
  - 产品数据迁移

## 测试任务

### 7. 验证功能
- [ ] 测试供应商 CRUD
- [ ] 测试产品 CRUD
