# 供应商和产品模型更新设计

## 一、变更概述
按照用户要求，调整供应商和产品模型，使其符合规范并保持现有业务功能。

## 二、供应商模型变更

### 1. 字段变更

| 规范字段 | 原字段 | 新字段 | 说明 |
|---------|-------|-------|------|
| contact_person | contact_person | contact_person | 保持不变 |
| contact_phone | contact_phone | contact_phone | 保持不变 |
| status | is_active (bool) | status (str) | 改为字符串，值为 "enabled" / "disabled" |
| remark | notes | remark | 字段名变更 |
| - | address | - | 删除 address 字段 |
| - | created_by | created_by | 保持不变 |

### 2. 数据库变更
- 表名：suppliers
- 字段变更：
  - 删除 address 列
  - 删除 is_active 列（或保留并迁移数据）
  - 添加 status 列，默认值 "enabled"
  - 重命名 notes 为 remark

## 三、产品模型变更

### 1. 字段变更

| 规范字段 | 原字段 | 新字段 | 说明 |
|---------|-------|-------|------|
| price | reference_price | price | 字段名变更，非可选 |
| remark | notes | remark | 字段名变更 |
| status | status (active/inactive) | status (enabled/disabled) | 枚举值变更 |
| origin | origin | origin | 保持不变 |
| destination | destination | destination | 保持不变 |
| includes | includes | includes | 保持不变 |
| excludes | excludes | excludes | 保持不变 |
| cancellation_policy | cancellation_policy | cancellation_policy | 保持不变 |
| travel_notice | travel_notice | travel_notice | 保持不变 |
| important_tips | important_tips | important_tips | 保持不变 |
| itinerary_template | itinerary_template (JSONB) | itinerary_template (JSONB) | 保持不变 |
| - | created_by | created_by | 保持不变 |
| - | product_type, tags | - | 删除这两个字段 |

### 2. 数据库变更
- 表名：products
- 字段变更：
  - 重命名 reference_price 为 price
  - 重命名 notes 为 remark
  - 调整 status 枚举值从 active/inactive 为 enabled/disabled
  - 删除 product_type 列
  - 删除 tags 列

## 四、API 变更
- 供应商 API：
  - list 参数从 is_active 改为 status
  - create/update 参数调整为新字段
- 产品 API：
  - 移除 product_type 参数
  - create/update 参数调整为新字段

## 五、前端变更
- 更新类型定义
- 更新供应商列表页面
- 产品页面同步调整（如果有）

## 六、数据迁移
- 供应商：
  - is_active=true → status="enabled"
  - is_active=false → status="disabled"
  - notes 内容迁移到 remark
- 产品：
  - status="active" → "enabled"
  - status="inactive" → "disabled"
  - reference_price → price
  - notes → remark
