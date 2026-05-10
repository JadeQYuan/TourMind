## 1. 模型层重构

- [ ] 1.1 backend/app/models/order.py：重命名 `CustomerOrder` → `Order`，`__tablename__` 从 "customer_orders" → "orders"，更新注释
- [ ] 1.2 backend/app/models/itinerary.py：删除 `Order`、`OrderAttachment` 类，删除 `Itinerary.orders` 关联关系；`customer_order_id` → `order_id`，外键引用从 "customer_orders.id" → "orders.id"，UniqueConstraint 同步更新
- [ ] 1.3 backend/app/models/__init__.py：更新导出，删除 `Order`、`OrderAttachment`，添加 `Order`（原 CustomerOrder）
- [ ] 1.4 backend/app/models/contract.py：`customer_order_id` → `order_id`，外键引用从 "customer_orders.id" → "orders.id"
- [ ] 1.5 backend/app/models/bill.py：`customer_order_id` → `order_id`，外键引用从 "customer_orders.id" → "orders.id"；删除原供应商订单关联的 `order_id` 字段及其外键

## 2. Schema 层清理

- [ ] 2.1 backend/app/schemas/itinerary.py：删除供应商订单相关 Schema（`OrderCreate`、`OrderUpdate`、`OrderOut`、`OrderAttachmentOut`、`OrderListOut`），从 `ItineraryOut` 中移除 `orders` 字段；`customer_order_id` → `order_id`
- [ ] 2.2 backend/app/schemas/contract.py：`customer_order_id` → `order_id`
- [ ] 2.3 backend/app/schemas/bill.py：`customer_order_id` → `order_id`

## 3. 路由层精简

- [ ] 3.1 backend/app/routers/orders.py：删除供应商订单相关路由（226 行之后的部分），更新导入从 `CustomerOrder` → `Order`
- [ ] 3.2 backend/app/routers/itineraries.py：删除供应商订单子路由（220-266 行），更新导入，移除 `_LOAD_FULL` 中的订单加载；`customer_order_id` → `order_id`
- [ ] 3.3 backend/app/routers/contracts.py：更新导入从 `CustomerOrder` → `Order`；`customer_order_id` → `order_id`
- [ ] 3.4 backend/app/routers/dashboard.py：更新导入从 `CustomerOrder` → `Order`

## 4. 数据库迁移

- [ ] 4.1 生成 Alembic 迁移脚本：重命名表、更新字段名、删除旧表和字段
- [ ] 4.2 执行迁移脚本验证

## 5. 验证测试

- [ ] 5.1 启动后端服务，验证 API 正常
- [ ] 5.2 检查数据库表结构正确
