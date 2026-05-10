## Context

当前系统存在两种订单模型：
- `CustomerOrder`（客户→旅行社订单，表 `customer_orders`）
- `Order`（旅行社→供应商订单，表 `orders`，关联行程）

导致命名冲突、架构复杂。根据业务需求，仅需保留客户→旅行社订单。

## Goals / Non-Goals

**Goals:**
- 简化订单模型，统一命名为 `Order`，表名为 `orders`
- 完全删除供应商订单相关模型、Schema、路由
- 更新所有外键引用、关联关系
- 提供数据库迁移方案

**Non-Goals:**
- 不保留供应商订单功能
- 不涉及前端页面修改（假设前端未使用供应商订单功能）

## Decisions

- **模型重命名**：`CustomerOrder` → `Order`，表名 `customer_orders` → `orders`
- **删除内容**：
  - `itinerary.py` 中的 `Order`、`OrderAttachment` 模型
  - `itinerary.py` 中 `Itinerary.orders` 关联关系
  - `schemas/itinerary.py` 中的供应商订单相关 Schema
  - `routers/orders.py` 中的供应商订单路由
  - `routers/itineraries.py` 中的供应商订单子路由
  - `bill.py` 中的 `order_id` 外键字段（原供应商订单关联）
- **外键更新**：
  - `contracts.customer_order_id` → `contracts.order_id`，引用 `orders.id`
  - `bills.customer_order_id` → `bills.order_id`，引用 `orders.id`
  - `itineraries.customer_order_id` → `itineraries.order_id`，引用 `orders.id`
- **数据库迁移**：采用 Alembic，先重命名表，再更新字段名，最后删除旧表

## Risks / Trade-offs

- [风险] 旧数据依赖供应商订单 → [缓解] 确认业务不再需要后再执行
- [风险] 外键约束处理顺序 → [缓解] 迁移脚本按正确顺序执行

## Migration Plan

1. 备份数据库
2. 更新后端模型文件
3. 生成 Alembic 迁移脚本
4. 执行迁移脚本
5. 更新路由、Schema 文件
6. 验证功能正常

## Open Questions

- 前端是否使用了供应商订单相关 API？（默认假设没有）
