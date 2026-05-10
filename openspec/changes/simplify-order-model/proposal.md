## Why

当前系统存在两种订单概念（客户订单 `CustomerOrder` 和供应商订单 `Order`），导致架构复杂、命名冲突、维护成本高。根据业务需求，仅需保留客户→旅行社的订单模型，简化系统架构，消除命名混淆。

## What Changes

- **模型重构**：
  - 重命名 `CustomerOrder` → `Order`，表名从 `customer_orders` → `orders`
  - 删除原 `itinerary.py` 中的供应商订单 `Order` 及 `OrderAttachment` 模型
  - `Itinerary` 表：`customer_order_id` → `order_id`，关联到 `orders` 表
  - 调整相关外键约束、关联关系
- **Schema 清理**：删除供应商订单相关的 Pydantic Schema
- **路由精简**：删除供应商订单相关的 API 路由
- **数据库迁移**：创建 Alembic 迁移脚本处理表结构变更

**BREAKING**：供应商订单功能完全移除，相关 API 不可用；表名、类名发生变更

## Capabilities

- `order`: 保留客户订单核心功能，简化模型命名
- `itinerary`: 移除行程内供应商订单子功能

## Impact

- backend/app/models/order.py - 重命名类、表名
- backend/app/models/itinerary.py - 删除供应商订单模型
- backend/app/models/__init__.py - 更新导出
- backend/app/models/contract.py - 更新外键引用
- backend/app/models/bill.py - 更新外键引用，删除供应商订单关联
- backend/app/schemas/itinerary.py - 删除供应商订单 Schema
- backend/app/routers/orders.py - 删除供应商订单路由
- backend/app/routers/itineraries.py - 删除供应商订单子路由
- backend/alembic/versions/ - 新增迁移脚本
- 影响订单、行程、合同、账单模块
